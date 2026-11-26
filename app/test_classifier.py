
from app.orchestration.intent_classifier import classify_intent


queries = [
    "What are the best places to visit in Varanasi?",

    "Plan a 3-day trip to Jaipur for two people.",

    "Find hotels in Goa for two people.",

    "I want to book a hotel in Manali.",

    "Hello, how are you?"
]


for query in queries:

    print("\nUSER QUERY:", query)

    result = classify_intent(query)

    print("\nCLASSIFICATION:")
    print(result.model_dump())

    print("-" * 60)
