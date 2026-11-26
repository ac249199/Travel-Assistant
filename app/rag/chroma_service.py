
import chromadb

# 1. Create a persistent ChromaDB client
client = chromadb.PersistentClient(
    path="data/chroma_db"
)


# 2. Create or access our collection
collection = client.get_or_create_collection(
    name="varanasi_knowledge",
    metadata={
        "hnsw:space": "cosine"
    }
)


# 3. Function to insert documents

def add_documents(
    ids,
    documents,
    embeddings,
    metadatas
):

    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings.tolist(),
        metadatas=metadatas
    )


# 4. Function to search documents
def search_documents(query_embedding, n_results=3):

    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=n_results
    )

    return results
