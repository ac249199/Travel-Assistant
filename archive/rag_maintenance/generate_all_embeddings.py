
import json
import numpy as np

from app.rag.embedding_service import generate_embeddings


# 1. Load all chunks
with open(
    "data/varanasi_chunks.json",
    "r",
    encoding="utf-8"
) as file:
    data = json.load(file)


chunks = data["chunks"]


# 2. Extract text from every chunk
texts = [
    chunk["content"]
    for chunk in chunks
]


# 3. Generate embeddings
embeddings = generate_embeddings(texts)


# 4. Display embedding information
print("\n========== EMBEDDING GENERATION ==========")

print("Total chunks:", len(chunks))
print("Embedding matrix shape:", embeddings.shape)
print("Data type:", embeddings.dtype)


# 5. Save embeddings separately
np.save(
    "data/varanasi_embeddings.npy",
    embeddings
)

print("\nEmbeddings saved successfully!")
print("Output: data/varanasi_embeddings.npy")
