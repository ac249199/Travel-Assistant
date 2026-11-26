
from app.rag.answer_generator import generate_answer

question = "What is the best hotel in Varanasi with a swimming pool?"

result = generate_answer(question)


print("\n========== BANARASI BHAUKAL TRAVEL GURU ==========")

print("\nUSER QUESTION:")
print(question)

print("\nGENERATED ANSWER:")
print(result["answer"])
print("\nSOURCES USED:")

print("\nSOURCE IDS SELECTED BY LLM:")
print(result["source_ids"])

for source in result["sources"]:

    print("\nTitle:", source["title"])
    print("Date:", source["date"])
    print("URL:", source["url"])
