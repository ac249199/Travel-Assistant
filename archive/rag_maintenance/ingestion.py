
import json
import time
from pathlib import Path

from app.rag.website_loader import load_website


INPUT_FILE = Path("data/varanasi_urls.json")
OUTPUT_FILE = Path("data/varanasi_documents.json")

REQUEST_DELAY = 2


def run_ingestion():

    print("\nStarting bulk website ingestion...\n")

    # Check whether input file exists
    if not INPUT_FILE.exists():
        print("URL file not found:", INPUT_FILE)
        return

    # Load candidate URLs
    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    urls = data["relevant_urls"]

    print("Total URLs to process:", len(urls))

    documents = []
    failed_urls = []

    # Process URLs one by one
    for index, url in enumerate(urls, start=1):

        print(f"\nProcessing {index}/{len(urls)}")

        document = load_website(url)

        if document and document.get("content"):

            documents.append(document)
            print("Successfully extracted:", document["title"])

        else:

            failed_urls.append(url)
            print("Extraction failed:", url)

        # Avoid sending requests too quickly
        if index < len(urls):
            time.sleep(REQUEST_DELAY)

    # Save extracted documents
    output = {
        "total_urls": len(urls),
        "successful_extractions": len(documents),
        "failed_extractions": len(failed_urls),
        "documents": documents,
        "failed_urls": failed_urls
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(output, file, indent=4, ensure_ascii=False)

    print("\nIngestion completed!")
    print("Successful:", len(documents))
    print("Failed:", len(failed_urls))
    print("Saved to:", OUTPUT_FILE)


if __name__ == "__main__":
    run_ingestion()
