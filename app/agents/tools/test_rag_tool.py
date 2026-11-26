
from app.agents.tools.rag_tool import varanasi_knowledge_search


query = "Tell me about Assi Ghat."

result = varanasi_knowledge_search.invoke({
    "query": query
})

print("\n========== RAG TOOL TEST ==========")

print("\nANSWER:")
print(result["answer"])

print("\nSOURCES:")
for source in result["sources"]:
    print(source["title"])
    print(source["url"])
