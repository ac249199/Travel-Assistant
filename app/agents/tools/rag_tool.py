
from langchain_core.tools import tool

from app.rag.answer_generator import generate_answer


@tool
def varanasi_knowledge_search(query: str) -> dict:
    """
    Search the Varanasi Guru knowledge base.

    Use this tool for questions about Varanasi's:
    - History and culture
    - Temples and ghats
    - Traditions and festivals
    - Local experiences
    - Heritage walks and tours

    Do not use this tool to verify live hotel availability,
    current restaurant ratings, or real-time opening hours.
    
    Pass the user's original question without
    rewriting or expanding it.
    """
    result = generate_answer(query)

    return {
        "answer": result["answer"],
        "sources": result["sources"]
    }
