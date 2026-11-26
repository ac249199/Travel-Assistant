
from app.agents.travel_search import travel_search_extraction_chain


test_queries = [
    "Find budget hotels in Varanasi for 2 people from 25 November to 28 November.",

    "Find vegetarian restaurants near Assi Ghat.",

    "Find a taxi from Varanasi Airport to Assi Ghat."
]


for query in test_queries:

    print("\n" + "=" * 60)
    print("USER QUERY:", query)

    result = travel_search_extraction_chain.invoke({
        "user_query": query
    })

    print("\nEXTRACTED DETAILS:")
    print(result)
