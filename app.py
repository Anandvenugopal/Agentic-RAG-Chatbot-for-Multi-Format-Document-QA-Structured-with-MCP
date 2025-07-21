
import os
import streamlit as st
import tempfile
from orchestrator import Orchestrator



CUSTOM_STYLES = """
<style>
    /* --- Professional Light Blue Theme CSS Variables --- */
    :root {
        --primary-blue: #2563eb;
        --primary-dark: #1d4ed8;
        --primary-light: #3b82f6;
        --secondary-blue: #60a5fa;
        --accent-cyan: #06b6d4;
        --accent-light: #0891b2;
        
        --bg-primary: #f8fafc;
        --bg-secondary: #f1f5f9;
        --bg-tertiary: #e2e8f0;
        --bg-elevated: #ffffff;
        
        --text-primary: #1e293b;
        --text-secondary: #475569;
        --text-muted: #64748b;
        --text-light: #94a3b8;
        --text-white: #ffffff;
        
        --border-light: #e2e8f0;
        --border-medium: #cbd5e1;
        --border-strong: #94a3b8;
        
        --shadow-xs: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow-sm: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        
        --blue-gradient: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        --cyan-gradient: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
        --light-gradient: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
    }

    /* --- Global App Styling --- */
    .stApp {
        background: var(--light-gradient);
        font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
        color: var(--text-primary);
        line-height: 1.6;
        letter-spacing: -0.01em;
    }

    /* Ensure proper text inheritance */
    .stApp *, .stApp p, .stApp div, .stApp span, .stApp label {
        color: inherit;
    }

    /* --- Typography Hierarchy --- */
    h1 {
        color: var(--text-primary);
        text-align: center;
        padding: 2rem 0 3rem 0;
        font-size: 2.75rem;
        font-weight: 700;
        letter-spacing: -0.05em;
        background: var(--blue-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0;
    }

    h2, h3, h4, h5, h6 {
        color: var(--text-primary);
        font-weight: 600;
        margin-bottom: 1rem;
        letter-spacing: -0.025em;
    }

    /* --- Enhanced Expanders --- */
    .st-expander {
        background: var(--bg-elevated);
        border: 1px solid var(--border-light);
        border-radius: 16px;
        box-shadow: var(--shadow-sm);
        margin-bottom: 1.5rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        overflow: hidden;
    }

    .st-expander:hover {
        border-color: var(--secondary-blue);
        box-shadow: var(--shadow-md);
        transform: translateY(-2px);
    }

    .st-expander[data-testid="expander"] > div:first-child {
        background: var(--bg-secondary);
        color: var(--text-primary);
        font-weight: 600;
        font-size: 1rem;
        padding: 1.25rem 1.5rem;
        border: none;
        border-bottom: 1px solid var(--border-light);
    }

    .st-expander .streamlit-expanderContent {
        padding: 1.5rem;
        background: var(--bg-elevated);
        color: var(--text-secondary);
    }

    /* --- Professional Button Styling --- */
    .stButton > button {
        border-radius: 12px;
        font-weight: 500;
        font-size: 0.925rem;
        padding: 0.75rem 1.5rem;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        border: 1px solid var(--primary-blue);
        background: var(--bg-elevated);
        color: var(--primary-blue);
        box-shadow: var(--shadow-xs);
        text-transform: none;
        letter-spacing: -0.01em;
        min-height: 44px;
    }

    .stButton > button:hover {
        background: var(--blue-gradient);
        color: var(--text-white);
        border-color: var(--primary-dark);
        box-shadow: var(--shadow-md);
        transform: translateY(-1px);
    }

    .stButton > button:active {
        transform: translateY(0);
        box-shadow: var(--shadow-sm);
    }

    .stButton > button:focus {
        outline: none;
        box-shadow: var(--shadow-md), 0 0 0 3px rgba(59, 130, 246, 0.1);
    }

    /* --- Primary Button Variant --- */
    .stButton.primary > button {
        background: var(--blue-gradient);
        color: var(--text-white);
        border-color: var(--primary-blue);
    }

    .stButton.primary > button:hover {
        background: var(--primary-dark);
        border-color: var(--primary-dark);
        box-shadow: var(--shadow-lg);
    }

    /* --- Enhanced Chat Interface --- */
    [data-testid="chat-message-container"] {
        border-radius: 20px;
        padding: 1.5rem;
        margin-bottom: 1.25rem;
        border: 1px solid var(--border-light);
        background: var(--bg-elevated);
        box-shadow: var(--shadow-xs);
        transition: all 0.3s ease;
    }

    [data-testid="chat-message-container"]:hover {
        box-shadow: var(--shadow-sm);
        border-color: var(--border-medium);
    }

    /* --- User Message Styling --- */
    [data-testid="chat-message-container"]:has([data-testid="chat-avatar-user"]) {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.05) 0%, rgba(37, 99, 235, 0.08) 100%);
        border-color: rgba(59, 130, 246, 0.2);
        margin-left: 3rem;
        color: var(--text-primary);
    }

    [data-testid="chat-message-container"]:has([data-testid="chat-avatar-user"]) * {
        color: var(--text-primary);
    }

    /* --- Assistant Message Styling --- */
    [data-testid="chat-message-container"]:has([data-testid="chat-avatar-assistant"]) {
        background: var(--bg-elevated);
        border-color: var(--border-light);
        margin-right: 3rem;
        color: var(--text-secondary);
    }

    [data-testid="chat-message-container"]:has([data-testid="chat-avatar-assistant"]) * {
        color: var(--text-secondary);
    }

    /* --- Chat Avatar Enhancements --- */
    [data-testid="chat-avatar-user"] {
        background: var(--blue-gradient) !important;
        border: 2px solid var(--bg-elevated) !important;
        box-shadow: var(--shadow-md) !important;
        width: 40px !important;
        height: 40px !important;
    }

    [data-testid="chat-avatar-assistant"] {
        background: var(--cyan-gradient) !important;
        border: 2px solid var(--bg-elevated) !important;
        box-shadow: var(--shadow-md) !important;
        width: 40px !important;
        height: 40px !important;
    }

    /* --- Source Context in Chat --- */
    [data-testid="chat-message-container"] .st-expander {
        background: var(--bg-secondary);
        border: 1px solid var(--border-medium);
        border-radius: 12px;
        margin-top: 1rem;
        box-shadow: none;
    }

    [data-testid="chat-message-container"] .st-expander[data-testid="expander"] > div:first-child {
        background: var(--bg-tertiary);
        color: var(--accent-light);
        font-size: 0.875rem;
        font-weight: 600;
        padding: 0.875rem 1.25rem;
        border-radius: 12px 12px 0 0;
    }

    [data-testid="chat-message-container"] .st-expander .streamlit-expanderContent {
        background: var(--bg-secondary);
        color: var(--text-secondary);
        padding: 1.25rem;
    }

    /* --- Input Field Styling --- */
    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        background: var(--bg-elevated) !important;
        border: 1px solid var(--border-medium) !important;
        border-radius: 12px !important;
        color: var(--text-primary) !important;
        font-size: 0.925rem !important;
        padding: 0.75rem 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: var(--shadow-xs) !important;
    }

    .stTextInput input:focus, .stTextArea textarea:focus, .stSelectbox select:focus {
        border-color: var(--primary-blue) !important;
        box-shadow: var(--shadow-sm), 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
        outline: none !important;
    }

    /* --- File Upload Styling --- */
    .stFileUploader {
        background: var(--bg-elevated);
        border: 2px dashed var(--border-medium);
        border-radius: 16px;
        padding: 2rem;
        transition: all 0.3s ease;
        text-align: center;
    }

    .stFileUploader:hover {
        border-color: var(--secondary-blue);
        background: rgba(59, 130, 246, 0.02);
    }

    .stFileUploader label {
        color: var(--text-muted) !important;
        font-weight: 500;
    }

    /* --- Sidebar Enhancements --- */
    .css-1d391kg, .st-emotion-cache-1d391kg {
        background: var(--bg-secondary);
        border-right: 1px solid var(--border-light);
    }

    /* --- Loading States --- */
    .stSpinner > div {
        border-color: var(--primary-light) transparent var(--primary-light) transparent !important;
    }

    /* --- Status Messages --- */
    .stSuccess {
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-left: 4px solid #10b981;
        border-radius: 12px;
        padding: 1rem 1.25rem;
        color: var(--text-primary);
    }

    .stError {
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.3);
        border-left: 4px solid #ef4444;
        border-radius: 12px;
        padding: 1rem 1.25rem;
        color: var(--text-primary);
    }

    .stWarning {
        background: rgba(245, 158, 11, 0.1);
        border: 1px solid rgba(245, 158, 11, 0.3);
        border-left: 4px solid #f59e0b;
        border-radius: 12px;
        padding: 1rem 1.25rem;
        color: var(--text-primary);
    }

    .stInfo {
        background: rgba(59, 130, 246, 0.1);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-left: 4px solid var(--primary-blue);
        border-radius: 12px;
        padding: 1rem 1.25rem;
        color: var(--text-primary);
    }

    /* --- Metric Cards --- */
    [data-testid="metric-container"] {
        background: var(--bg-elevated);
        border: 1px solid var(--border-light);
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: var(--shadow-xs);
        transition: all 0.3s ease;
    }

    [data-testid="metric-container"]:hover {
        box-shadow: var(--shadow-md);
        border-color: var(--border-medium);
    }

    /* --- Tables --- */
    .stDataFrame, [data-testid="stTable"] {
        background: var(--bg-elevated);
        border: 1px solid var(--border-light);
        border-radius: 12px;
        overflow: hidden;
        box-shadow: var(--shadow-xs);
    }

    .stDataFrame th, [data-testid="stTable"] th {
        background: var(--bg-secondary);
        color: var(--text-primary);
        font-weight: 600;
        padding: 1rem;
        border-bottom: 1px solid var(--border-light);
    }

    .stDataFrame td, [data-testid="stTable"] td {
        color: var(--text-secondary);
        padding: 0.875rem 1rem;
        border-bottom: 1px solid var(--border-light);
    }

    /* --- Custom Scrollbar --- */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: var(--bg-secondary);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb {
        background: var(--border-strong);
        border-radius: 4px;
        transition: background 0.3s ease;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: var(--primary-blue);
    }

    /* --- Tabs Styling --- */
    .stTabs [data-baseweb="tab-list"] {
        background: var(--bg-secondary);
        border-radius: 12px;
        padding: 0.25rem;
        gap: 0.25rem;
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        color: var(--text-muted);
        font-weight: 500;
        padding: 0.75rem 1rem;
        transition: all 0.2s ease;
    }

    .stTabs [aria-selected="true"] {
        background: var(--bg-elevated);
        color: var(--primary-blue);
        box-shadow: var(--shadow-xs);
    }

    /* --- Progress Bar --- */
    .stProgress .st-bo {
        background: var(--bg-tertiary);
        border-radius: 8px;
        overflow: hidden;
    }

    .stProgress .st-bp {
        background: var(--blue-gradient);
        border-radius: 8px;
    }

    /* --- Responsive Design --- */
    @media (max-width: 768px) {
        [data-testid="chat-message-container"] {
            margin-left: 0.5rem;
            margin-right: 0.5rem;
            padding: 1.25rem;
            border-radius: 16px;
        }
        
        h1 {
            font-size: 2rem;
            padding: 1.5rem 0 2rem 0;
        }

        .stButton > button {
            padding: 0.875rem 1.25rem;
            font-size: 0.875rem;
        }
    }

    /* --- Animation Utilities --- */
    @keyframes slideInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes fadeIn {
        from {
            opacity: 0;
        }
        to {
            opacity: 1;
        }
    }

    .animate-slide-up {
        animation: slideInUp 0.5s ease-out;
    }

    .animate-fade-in {
        animation: fadeIn 0.3s ease-in;
    }

    /* --- Focus Management --- */
    *:focus {
        outline: 2px solid var(--primary-blue);
        outline-offset: 2px;
    }

    button:focus, input:focus, textarea:focus, select:focus {
        outline: none;
    }
</style>
"""



st.set_page_config(
    page_title="Agentic RAG Chatbot",
    page_icon="🤖",
    layout="wide"
)

# Apply the custom styles from our control panel
st.markdown(CUSTOM_STYLES, unsafe_allow_html=True)

@st.cache_resource
def get_orchestrator():
    return Orchestrator()

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []
if "ingested_files" not in st.session_state:
    st.session_state.ingested_files = set()

st.title("Agentic RAG Chatbot 🤖")

with st.expander("📁 Manage Knowledge Base", expanded=True):
    st.subheader("Upload Documents")
    uploaded_files = st.file_uploader(
        "Upload documents to add them to the chatbot's knowledge.",
        type=['pdf', 'docx', 'pptx', 'txt', 'csv', 'md'],
        accept_multiple_files=True
    )

    if st.button("Process and Add to Knowledge Base"):
        if not uploaded_files:
            st.warning("Please upload at least one document first.")
        else:
            with st.spinner("Processing documents..."):
                orchestrator = get_orchestrator()
                newly_uploaded_files = [f for f in uploaded_files if f.name not in st.session_state.ingested_files]
                if not newly_uploaded_files:
                    st.info("All selected documents have already been processed.")
                else:
                    for uploaded_file in newly_uploaded_files:
                        st.info(f"Processing '{uploaded_file.name}'...")
                        try:
                            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                                tmp_file.write(uploaded_file.getvalue())
                                tmp_file_path = tmp_file.name
                            ingestion_result = orchestrator.ingest_document(tmp_file_path)
                            os.remove(tmp_file_path)
                            if ingestion_result['type'] == 'STORAGE_SUCCESS':
                                st.session_state.ingested_files.add(uploaded_file.name)
                            else:
                                st.error(f"Failed to process '{uploaded_file.name}': {ingestion_result.get('payload', {}).get('error', 'Unknown')}")
                        except Exception as e:
                            st.error(f"An error occurred with '{uploaded_file.name}': {e}")
                    st.success("Selected documents have been successfully added!")

    st.divider()
    st.subheader("Active Documents")
    if not st.session_state.ingested_files:
        st.info("The knowledge base is empty.")
    else:
        col1, col2 = st.columns([3, 1])
        with col1:
            for file_name in sorted(list(st.session_state.ingested_files)):
                st.markdown(f"- `{file_name}`")
        with col2:
            if st.button("Clear Knowledge Base"):
                with st.spinner("Forgetting everything..."):
                    orchestrator = get_orchestrator()
                    orchestrator.retrieval_agent.index.delete(delete_all=True)
                    st.session_state.ingested_files.clear()
                    st.session_state.messages.clear()
                    st.success("Knowledge base cleared!")
                    st.rerun()

st.divider()
st.header("Chat with your Documents")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "source_context" in message and message["source_context"]:
            with st.expander("View Source Context"):
                for i, context in enumerate(message["source_context"]):
                    source = context.get('source', 'Unknown')
                    text = context.get('text', 'No text available')
                    st.write(f"**Source {i+1} from `{source}`:**\n> {text}")

if prompt := st.chat_input("Ask a question about the uploaded documents..."):
    if not st.session_state.ingested_files:
        st.warning("Please upload and process at least one document.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Searching knowledge base..."):
                orchestrator = get_orchestrator()
                response_mcp = orchestrator.ask_question(prompt)
                payload = response_mcp.get('payload', {})
                answer = payload.get('answer', "Sorry, I encountered an error.")
                source_context = payload.get('source_context', [])
                st.markdown(answer)
                if source_context:
                    with st.expander("View Source Context"):
                        for i, context in enumerate(source_context):
                            source = context.get('source', 'Unknown')
                            text = context.get('text', 'No text available')
                            st.write(f"**Source {i+1} from `{source}`:**\n> {text}")
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": answer, 
                    "source_context": source_context
                })