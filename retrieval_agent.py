# retrieval_agent.py
import os
import time
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer

from mcp import create_mcp_message

# --- Agent Configuration ---
PINECONE_INDEX_NAME = "rag"
EMBEDDING_MODEL = 'all-MiniLM-L6-v2' # 384 dimensions

class RetrievalAgent:
    def __init__(self, agent_name="RetrievalAgent"):
        self.name = agent_name
        print(f"[{self.name}] Initializing...")
        
        # Load environment variables
        load_dotenv()
        pinecone_api_key = os.getenv("PINECONE_API_KEY")
        if not pinecone_api_key:
            raise ValueError("PINECONE_API_KEY is not set in the .env file.")

        # 1. Initialize Embedding Model (do this once for efficiency)
        print(f"[{self.name}] Loading embedding model: {EMBEDDING_MODEL}")
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL, device='cpu') # Use 'cuda' if GPU is available
        self.embedding_dimension = self.embedding_model.get_sentence_embedding_dimension()
        print(f"[{self.name}] Embedding model loaded. Dimension: {self.embedding_dimension}")
        
        # 2. Initialize Pinecone connection
        print(f"[{self.name}] Initializing Pinecone...")
        self.pc = Pinecone(api_key=pinecone_api_key)
        self._ensure_pinecone_index()
        self.index = self.pc.Index(PINECONE_INDEX_NAME)
        print(f"[{self.name}] Pinecone initialized. Index stats: {self.index.describe_index_stats()}")

    def _ensure_pinecone_index(self):
        """Checks if the Pinecone index exists, and if not, creates it."""
        if PINECONE_INDEX_NAME not in self.pc.list_indexes().names():
            print(f"[{self.name}] Index '{PINECONE_INDEX_NAME}' not found. Creating new index...")
            try:
                self.pc.create_index(
                    name=PINECONE_INDEX_NAME,
                    dimension=self.embedding_dimension,
                    metric='cosine',
                    spec=ServerlessSpec(
                        cloud='aws', 
                        region='us-east-1'
                    )
                )
                print(f"[{self.name}] Index created successfully. Waiting for initialization...")
                time.sleep(10) # Wait a bit for the index to be ready
            except Exception as e:
                print(f"[{self.name}] Error creating index: {e}")
                raise
        else:
            print(f"[{self.name}] Found existing index '{PINECONE_INDEX_NAME}'.")

    def embed_and_store(self, mcp_message):
        """Receives chunks from IngestionAgent, creates embeddings, and stores them."""
        payload = mcp_message.get('payload', {})
        chunks = payload.get('chunks')
        source_file = payload.get('source_file', 'unknown_source')

        if not chunks:
            return create_mcp_message(self.name, "Orchestrator", "STORAGE_ERROR", {"error": "No chunks received."})

        print(f"[{self.name}] Received {len(chunks)} chunks from '{source_file}'. Creating embeddings...")
        
        # Create embeddings for all chunks in a single, efficient batch operation
        embeddings = self.embedding_model.encode(chunks, show_progress_bar=True)

        # Prepare vectors for Pinecone upsert
        vectors_to_upsert = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            vector_id = f"{source_file}-{i}"
            metadata = {"text": chunk, "source": source_file}
            vectors_to_upsert.append((vector_id, embedding.tolist(), metadata))
        
        print(f"[{self.name}] Upserting {len(vectors_to_upsert)} vectors to Pinecone...")
        
        # Upsert in batches for performance and to stay within limits
        batch_size = 100
        for i in range(0, len(vectors_to_upsert), batch_size):
            batch = vectors_to_upsert[i:i + batch_size]
            self.index.upsert(vectors=batch)

        print(f"[{self.name}] Upsert complete.")
        return create_mcp_message(
            self.name, "Orchestrator", "STORAGE_SUCCESS", 
            {"message": f"Successfully stored {len(vectors_to_upsert)} chunks from {source_file}."}
        )

    def retrieve_context(self, mcp_message):
        """Receives a query, embeds it, and retrieves relevant context from Pinecone."""
        payload = mcp_message.get('payload', {})
        query = payload.get('query')
        top_k = payload.get('top_k', 5) # Default to retrieving top 5 chunks

        if not query:
            return create_mcp_message(self.name, "LLMResponseAgent", "CONTEXT_ERROR", {"error": "No query received."})

        print(f"[{self.name}] Received query: '{query}'. Retrieving context...")
        
        # 1. Embed the user's query
        query_embedding = self.embedding_model.encode(query).tolist()
        
        # 2. Query Pinecone
        query_result = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )

        # 3. Extract the text from the results
        context_chunks = [match['metadata'] for match in query_result['matches']]
        
        print(f"[{self.name}] Retrieved {len(context_chunks)} context chunks.")
        
        return create_mcp_message(
            self.name, "LLMResponseAgent", "CONTEXT_RESPONSE",
            {"query": query, "top_chunks": context_chunks}
        )

# --- Let's test this step in isolation ---

if __name__ == "__main__":
    import json
    
    # 1. Initialize the agent
    retrieval_agent = RetrievalAgent()
    
    # Clear the index to ensure a clean test run
    print("\n--- Clearing index for a fresh start ---")
    retrieval_agent.index.delete(delete_all=True)
    
    # 2. Simulate the "Ingestion" flow
    print("\n--- Testing Ingestion Flow ---")
    fake_chunks = [
        "Llama 3 is the latest generation of our open source large language model.",
        "Groq is a company that builds custom chips for high-speed AI inference.",
        "The LPU (Language Processing Unit) from Groq is designed for sequential processing tasks.",
        "Model Context Protocol (MCP) is a structured way for AI agents to communicate.",
        "Pinecone is a vector database used for storing and retrieving high-dimensional data."
    ]
    
    fake_ingestion_mcp = {
        "payload": {
            "chunks": fake_chunks,
            "source_file": "test_document.txt"
        }
    }
    
    storage_response = retrieval_agent.embed_and_store(fake_ingestion_mcp)
    print("Storage Response:", json.dumps(storage_response, indent=2))
    
    # --- NEW: Robust waiting loop ---
    print("\n--- Waiting for Pinecone to finish indexing... ---")
    expected_vectors = len(fake_chunks)
    max_wait_seconds = 60
    start_time = time.time()
    
    while time.time() - start_time < max_wait_seconds:
        stats = retrieval_agent.index.describe_index_stats()
        current_vectors = stats.get('total_vector_count', 0)
        print(f"Current vector count: {current_vectors} / {expected_vectors}")
        if current_vectors >= expected_vectors:
            print("Indexing complete!")
            break
        time.sleep(5) # Wait 5 seconds before checking again
    else:
        print("Warning: Timed out waiting for vectors to be indexed.")


    # 3. Simulate the "Retrieval" flow
    print("\n--- Testing Retrieval Flow ---")
    user_query = "What is Groq's LPU?"
    
    fake_query_mcp = {
        "payload": {"query": user_query, "top_k": 3}
    }

    context_response = retrieval_agent.retrieve_context(fake_query_mcp)
    print("Context Response:", json.dumps(context_response, indent=2))

    print(f"\n--- Final Pinecone Index Stats ---")
    print(retrieval_agent.index.describe_index_stats())