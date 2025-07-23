# mcp.py
import uuid
import json

def create_mcp_message(sender, receiver, msg_type, payload=None):
    """
    Creates a structured message following the Model Context Protocol (MCP).
    """
    return {
        "sender": sender,
        "receiver": receiver,
        "type": msg_type,
        "trace_id": str(uuid.uuid4()),
        "payload": payload if payload is not None else {}
    }

if __name__ == "__main__":
    print("--- Testing MCP Message Creation ---")
    
    ingestion_request = create_mcp_message(
        sender="Orchestrator",
        receiver="IngestionAgent",
        msg_type="INGEST_REQUEST",
        payload={"file_path": "/path/to/my/document.pdf"}
    )
    print(json.dumps(ingestion_request, indent=2))
