from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
import json
import re


# Read extracted text
input_path = Path("data/itineraries/extracted_itinerary.txt")

text = input_path.read_text(encoding="utf-8")


# Remove standalone page markers
text = re.sub(r"--- Page \d+ ---", "", text)


# Initialize text splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1200,
    chunk_overlap=150,
    separators=["\n\n", "\n", ".", " ", ""]
)


# Split text into chunks
chunks = text_splitter.split_text(text)


# Save chunks
output_path = Path("data/itineraries/itinerary_chunks.json")

with open(output_path, "w", encoding="utf-8") as file:
    json.dump(chunks, file, ensure_ascii=False, indent=4)


print("Chunking completed!")
print("Total chunks:", len(chunks))

for i, chunk in enumerate(chunks):
    print(f"\nChunk {i+1}:")
    print(chunk)