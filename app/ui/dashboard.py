"""
EnterpriseRAG Dashboard.

Streamlit frontend for interacting with the RAG system.
"""

import streamlit as st
import requests
import json
from typing import List, Optional

# --- Page Config ---
st.set_page_config(
    page_title="EnterpriseRAG Dashboard",
    page_icon="🤖",
    layout="wide"
)

API_URL = "http://localhost:8000"

# --- Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "token" not in st.session_state:
    st.session_state.token = None
if "role" not in st.session_state:
    st.session_state.role = None
if "username" not in st.session_state:
    st.session_state.username = None

# --- Auth Helper ---
def login(username, password):
    try:
        response = requests.post(
            f"{API_URL}/token",
            data={"username": username, "password": password}
        )
        if response.status_code == 200:
            data = response.json()
            st.session_state.token = data["access_token"]
            st.session_state.username = username
            # We don't get role back in token response usually, 
            # but we can decode it if we wanted. 
            # For simplicity, let's just mark logged in.
            return True
        return False
    except Exception as e:
        st.error(f"Connection error: {e}")
        return False

# --- Sidebar: Auth & Info ---
with st.sidebar:
    st.title("🔐 Access Control")
    
    if not st.session_state.token:
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if login(username, password):
                st.success(f"Logged in as {username}")
                st.rerun()
            else:
                st.error("Invalid credentials")
        
        st.info("Demo Users:\n- admin / admin123\n- mark / mark123\n- fin / fin123")
    else:
        st.write(f"Logged in as: **{st.session_state.username}**")
        if st.button("Logout"):
            st.session_state.token = None
            st.session_state.username = None
            st.session_state.messages = []
            st.rerun()

    st.divider()
    st.subheader("Settings")
    top_k = st.slider("Top K Chunks", 1, 10, 5)

# --- Main Interface ---
st.title("🏢 Enterprise Knowledge Base")
st.markdown("### Hybrid Search RAG with RBAC & Guardrails")

if not st.session_state.token:
    st.warning("Please login to access the knowledge base.")
    st.stop()

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message:
            with st.expander("View Sources"):
                for i, src in enumerate(message["sources"]):
                    st.write(f"**Source {i+1}:** {src['metadata'].get('source', 'Unknown')}")
                    st.caption(src["content"][:200] + "...")

# Chat Input
if prompt := st.chat_input("Ask a question about company policies, finances, or marketing..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get response from API
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        with st.spinner("Thinking..."):
            try:
                headers = {"Authorization": f"Bearer {st.session_state.token}"}
                response = requests.post(
                    f"{API_URL}/query",
                    headers=headers,
                    json={"question": prompt, "top_k": top_k}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data["answer"]
                    sources = data["sources"]
                    guardrail = data["guardrail_triggered"]
                    
                    if guardrail:
                        st.warning("⚠️ Guardrail Triggered")
                    
                    message_placeholder.markdown(answer)
                    
                    # Store assistant response
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": answer,
                        "sources": sources
                    })
                    
                    if sources:
                        with st.expander("View Sources"):
                            for i, src in enumerate(sources):
                                st.write(f"**Source {i+1}:** {src['metadata'].get('source', 'Unknown')}")
                                st.caption(src["content"][:200] + "...")
                else:
                    error_detail = response.json().get("detail", "Unknown error")
                    st.error(f"API Error: {error_detail}")
            except Exception as e:
                st.error(f"Error: {e}")
