
import os
from dotenv import load_dotenv

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq

from mcp import create_mcp_message

# --- Agent Configuration ---
# Using a fast and capable model from Groq
LLM_MODEL = "llama3-8b-8192" 

class LLMResponseAgent:
    def __init__(self, agent_name="LLMResponseAgent"):
        self.name = agent_name
        print(f"[{self.name}] Initializing...")
        
        load_dotenv()
        if not os.getenv("GROQ_API_KEY"):
            raise ValueError("GROQ_API_KEY is not set in the .env file.")

        # The RAG prompt template is crucial for instructing the LLM
        # It tells the model to answer based *only* on the provided context.
        prompt_template = """
        You are an expert Question-Answering assistant.
        Your goal is to provide accurate and concise answers based strictly on the provided context.
        
        CONTEXT:
        {context}
        
        QUESTION:
        {question}
        
        INSTRUCTIONS:
        1. Read the CONTEXT carefully.
        2. Answer the QUESTION based *only* on the information in the CONTEXT.
        3. If the context does not contain the answer, state clearly: "The provided documents do not contain information on this topic."
        4. Do not use any external knowledge or make up information.
        """
        
        # Initialize the LangChain components
        prompt = ChatPromptTemplate.from_template(prompt_template)
        
        llm = ChatGroq(
            model=LLM_MODEL,
            temperature=0, # Low temperature for factual, less creative answers
        )
        
        # Define the chain of operations: Prompt -> LLM -> String Output
        self.rag_chain = prompt | llm | StrOutputParser()
        
        print(f"[{self.name}] Initialized with model {LLM_MODEL}.")

    def generate_response(self, mcp_message):
        """Receives context and a query, then generates a final answer."""
        payload = mcp_message.get('payload', {})
        query = payload.get('query')
        context_chunks = payload.get('top_chunks', [])

        if not query:
            return create_mcp_message(self.name, "Orchestrator", "RESPONSE_ERROR", {"error": "No query received."})

        # If the retrieval agent found no relevant context, respond accordingly without calling the LLM.
        if not context_chunks:
            print(f"[{self.name}] No context provided. Replying directly.")
            no_context_answer = "The provided documents do not contain information on this topic."
            return create_mcp_message(
                self.name, "Orchestrator", "FINAL_RESPONSE",
                {"answer": no_context_answer, "source_context": []}
            )

        print(f"[{self.name}] Generating response for query: '{query}'")
        
        # Format the context chunks into a single string for the prompt
        formatted_context = "\n\n---\n\n".join([chunk['text'] for chunk in context_chunks])
        
        # Invoke the RAG chain with the context and question
        try:
            final_answer = self.rag_chain.invoke({
                "context": formatted_context,
                "question": query
            })
        except Exception as e:
            print(f"[{self.name}] Error during LLM invocation: {e}")
            return create_mcp_message(self.name, "Orchestrator", "RESPONSE_ERROR", {"error": str(e)})

        print(f"[{self.name}] Successfully generated answer.")
        
        # Return the final, structured response, including the source context for transparency.
        return create_mcp_message(
            self.name, "Orchestrator", "FINAL_RESPONSE",
            {"answer": final_answer, "source_context": context_chunks}
        )

# --- Let's test this step in isolation ---
if __name__ == "__main__":
    import json
    
    # 1. Initialize the agent
    llm_agent = LLMResponseAgent()

    # 2. Simulate a "successful retrieval" message from RetrievalAgent
    print("\n--- Testing with valid context ---")
    fake_retrieval_mcp = {
        "sender": "RetrievalAgent",
        "receiver": "LLMResponseAgent",
        "type": "CONTEXT_RESPONSE",
        "payload": {
            "query": "What is the purpose of Groq's LPU?",
            "top_chunks": [
                "The LPU (Language Processing Unit) from Groq is designed for sequential processing tasks, making it very fast for language models.",
                "Unlike GPUs which are for parallel tasks, the LPU excels at inference speed for LLMs.",
                "Groq is a company that builds custom chips for high-speed AI inference."
            ]
        }
    }
    
    final_response = llm_agent.generate_response(fake_retrieval_mcp)
    print("Final Response (MCP Format):\n", json.dumps(final_response, indent=2))
    print("\n----------------------------------\n")
    print("Just the Answer:\n", final_response['payload']['answer'])


    # 3. Simulate a "no context found" message from RetrievalAgent
    print("\n\n--- Testing with no context ---")
    fake_no_context_mcp = {
        "sender": "RetrievalAgent",
        "receiver": "LLMResponseAgent",
        "type": "CONTEXT_RESPONSE",
        "payload": {
            "query": "What is the capital of Mars?",
            "top_chunks": [] # Empty list!
        }
    }
    
    no_context_response = llm_agent.generate_response(fake_no_context_mcp)
    print("No-Context Response (MCP Format):\n", json.dumps(no_context_response, indent=2))
    print("\n----------------------------------\n")
    print("Just the Answer:\n", no_context_response['payload']['answer'])