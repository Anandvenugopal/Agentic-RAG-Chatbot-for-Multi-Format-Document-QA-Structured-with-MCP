# ingestion_agent.py 
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from unstructured.partition.auto import partition

from mcp import create_mcp_message

class IngestionAgent:
    def __init__(self, agent_name="IngestionAgent"):
        self.name = agent_name
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )

    def parse_and_chunk_document(self, file_path):
        print(f"[{self.name}] Received request to parse {file_path} using 'unstructured'")
        
        try:
            # 'unstructured' automatically handles different file types
            elements = partition(filename=file_path)
            raw_text = "\n\n".join([str(el) for el in elements])

        except Exception as e:
            error_message = create_mcp_message(
                self.name, "Orchestrator", "INGESTION_ERROR", 
                {"file_path": file_path, "error": f"Failed to parse with unstructured: {str(e)}"}
            )
            return error_message

        if not raw_text.strip():
             error_message = create_mcp_message(
                self.name, "Orchestrator", "INGESTION_ERROR", 
                {"error": "No text extracted from document."}
            )
             return error_message

        chunks = self.text_splitter.split_text(raw_text)
        print(f"[{self.name}] Successfully chunked document into {len(chunks)} chunks.")
        
        # Using MCP to structure the successful response
        response_message = create_mcp_message(
            self.name,
            "RetrievalAgent", # The next agent in the pipeline
            "CHUNKS_READY",
            {"chunks": chunks, "source_file": os.path.basename(file_path)}
        )
        return response_message

# --- Let's test this step ---
if __name__ == "__main__":
    # Created a dummy file to test
    with open("test.txt", "w") as f:
        f.write("This is a test document powered by unstructured. It should handle this easily.\n" * 50)
        f.write("The agent will parse this text file and split it into chunks using the new library.")
        f.write("\nThis is the final sentence." * 10)

    agent = IngestionAgent()
    
    # Test a supported file type
    print("\n--- Testing TXT file with unstructured ---")
    result = agent.parse_and_chunk_document("test.txt")
    import json
    print(json.dumps(result, indent=2))
    
    # Check if chunks were created
    if result['type'] == 'CHUNKS_READY':
        print(f"Number of chunks: {len(result['payload']['chunks'])}")
        # Print a snippet of the first chunk
        print(f"First chunk snippet: '{result['payload']['chunks'][0][:100]}...'")

   
    os.remove("test.txt")
