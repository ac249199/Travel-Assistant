
import json
from pathlib import Path
from sentence_transformers import SentenceTransformer
import chromadb

# Step 1: Load itinerary chunks
input_path = Path("data/itineraries/itinerary_chunks.json")

with open(input_path, "r", encoding="utf-8") as file:
    chunks = json.load(file)

print("Total chunks loaded:", len(chunks))

# Step 2: Load the existing embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Step 3: Generate embeddings
embeddings = model.encode(
    chunks,
    convert_to_numpy=True,
    show_progress_bar=True
)

print("Embedding shape:", embeddings.shape)

# Step 4: Connect to persistent ChromaDB
client = chromadb.PersistentClient(path="./chroma_db")

# Step 5: Create a separate itinerary collection
collection = client.get_or_create_collection(
    name="varanasi_itineraries",
    metadata={"hnsw:space": "cosine"}
)

# Step 6: Store chunks and embeddings
collection.add(
    ids=[f"itinerary_{i}" for i in range(len(chunks))],
    documents=chunks,
    embeddings=embeddings.tolist(),
    metadatas=[
        {
            "source": "Banaras_Itineraries.pdf",
            "chunk_number": i
        }
        for i in range(len(chunks))
    ]
)

print("Itinerary embeddings stored successfully!")
print("Total records in collection:", collection.count())
