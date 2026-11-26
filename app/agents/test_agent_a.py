
import asyncio

from app.agents.agent_a import run_agent_a


async def main():

    query = (
    "Explain the historical significance of Assi Ghat "
    "and show its Google Maps location."
    )
    response = await run_agent_a(query)

    print("\n========== AGENT A RESPONSE ==========")
    print(response)


if __name__ == "__main__":
    asyncio.run(main())
