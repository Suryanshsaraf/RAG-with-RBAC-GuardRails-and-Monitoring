import asyncio
from app.rag.engine import get_rag_engine
import os
from dotenv import load_dotenv

load_dotenv()

async def test_query():
    engine = get_rag_engine()
    try:
        result = await engine.query("What are the data privacy policies?", role="admin")
        print("RESULT:", result)
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_query())
