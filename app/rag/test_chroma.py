
import json
import numpy as np

from app.rag.chroma_service import (
    collection,
    add_documents,
    search_documents
)


# 1. Load chunks
with open(
    "data/varanasi_chunks.json",
    "r",
    encoding="utf-8"
) as file:
    data = json.load(file)

first_chunk = data["chunks"][0]


# 2. Load embeddings
embeddings = np.load(
    "data/varanasi_embeddings.npy"
)

first_embedding = embeddings[0]


# 3. Prepare metadata
metadata = {
    key: value
    for key, value in first_chunk["metadata"].items()
    if value is not None
}


# 4. Insert one chunk
add_documents(
    ids=[first_chunk["chunk_id"]],
    documents=[first_chunk["content"]],
    embeddings=first_embedding.reshape(1, -1),
    metadatas=[metadata]
)


print("\n========== INSERTION SUCCESSFUL ==========")
print("Collection name:", collection.name)
print("Total records:", collection.count())


# 5. Search using the same embedding
results = search_documents(
    query_embedding=first_embedding,
    n_results=1
)


print("\n========== SEARCH RESULTS ==========")

print("Retrieved document:")
print(results["documents"][0][0])

print("\nRetrieved metadata:")
print(results["metadatas"][0][0])

print("\nDistance:")
print(results["distances"][0][0])
