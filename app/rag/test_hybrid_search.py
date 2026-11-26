
from app.rag.hybrid_retriever import hybrid_search


# Use the same query for both retrieval systems
query = "Subah-e-Banaras Assi Ghat morning aarti"


results = hybrid_search(
    query=query,
    n_results=5
)


print("\n========== HYBRID SEARCH (RRF) ==========")

print("User Query:", query)

for i, result in enumerate(results, start=1):

    print(f"\n========== RESULT {i} ==========")

    print("Chunk ID:", result["chunk_id"])

    print("Content:")
    print(result["content"])

    print("Metadata:")
    print(result["metadata"])

    print("RRF Score:")
    print(result["rrf_score"])
