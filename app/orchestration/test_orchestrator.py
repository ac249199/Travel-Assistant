
import asyncio

from app.orchestration.orchestrator import orchestrate


async def main():

    conversation_id = "orchestrator_test_1"

    # Turn 1
    print("\n========== TURN 1 ==========")

    response = await orchestrate(
        "Plan a trip to Varanasi.",
        conversation_id
    )

    print(response)

    # Turn 2
    print("\n========== TURN 2 ==========")

    response = await orchestrate(
        "3 days.",
        conversation_id
    )

    print(response)

    # Turn 3
    print("\n========== TURN 3 ==========")

    response = await orchestrate(
        "2 people.",
        conversation_id
    )

    print(response)


if __name__ == "__main__":
    asyncio.run(main())
