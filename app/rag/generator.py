"""
Generator module.

Initializes the LLM (Groq) and provides the generation chain.
"""

from typing import List, Optional

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.documents import Document

from app.core.config import settings


def get_llm():
    """Initialize and return the Groq LLM."""
    return ChatGroq(
        groq_api_key=settings.groq_api_key,
        model_name=settings.llm_model_name,
        temperature=0.1,
    )


def format_docs(docs: List[Document]) -> str:
    """Format documents for the prompt."""
    formatted = []
    for i, doc in enumerate(docs):
        formatted.append(f"Document {i+1}:\n{doc.page_content}")
    return "\n\n".join(formatted)


def get_rag_chain():
    """
    Construct the LangChain RAG pipeline (Chain/LCEL).
    
    Returns a chain that takes a dict with 'question' and 'context' 
    and returns a string.
    """
    template = """You are a helpful assistant for an enterprise RAG system.
Use the following context to answer the question.
If the context doesn't contain enough information, say that you don't know based on the provided documents.
Do not use your own knowledge outside of the provided context.

Context:
{context}

Question: {question}

Helpful Answer:"""
    
    prompt = ChatPromptTemplate.from_template(template)
    llm = get_llm()
    
    chain = (
        prompt
        | llm
        | StrOutputParser()
    )
    
    return chain
