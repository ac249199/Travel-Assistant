
import asyncio

from app.orchestration.orchestrator import orchestrate


async def main():

    response = await orchestrate(
        "Tell me about the history and cultural significance of Kashi Vishwanath Temple.",
        conversation_id="agent_a_test_1"
    )

    print("\n========== AGENT A RESPONSE ==========")
    print(response)


if __name__ == "__main__":
    asyncio.run(main())
