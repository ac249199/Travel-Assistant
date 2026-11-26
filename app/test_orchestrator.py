
from app.orchestration.orchestrator import orchestrate


queries = [

    "What are the best places to visit in Varanasi?",

    "Plan a 3-day trip to Jaipur for two people.",

    "Find hotels in Goa for two people.",

    "I want to book a hotel in Manali.",

    "Hello, how are you?"

]


for query in queries:

    print("\nUSER:", query)

    result = orchestrate(query)

    print("\nORCHESTRATOR RESULT:")
    print(result)

    print("=" * 60)
