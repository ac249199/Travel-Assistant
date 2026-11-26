from app.schemas.rag_answer_schema import RAGAnswer

test_response = RAGAnswer(
    answer="You can enjoy a peaceful morning boat ride in Varanasi.",
    source_ids=["S1", "S2"]
)

print(test_response)
print(test_response.model_dump())