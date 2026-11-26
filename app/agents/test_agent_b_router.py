from app.agents.agent_b_router import route_agent_b


queries = [
    "Plan a 3-day trip to Varanasi.",
    "Find three budget hotels in Varanasi.",
    "I want to book Hotel Taj."
]


for query in queries:

    print("\nUser Query:", query)

    result = route_agent_b(query)

    print("Selected Workflow:", result.workflow)
    print("Reason:", result.reason)