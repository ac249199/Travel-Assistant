from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.agents import (
    create_tool_calling_agent,
    AgentExecutor
)

from app.services.llm_service import get_llm
from app.agents.tools.rag_tool import varanasi_knowledge_search
from app.services.google_maps_mcp import get_google_maps_tool


llm = get_llm()


async def run_agent_a(user_query: str):

    # Load Google Maps search tool
    search_places_tool = await get_google_maps_tool(
        "search_places"
    )

    # Available tools for Agent A
    tools = [
        varanasi_knowledge_search,
        search_places_tool
    ]

    system_prompt = """
    You are Agent A of Banarasi Bhaukal Travel Guru.

    Your role is to provide travel information and guidance
    specifically about Varanasi.

    You have access to two tools:

    1. varanasi_knowledge_search

       Use this tool for:
       - Historical information
       - Temple history and cultural significance
       - Ghats and traditions
       - Festivals and heritage experiences
       - Cultural and historical explanations

    2. search_places

       Use this tool for:
       - Finding temples, restaurants and hotels
       - Finding tourist attractions
       - Finding addresses and Google Maps locations
       - Finding place ratings and reviews when available

    TOOL SELECTION RULES:

    1. If the user asks to find, list, locate or recommend
       places, use search_places.

    2. If the user asks about history, culture, traditions
       or heritage, use varanasi_knowledge_search.

    3. If the user asks for both location information
       and historical information, use both tools.

    4. For a request asking for multiple places, make ONE
       search_places call with an appropriate page_size.

       Example:
       If the user asks for five famous temples in Varanasi,
       search for "Famous temples in Varanasi, Uttar Pradesh, India"
       with page_size=5.

       Do not search for every place separately unless
       the user specifically requests separate searches.

    5. Do not invoke RAG for simple location searches.

    6. Do not use Google Maps as a substitute for historical
       or cultural knowledge.

    7. Use only information supported by tool results.

    8. Never invent historical facts, ratings, addresses,
       opening hours or coordinates.

    9. Include Google Maps links when available.

    10. Include source attribution when available.

    11. If information is unavailable, clearly say so.

    12. Never claim that a booking has been completed.

    ANSWERING RULES:

    - Answer the user's original question directly.
    - Present multiple places in a clear numbered list.
    - Include relevant details returned by the tools.
    - Distinguish historical information from live place-search
      results.
    - Do not add unsupported information just to make
      the answer longer.
    """

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}")
    ])

    # Create the tool-calling agent
    agent = create_tool_calling_agent(
        llm=llm,
        tools=tools,
        prompt=prompt
    )

    # Create agent executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=4
    )

    # Execute Agent A
    response = await agent_executor.ainvoke({
        "input": user_query
    })

    return response["output"]
