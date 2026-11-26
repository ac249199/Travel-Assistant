
import json
from langchain_text_splitters import RecursiveCharacterTextSplitter


# 1. Configure the text splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=150,
    separators=["\n\n", "\n", ". ", " ", ""]
)


# 2. Load cleaned documents
with open(
    "data/varanasi_cleaned_documents.json",
    "r",
    encoding="utf-8"
) as file:
    data = json.load(file)


documents = data["documents"]

all_chunks = []


# 3. Process each document
for document in documents:

    text = document.get("cleaned_content", "")

    # Split the document into chunks
    chunks = text_splitter.split_text(text)

    # 4. Attach metadata to every chunk
    for index, chunk in enumerate(chunks):

        chunk_data = {
            "chunk_id": f"{len(all_chunks) + 1}",
            "chunk_index": index,
            "content": chunk,

            "metadata": {
                "title": document.get("title"),
                "url": document.get("url"),
                "author": document.get("author"),
                "date": document.get("date"),
                "content_type": document.get("content_type")
            }
        }

        all_chunks.append(chunk_data)


# 5. Save all chunks
output_data = {
    "total_documents": len(documents),
    "total_chunks": len(all_chunks),
    "chunk_size": 800,
    "chunk_overlap": 150,
    "chunks": all_chunks
}

with open(
    "data/varanasi_chunks.json",
    "w",
    encoding="utf-8"
) as file:
    json.dump(
        output_data,
        file,
        ensure_ascii=False,
        indent=4
    )


print("\n========== CHUNKING COMPLETED ==========")
print("Total documents:", len(documents))
print("Total chunks generated:", len(all_chunks))
print("Output saved to data/varanasi_chunks.json")
