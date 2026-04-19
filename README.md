# Enterprise RAG System with RBAC, GuardRails, and Monitoring

An advanced Retrieval-Augmented Generation (RAG) system built to deliver enterprise-grade performance, security, and observability. This project integrates Role-Based Access Control (RBAC), AI Guardrails, and a comprehensive monitoring stack to ensure secure and reliable AI interactions.

## Key Features

- **Retrieval-Augmented Generation (RAG)**: Leverages state-of-the-art LLMs and vector databases for accurate, context-aware information retrieval.
- **Role-Based Access Control (RBAC)**: Secure access management using JWT, ensuring users only retrieve information authorized for their roles (e.g., engineering, finance, hr, marketing).
- **AI Guardrails**: Built-in mechanisms to ensure AI outputs are safe, relevant, and aligned with enterprise policies.
- **Monitoring & Evaluation**: Comprehensive tracking of system performance and response quality using Ragas.
- **Robust APIs & UI**: FastAPI-powered backend with a user-friendly Streamlit frontend interface.

## Technology Stack

- **Frameworks & Orchestration**: LangChain (Groq, OpenAI, HuggingFace)
- **Vector Database**: Qdrant
- **Embeddings**: Sentence Transformers
- **Backend API**: FastAPI, Uvicorn, Pydantic
- **Frontend**: Streamlit
- **Document Processing**: PyMuPDF, Docling, Pandas
- **Authentication & Security**: PyJWT
- **Evaluation & Testing**: Ragas, Pytest

## Project Structure

- `data/`: Contains domain-specific documents categorized by department (engineering, finance, hr, marketing, general).
- `requirements.txt`: Python dependencies.
- `EnterpriseRAG_PRD.docx` & `# DESIGN.docx`: Product requirements and system design documents.

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Suryanshsaraf/RAG-with-RBAC-GuardRails-and-Monitoring.git
   cd RAG-with-RBAC-GuardRails-and-Monitoring
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables:**
   Create a `.env` file in the root directory and add your necessary API keys and configuration values (e.g., OpenAI API Key, Groq API Key, JWT Secret).

5. **Run the Backend (FastAPI):**
   ```bash
   uvicorn main:app --reload
   ```
   *(Note: Adjust the main script name as development progresses)*

6. **Run the Frontend (Streamlit):**
   ```bash
   streamlit run app.py
   ```
   *(Note: Adjust the app script name as development progresses)*

## Roadmap

This project is currently under active development. Refer to the internal PRD and Design documents for detailed implementation phases and architectural decisions.
