
import json
import numpy as np

from app.rag.chroma_service import (
    collection,
    add_documents
)


# 1. Load all chunks
with open(
    "data/varanasi_chunks.json",
    "r",
    encoding="utf-8"
) as file:
    data = json.load(file)

chunks = data["chunks"]


# 2. Load all embeddings
embeddings = np.load(
    "data/varanasi_embeddings.npy"
)


# 3. Validate matching counts
if len(chunks) != len(embeddings):
    raise ValueError(
        "Number of chunks and embeddings does not match"
    )


# 4. Prepare data for ChromaDB
ids = []
documents = []
metadatas = []

for chunk in chunks:

    ids.append(chunk["chunk_id"])

    documents.append(chunk["content"])

    metadata = {
        key: value
        for key, value in chunk["metadata"].items()
        if value is not None
    }

    metadatas.append(metadata)


# 5. Insert all records
add_documents(
    ids=ids,
    documents=documents,
    embeddings=embeddings,
    metadatas=metadatas
)


# 6. Verify insertion
print("\n========== CHROMADB BULK INGESTION ==========")

print("Total chunks:", len(chunks))
print("Total embeddings:", len(embeddings))
print("Records in ChromaDB:", collection.count())

print("\nBulk ingestion completed!")
