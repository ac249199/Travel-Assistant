
from app.agents.agent_b import run_agent_b


conversation_id = "test_conversation_1"


# Turn 1
print("\n========== TURN 1 ==========\n")

response = run_agent_b(
    "Plan a trip to Varanasi.",
    conversation_id
)

print(response)


# Turn 2
print("\n========== TURN 2 ==========\n")

response = run_agent_b(
    "3 days.",
    conversation_id
)

print(response)


# Turn 3
print("\n========== TURN 3 ==========\n")

response = run_agent_b(
    "2 people.",
    conversation_id
)

print(response)
