
from sentence_transformers import CrossEncoder

# Load the reranker model
RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

reranker = CrossEncoder(RERANKER_MODEL)


def rerank_documents(query: str, documents: list):

    if not documents:
        return []

    # Prepare query-document pairs
    pairs = [
        (query, document["content"])
        for document in documents
    ]

    # Calculate relevance scores
    scores = reranker.predict(pairs)

    # Attach scores to documents
    reranked_documents = []

    for document, score in zip(documents, scores):

        document = document.copy()

        document["reranker_score"] = float(score)

        reranked_documents.append(document)

    # Sort by relevance score
    reranked_documents.sort(
        key=lambda x: x["reranker_score"],
        reverse=True
    )

    return reranked_documents
