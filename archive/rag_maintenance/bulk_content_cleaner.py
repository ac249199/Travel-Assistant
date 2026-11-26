import json
from app.rag.content_cleaner import clean_content


# 1. Read the original documents
with open(
    "data/varanasi_documents.json",
    "r",
    encoding="utf-8"
) as file:
    data = json.load(file)


# 2. Process every document
documents = data["documents"]

for document in documents:

    original_content = document.get("content", "")

    cleaned_content = clean_content(original_content)

    # Add a new field; preserve the original content
    document["cleaned_content"] = cleaned_content


# 3. Prepare the output
cleaned_data = {
    "total_urls": data["total_urls"],
    "successful_extractions": data["successful_extractions"],
    "failed_extractions": data["failed_extractions"],
    "documents": documents,
    "failed_urls": data["failed_urls"]
}


# 4. Save to a separate JSON file
with open(
    "data/varanasi_cleaned_documents.json",
    "w",
    encoding="utf-8"
) as file:
    json.dump(
        cleaned_data,
        file,
        ensure_ascii=False,
        indent=4
    )


print("Bulk content cleaning completed!")
print("Total documents processed:", len(documents))
print("Output saved to data/varanasi_cleaned_documents.json")