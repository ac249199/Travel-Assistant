
from sentence_transformers import SentenceTransformer


# 1. Load the embedding model
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

embedding_model = SentenceTransformer(MODEL_NAME)


# 2. Function to generate an embedding
def generate_embedding(text: str):

    if not text or not text.strip():
        raise ValueError("Text cannot be empty")

    embedding = embedding_model.encode(text)

    return embedding


# 3. Function to generate embeddings for multiple texts
def generate_embeddings(texts: list[str]):

    if not texts:
        raise ValueError("Text list cannot be empty")

    embeddings = embedding_model.encode(texts)

    return embeddings
