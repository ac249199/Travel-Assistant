
from app.rag.bm25_service import search_bm25
from app.rag.chroma_service import search_documents
from app.rag.embedding_service import generate_embedding


# RRF configuration
RRF_K = 60


def hybrid_search(query, n_results=5):

    # 1. Semantic search
    query_embedding = generate_embedding(query)

    semantic_results = search_documents(
        query_embedding=query_embedding,
        n_results=10
    )

    # 2. BM25 keyword search
    keyword_results = search_bm25(
        query=query,
        n_results=10
    )

    # 3. Store combined rankings
    combined_results = {}

    # Process semantic search results
    for rank, chunk_id in enumerate(
        semantic_results["ids"][0],
        start=1
    ):

        combined_results[chunk_id] = {
            "chunk_id": chunk_id,
            "content": semantic_results["documents"][0][rank - 1],
            "metadata": semantic_results["metadatas"][0][rank - 1],
            "rrf_score": 0
        }

        combined_results[chunk_id]["rrf_score"] += (
            1 / (RRF_K + rank)
        )

    # Process BM25 results
    for rank, result in enumerate(
        keyword_results,
        start=1
    ):

        chunk_id = result["chunk_id"]

        if chunk_id not in combined_results:

            combined_results[chunk_id] = {
                "chunk_id": chunk_id,
                "content": result["content"],
                "metadata": result["metadata"],
                "rrf_score": 0
            }

        combined_results[chunk_id]["rrf_score"] += (
            1 / (RRF_K + rank)
        )

    # 4. Sort by combined RRF score
    ranked_results = sorted(
        combined_results.values(),
        key=lambda x: x["rrf_score"],
        reverse=True
    )

    return ranked_results[:n_results]
