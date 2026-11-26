
import chromadb
from sentence_transformers import SentenceTransformer

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Connect to ChromaDB
client = chromadb.PersistentClient(path="./chroma_db")

# Access itinerary collection
collection = client.get_collection(
    name="varanasi_itineraries"
)

# User query
query = "What should I visit on the second day of my Varanasi trip?"

# Convert query into embedding
query_embedding = model.encode(query).tolist()

# Search relevant chunks
results = collection.query(
    query_embeddings=[query_embedding],
    n_results=3
)

# Display results
print("\nUser Query:", query)

for i, document in enumerate(results["documents"][0]):
    print(f"\nResult {i+1}:")
    print(document)
