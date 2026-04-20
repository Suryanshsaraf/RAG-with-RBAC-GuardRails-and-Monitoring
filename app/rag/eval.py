"""
RAG Evaluation module.

Uses RAGAS to evaluate retrieval and generation quality.
"""

from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevance,
    context_precision,
    context_recall,
)

from app.rag.engine import get_rag_engine


async def evaluate_rag(test_queries: list):
    """
    Evaluate the RAG engine on a set of test queries.
    Each query in test_queries should be a dict with:
    - 'question'
    - 'ground_truth' (optional)
    """
    engine = get_rag_engine()
    results = []

    for item in test_queries:
        # Execute RAG
        # Note: We use 'admin' role for evaluation to see all docs
        response = await engine.query(item["question"], role="admin", use_hyde=True)
        
        results.append({
            "question": item["question"],
            "answer": response["answer"],
            "contexts": [doc.page_content for doc in response["source_documents"]],
            "ground_truth": item.get("ground_truth", "")
        })

    # Convert to HuggingFace Dataset
    dataset = Dataset.from_list(results)

    # Run Ragas evaluation
    # Note: This requires an LLM (defaults to OpenAI)
    # To use Groq, we'd need to configure the Ragas evaluator llm.
    score = evaluate(
        dataset,
        metrics=[
            faithfulness,
            answer_relevance,
            context_precision,
            context_recall,
        ],
    )

    return score


if __name__ == "__main__":
    import asyncio
    
    test_data = [
        {
            "question": "What is the company leave policy?",
            "ground_truth": "The company offers various leaves including annual, sick, and maternity leave."
        }
    ]
    
    # asyncio.run(evaluate_rag(test_data))
    print("Evaluation script ready. Configure LLM keys to run.")
