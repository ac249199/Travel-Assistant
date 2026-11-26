
from app.rag.hybrid_retriever import hybrid_search
from app.rag.reranker_service import rerank_documents


# Test query
query = "Tell me about Assi Ghat."


# 1. Retrieve candidate chunks using hybrid search
retrieved_documents = hybrid_search(
    query=query,
    n_results=15
)


print("\n========== ORIGINAL RRF RESULTS ==========")

for index, document in enumerate(retrieved_documents, start=1):

    print(f"\nRank: {index}")
    print("Title:", document["metadata"].get("title"))
    print("RRF Score:", document.get("rrf_score"))
    print("Content:", document["content"][:200])


# 2. Rerank retrieved documents
reranked_documents = rerank_documents(
    query=query,
    documents=retrieved_documents
)


print("\n========== RERANKED RESULTS ==========")

for index, document in enumerate(reranked_documents, start=1):

    print(f"\nRank: {index}")
    print("Title:", document["metadata"].get("title"))
    print("RRF Score:", document.get("rrf_score"))
    print("Reranker Score:", document.get("reranker_score"))
    print("Content:", document["content"][:200])
