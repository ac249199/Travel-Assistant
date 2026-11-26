from app.rag.itinerary_retriever import retrieve_itinerary

query = "What should I visit on the second day of my Varanasi trip?"

results = retrieve_itinerary(query, top_k=3)

print("\nUser Query:", query)

for i, document in enumerate(results, start=1):
    print(f"\nRetrieved Chunk {i}:")
    print(document)