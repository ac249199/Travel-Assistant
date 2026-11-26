
import asyncio
from pprint import pprint

from app.services.google_maps_mcp import get_google_maps_tool


async def main():

    search_places_tool = await get_google_maps_tool(
        "search_places"
    )

    print("\n========== SEARCH PLACES TOOL ==========")

    print("Tool Name:", search_places_tool.name)

    print("\nTool Description:")
    print(search_places_tool.description)

    print("\nTool Input Schema:")

    pprint(search_places_tool.args_schema)


if __name__ == "__main__":
    asyncio.run(main())
