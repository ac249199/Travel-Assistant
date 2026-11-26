
import asyncio

from app.services.google_maps_mcp import (
    get_google_maps_tools,
    get_google_maps_tool
)


async def main():

    # Get all available tools
    tools = await get_google_maps_tools()

    print("\n========== ALL MAPS TOOLS ==========")

    for tool in tools:
        print(tool.name)

    # Get one specific tool
    search_tool = await get_google_maps_tool("search_places")

    print("\n========== SELECTED TOOL ==========")
    print("Tool name:", search_tool.name)

    # Call the loader again to check the cache
    tools_again = await get_google_maps_tools()

    print("\n========== CACHE TEST ==========")
    print("Same cached list:", tools is tools_again)


if __name__ == "__main__":
    asyncio.run(main())
