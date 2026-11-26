
import chromadb
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path="./chroma_db")

collection = client.get_collection(
    name="varanasi_itineraries"
)


def retrieve_itinerary(
    query: str,
    top_k: int = 3,
    duration_days: int | None = None
):
    """
    Retrieve itinerary chunks based on the user's query
    and requested trip duration.
    """

    # Make the search query duration-specific
    if duration_days is not None:
        duration_query = (
            f"Banaras Itinerary for {duration_days} Days. "
            f"{duration_days} days in Varanasi. "
        )
        query = duration_query + query

    # Generate query embedding
    query_embedding = model.encode(query).tolist()

    # Search ChromaDB
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    return results["documents"][0]
