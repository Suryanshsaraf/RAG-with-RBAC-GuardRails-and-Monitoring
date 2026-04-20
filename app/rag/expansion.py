"""
Query Expansion module.

Implements HyDE (Hypothetical Document Embeddings) and other expansion techniques.
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.rag.generator import get_llm


async def generate_hypothetical_document(query: str) -> str:
    """
    Generate a hypothetical document (HyDE) based on the user query.
    """
    template = """You are an expert technical writer. 
Write a short, factual paragraph that answers the following question. 
Do not say "Based on my knowledge" or "Here is an answer". 
Just provide the factual content as it might appear in a company handbook or report.

Question: {question}

Factual Paragraph:"""
    
    prompt = ChatPromptTemplate.from_template(template)
    llm = get_llm()
    
    chain = prompt | llm | StrOutputParser()
    
    # Generate the hypothetical document
    hypothetical_doc = await chain.ainvoke({"question": query})
    return hypothetical_doc
