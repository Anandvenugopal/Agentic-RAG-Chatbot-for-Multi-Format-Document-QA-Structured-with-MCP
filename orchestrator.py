# orchestrator.py
import os
import json
import time

from ingestion_agent import IngestionAgent
from retrieval_agent import RetrievalAgent
from llm_response_agent import LLMResponseAgent
from mcp import create_mcp_message

class Orchestrator:
    def __init__(self):
        """
        Initializes the entire agentic system.
        This is where we instantiate our agents, loading models and connections
        only once for efficiency.
        """
        print("[Orchestrator] Initializing the RAG system...")
        self.ingestion_agent = IngestionAgent()
        self.retrieval_agent = RetrievalAgent()
        self.llm_agent = LLMResponseAgent()
        print("[Orchestrator] All agents initialized.")

    def ingest_document(self, file_path: str):
        """
        Orchestrates the ingestion pipeline:
        1. IngestionAgent: Parses and chunks the document.
        2. RetrievalAgent: Embeds and stores the chunks.
        """
        print(f"\n[Orchestrator] --- Starting Ingestion Pipeline for: {os.path.basename(file_path)} ---")
        
        # 1. Pass the file to the IngestionAgent
        print("[Orchestrator] -> Calling IngestionAgent to parse and chunk...")
        mcp_from_ingestion = self.ingestion_agent.parse_and_chunk_document(file_path)

        # Error handling
        if mcp_from_ingestion['type'] == 'INGESTION_ERROR':
            print(f"[Orchestrator] Ingestion failed: {mcp_from_ingestion['payload']['error']}")
            return mcp_from_ingestion

        # 2. Pass the chunks to the RetrievalAgent
        print("[Orchestrator] Chunks received. -> Calling RetrievalAgent to embed and store...")
        mcp_from_retrieval = self.retrieval_agent.embed_and_store(mcp_from_ingestion)
        
        print("[Orchestrator] --- Ingestion Pipeline Complete ---")
        return mcp_from_retrieval

    def ask_question(self, query: str):
        """
        Orchestrates the question-answering pipeline:
        1. RetrievalAgent: Retrieves relevant context for the query.
        2. LLMResponseAgent: Generates an answer based on the context.
        """
        print(f"\n[Orchestrator] --- Starting Query Pipeline for: '{query}' ---")
        
        # 1. Create an MCP request for the RetrievalAgent
        mcp_retrieve_request = create_mcp_message(
            "Orchestrator", "RetrievalAgent", "RETRIEVE_REQUEST", {"query": query, "top_k": 5}
        )
        
        # 2. Call the RetrievalAgent to get context
        print("[Orchestrator] -> Calling RetrievalAgent to retrieve context...")
        mcp_from_retrieval = self.retrieval_agent.retrieve_context(mcp_retrieve_request)

        # Error handling
        if mcp_from_retrieval['type'] == 'CONTEXT_ERROR':
            print(f"[Orchestrator] Context retrieval failed: {mcp_from_retrieval['payload']['error']}")
            return mcp_from_retrieval
            
        # 3. Pass the context to the LLMResponseAgent
        print("[Orchestrator] Context received. -> Calling LLMResponseAgent to generate answer...")
        final_response_mcp = self.llm_agent.generate_response(mcp_from_retrieval)
        
        print("[Orchestrator] --- Query Pipeline Complete ---")
        return final_response_mcp

# --- Let's test the full end-to-end pipeline ---
if __name__ == "__main__":
    # This test simulates the entire process from document upload to getting an answer
    orchestrator = Orchestrator()
    
    # Optional: Clear the index for a clean test run
    print("\n[Test Runner] Clearing Pinecone index for a fresh start...")
    orchestrator.retrieval_agent.index.delete(delete_all=True)
    
    # 1. Create a dummy document to ingest
    test_file_path = "test_data.txt"
    document_content = """
    RAG-Man is a new superhero. His real name is Reginald "Reggie" Augment.
    His primary power is 'Contextual Recall', allowing him to remember text from any document he has read.
    Reggie's suit is powered by a Pinecone-core and uses Groq-chips for rapid thought processing.
    His main weakness is ambiguity and questions without context. He operates out of a library.
    """
    with open(test_file_path, "w") as f:
        f.write(document_content)

    # 2. Run the ingestion pipeline
    ingestion_result = orchestrator.ingest_document(test_file_path)
    print("\n[Test Runner] Ingestion Result:", json.dumps(ingestion_result, indent=2))
    
    # 3. Wait for Pinecone to index (using our robust waiting loop)
    print("\n[Test Runner] Waiting for indexing...")
    time.sleep(10) # Initial sleep, then poll
    while True:
        stats = orchestrator.retrieval_agent.index.describe_index_stats()
        if stats.get('total_vector_count', 0) > 0:
            print(f"[Test Runner] Indexing complete! Vector count: {stats['total_vector_count']}")
            break
        print("[Test Runner] Waiting for vectors to appear in index...")
        time.sleep(5)
        
    # 4. Run the query pipeline with a relevant question
    question_1 = "What is RAG-Man's real name and what are his powers?"
    answer_1_mcp = orchestrator.ask_question(question_1)
    
    print("\n" + "="*50)
    print(f"[Test Runner] Final Answer for: '{question_1}'")
    print(json.dumps(answer_1_mcp['payload'], indent=2))
    print("="*50 + "\n")

    # 5. Run the query pipeline with an irrelevant question
    question_2 = "What is the price of milk?"
    answer_2_mcp = orchestrator.ask_question(question_2)
    
    print("\n" + "="*50)
    print(f"[Test Runner] Final Answer for: '{question_2}'")
    print(json.dumps(answer_2_mcp['payload'], indent=2))
    print("="*50 + "\n")
    
    # 6. Clean up the dummy file
    os.remove(test_file_path)