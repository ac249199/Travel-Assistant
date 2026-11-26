
from langchain_mcp_adapters.client import MultiServerMCPClient

from app.config import GOOGLE_MAPS_API_KEY


# Create Google Maps MCP client
maps_mcp_client = MultiServerMCPClient(
    {
        "google_maps": {
            "transport": "streamable_http",
            "url": "https://mapstools.googleapis.com/mcp",
            "headers": {
                "X-Goog-Api-Key": GOOGLE_MAPS_API_KEY,
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream"
            }
        }
    }
)


# Cache the discovered tools
_maps_tools = None


async def get_google_maps_tools():

    global _maps_tools

    if _maps_tools is None:
        print("Loading Google Maps MCP tools...")

        _maps_tools = await maps_mcp_client.get_tools()

        print("Google Maps MCP tools loaded successfully!")

    return _maps_tools


# Get one specific tool by name
async def get_google_maps_tool(tool_name: str):

    tools = await get_google_maps_tools()

    for tool in tools:
        if tool.name == tool_name:
            return tool

    raise ValueError(
        f"Google Maps tool '{tool_name}' was not found."
    )
