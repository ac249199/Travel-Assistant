from app.services.llm_service import get_llm
from app.rag.hybrid_retriever import hybrid_search
from app.rag.reranker_service import rerank_documents
from langchain_core.prompts import ChatPromptTemplate


# 1. Get the existing LLM
llm = get_llm()


# 2. Define the answer-generation prompt
prompt = ChatPromptTemplate.from_messages([

    (
        "system",
        
    """
    You are Banarasi Bhaukal Travel Guru,
    a friendly, knowledgeable and helpful travel assistant
    specializing in Varanasi.

    Your goal is to provide natural, engaging and useful
    answers to people exploring Varanasi.

    Answer the user's question using ONLY the information
    provided in the retrieved context.

    Instructions:

    1. Give direct, clear, conversational and natural answers.
    2. Start with the actual answer. Never begin with phrases like:
    - "In the available information..."
    - "According to the retrieved context..."
    - "Based on the provided context..."
    - "As per the knowledge base..."
    - "The sources mention..."
    - "From the given information..."
    3. Never tell the user that you are reading retrieved
    documents, context or a knowledge base.
    4. Do not invent facts, timings, prices, locations,
    recommendations or other information.
    5. If the retrieved information does not answer the
    question, politely say that you don't have enough
    reliable information to answer that specific question.
    Do not guess or make up an answer.
    6. If the retrieved information contains conflicting
    details, explain the uncertainty clearly.
    7. Pay attention to publication dates. Do not present
    outdated timings, prices, schedules or events as
    currently verified information.
    8. Do not treat promotional content as factual guidance.
    9. Keep the answer focused on the user's actual question.
    10. Use simple, friendly and engaging language.
    11. Use bullet points or numbered lists when they make
        the answer easier to understand.
    12. Avoid unnecessary introductions and repetitive
        concluding statements.
    13. Do not force an itinerary or additional suggestions
        unless they are relevant to the user's question.
    15. Each retrieved document has a unique source ID.
    16. Use the source IDs to identify which documents
        actually support your answer.
    17. Return only source IDs that genuinely support
        the information in your answer.
    18. Do not include irrelevant sources.
    19. If no retrieved source supports the answer,
        return an empty source_ids list.
    20. Do not invent source IDs.
    21. Exact timings, prices and schedules must be treated
    as time-sensitive information.

    22. Never include an exact timing if its current validity
        cannot be established from the retrieved information.

    23. When the source date is old or the information is
        undated, omit the exact timing rather than guessing.

    24. Never convert historical information into a
        current recommendation.

    Remember:
    Speak like a helpful Varanasi travel guide,
    not like an AI explaining where it found its information.

    Return your response using the required structured output:
    - answer: The final user-friendly answer.
    - source_ids: IDs of the sources actually used.

    Retrieved Context:

    {context}
    """

    ),

    (
        "human",
        "{question}"
    )
])


# 3. Create the answer-generation chain
from app.schemas.rag_answer_schema import RAGAnswer

structured_llm = llm.with_structured_output(RAGAnswer)

answer_chain = prompt | structured_llm


# 4. Main RAG function

def generate_answer(question: str):

   # Step 1: Retrieve 15 candidate chunks
    retrieved_chunks = hybrid_search(
        query=question,
        n_results=15
    )

    # Step 2: Rerank the retrieved chunks
    reranked_chunks = rerank_documents(
        query=question,
        documents=retrieved_chunks
    )

    # Step 3: Select the top 5 relevant chunks
    retrieved_chunks = reranked_chunks[:5]
    print("\n========== RETRIEVAL DEBUG ==========")

    for index, chunk in enumerate(retrieved_chunks, start=1):

        metadata = chunk["metadata"]

        print(f"\nSource ID: S{index}")
        print("Title:", metadata.get("title"))
        print("URL:", metadata.get("url"))
        print("RRF Score:", chunk.get("rrf_score"))
        print("Reranker Score:", chunk.get("reranker_score"))
        print("Content Preview:", chunk["content"][:300])

    # Handle empty retrieval
    if not retrieved_chunks:
        return {
            "answer": "I couldn't find enough reliable information to answer that question.",
            "sources": []
        }

    # Prepare context and source mapping
    context_parts = []
    source_mapping = {}

    for index, chunk in enumerate(retrieved_chunks, start=1):

        source_id = f"S{index}"
        metadata = chunk["metadata"]
        source_url = metadata.get("url")

        context_parts.append(
            f"""
            Source ID: {source_id}

            Title: {metadata.get("title")}
            URL: {source_url}
            Author: {metadata.get("author")}
            Publication Date: {metadata.get("date")}
            Content Type: {metadata.get("content_type")}

            Content:
            {chunk["content"]}
            """
        )

        # Store source details against source ID
        source_mapping[source_id] = {
            "title": metadata.get("title"),
            "url": source_url,
            "date": metadata.get("date")
        }

    # Combine retrieved context
    context = "\n\n".join(context_parts)

    # Generate structured answer
    response = answer_chain.invoke({
        "question": question,
        "context": context
    })

    # Map LLM-selected source IDs to source details
    used_sources = []

    for source_id in response.source_ids:

        if source_id in source_mapping:
            source = source_mapping[source_id]

            # Avoid duplicate URLs
            if source["url"] and not any(
                item["url"] == source["url"]
                for item in used_sources
            ):
                used_sources.append(source)

    return {
        "answer": response.answer,
        "sources": used_sources,
        "source_ids": response.source_ids
    }
