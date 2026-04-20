import streamlit as st
import requests
import json
import time
import os
from typing import List, Dict

# --- Configuration & Constants ---
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="EnterpriseRAG Dashboard",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom Styling (Premium Look) ---
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #e0e0e0;
    }
    .chat-bubble {
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 1.5rem;
        display: flex;
        flex-direction: column;
        border: 1px solid #30363d;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .user-bubble {
        background-color: #161b22;
        border-left: 5px solid #238636;
    }
    .assistant-bubble {
        background-color: #1c2128;
        border-left: 5px solid #1f6feb;
    }
    .role-badge {
        font-size: 0.75rem;
        font-weight: bold;
        padding: 0.2rem 0.6rem;
        border-radius: 10px;
        margin-bottom: 0.5rem;
        width: fit-content;
    }
    .admin-badge { background-color: #8957e5; color: white; }
    .marketing-badge { background-color: #d29922; color: black; }
    .finance-badge { background-color: #238636; color: white; }
    .source-card {
        background-color: #0d1117;
        border: 1px solid #30363d;
        padding: 0.8rem;
        border-radius: 8px;
        font-size: 0.85rem;
        margin-top: 0.5rem;
    }
    .sidebar-section {
        padding: 1rem;
        background-color: #161b22;
        border-radius: 10px;
        margin-bottom: 1rem;
        border: 1px solid #30363d;
    }
</style>
""", unsafe_allow_html=True)

# --- Session State Management ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "token" not in st.session_state:
    st.session_state.token = None
if "role" not in st.session_state:
    st.session_state.role = None
if "username" not in st.session_state:
    st.session_state.username = None

# --- Helper Functions ---
def login(username, password):
    try:
        response = requests.post(f"{API_URL}/token", data={"username": username, "password": password})
        if response.status_code == 200:
            data = response.json()
            st.session_state.token = data["access_token"]
            st.session_state.username = username
            # Simple role extraction from dummy DB logic or token decode
            # For now, we'll just set it based on username for the demo
            role_map = {"admin": "admin", "mark": "marketing", "fin": "finance"}
            st.session_state.role = role_map.get(username, "general")
            return True
        return False
    except Exception as e:
        st.error(f"Login failed: {e}")
        return False

def upload_file(uploaded_file):
    if not st.session_state.token:
        st.error("Please login first")
        return
    
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
    
    with st.spinner(f"Uploading and indexing {uploaded_file.name}..."):
        try:
            response = requests.post(f"{API_URL}/upload", headers=headers, files=files)
            if response.status_code == 200:
                st.success(f"Successfully indexed {uploaded_file.name}!")
                return True
            else:
                st.error(f"Upload failed: {response.text}")
                return False
        except Exception as e:
            st.error(f"Upload error: {e}")
            return False

# --- Sidebar ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>🔐 Control Center</h2>", unsafe_allow_html=True)
    
    if not st.session_state.token:
        with st.container():
            st.markdown("<div class='sidebar-section'>", unsafe_allow_html=True)
            st.subheader("Login")
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.button("Sign In", use_container_width=True):
                if login(u, p):
                    st.rerun()
                else:
                    st.error("Invalid credentials")
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        with st.container():
            st.markdown("<div class='sidebar-section'>", unsafe_allow_html=True)
            st.markdown(f"**User:** `{st.session_state.username}`")
            st.markdown(f"**Role:** <span class='role-badge {st.session_state.role}-badge'>{st.session_state.role.upper()}</span>", unsafe_allow_html=True)
            if st.button("Logout", use_container_width=True):
                st.session_state.token = None
                st.session_state.messages = []
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
            
            # --- Document Upload Section ---
            st.markdown("<div class='sidebar-section'>", unsafe_allow_html=True)
            st.subheader("📁 Upload Data")
            uploaded_file = st.file_uploader("Add to Knowledge Base", type=["md", "csv", "pdf"])
            if uploaded_file and st.button("Process & Index", use_container_width=True):
                upload_file(uploaded_file)
            st.markdown("</div>", unsafe_allow_html=True)

    # --- Settings Section ---
    with st.container():
        st.markdown("<div class='sidebar-section'>", unsafe_allow_html=True)
        st.subheader("⚙️ RAG Settings")
        top_k = st.slider("Top K Chunks", 1, 15, 5)
        use_hyde = st.toggle("HyDE Expansion", value=False)
        multi_query = st.toggle("Multi-Query", value=False)
        st.markdown("</div>", unsafe_allow_html=True)

# --- Main Chat Interface ---
st.title("🏢 Enterprise Knowledge Base")
st.caption("Secure Hybrid Search with RBAC & Guardrails")

# Display chat messages
for msg in st.session_state.messages:
    role_class = "user-bubble" if msg["role"] == "user" else "assistant-bubble"
    st.markdown(f"""
    <div class="chat-bubble {role_class}">
        <div style="font-weight: bold; margin-bottom: 0.5rem;">{'👤 User' if msg["role"] == "user" else '🤖 Assistant'}</div>
        <div>{msg["content"]}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Show sources if available
    if msg["role"] == "assistant" and "sources" in msg:
        with st.expander("🔍 View Sources"):
            for i, source in enumerate(msg["sources"]):
                st.markdown(f"""
                <div class="source-card">
                    <strong>Source {i+1}: {source['metadata'].get('source', 'Unknown')}</strong><br/>
                    {source['content'][:300]}...
                </div>
                """, unsafe_allow_html=True)

# Chat input
if prompt := st.chat_input("Ask a question about policies, finance, or marketing..."):
    if not st.session_state.token:
        st.warning("Please login to start chatting.")
    else:
        # Add user message to session
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        st.markdown(f"""
        <div class="chat-bubble user-bubble">
            <div style="font-weight: bold; margin-bottom: 0.5rem;">👤 User</div>
            <div>{prompt}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Assistant response
        with st.markdown(f'<div class="chat-bubble assistant-bubble"><div style="font-weight: bold; margin-bottom: 0.5rem;">🤖 Assistant</div>', unsafe_allow_html=True):
            response_placeholder = st.empty()
            full_response = ""
            sources = []
            
            headers = {"Authorization": f"Bearer {st.session_state.token}"}
            
            try:
                with requests.post(
                    f"{API_URL}/query/stream",
                    headers=headers,
                    json={
                        "question": prompt,
                        "top_k": top_k,
                        "use_hyde": use_hyde,
                        "multi_query": multi_query
                    },
                    stream=True
                ) as r:
                    for line in r.iter_lines():
                        if line:
                            data = json.loads(line.decode('utf-8'))
                            
                            if "answer" in data:
                                full_response += data["answer"]
                                response_placeholder.markdown(full_response + "▌")
                            
                            if "sources" in data:
                                sources = data["sources"]
                            
                            if data.get("guardrail_triggered"):
                                st.warning("⚠️ Guardrail Triggered: Content might be filtered or modified.")
                
                response_placeholder.markdown(full_response)
                
                # Save to history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": full_response,
                    "sources": sources
                })
                
                if sources:
                    with st.expander("🔍 View Sources"):
                        for i, source in enumerate(sources):
                            st.markdown(f"""
                            <div class="source-card">
                                <strong>Source {i+1}: {source['metadata'].get('source', 'Unknown')}</strong><br/>
                                {source['content'][:300]}...
                            </div>
                            """, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"Error communicating with API: {e}")
        st.markdown('</div>', unsafe_allow_html=True)
