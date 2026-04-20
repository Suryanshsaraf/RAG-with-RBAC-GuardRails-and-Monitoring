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


async def rewrite_query(query: str, n: int = 3) -> List[str]:
    """
    Generate N alternative versions of the query to improve retrieval coverage.
    """
    template = """You are an AI assistant tasked with optimizing search queries.
Generate {n} different versions of the following user question to retrieve relevant documents from a knowledge base.
Provide each version on a new line, starting with a hyphen (-).

Question: {question}

Alternative Versions:"""

    prompt = ChatPromptTemplate.from_template(template)
    llm = get_llm()
    
    chain = prompt | llm | StrOutputParser()
    
    response = await chain.ainvoke({"question": query, "n": n})
    
    # Parse lines starting with '-'
    alternatives = [
        line.strip("- ").strip() 
        for line in response.strip().split("\n") 
        if line.strip().startswith("-")
    ]
    
    # Ensure original query is included
    if query not in alternatives:
        alternatives.append(query)
        
    return alternatives[:n+1]
