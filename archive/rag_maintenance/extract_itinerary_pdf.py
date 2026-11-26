import pymupdf
from pathlib import Path


# PDF file path
pdf_path = Path("data/itineraries/Banaras_Itineraries.pdf")

# Open PDF
doc = pymupdf.open(pdf_path)

# Extract text from all pages
extracted_text = ""

for page_number, page in enumerate(doc, start=1):

    page_text = page.get_text()

    extracted_text += f"\n\n--- Page {page_number} ---\n\n"
    extracted_text += page_text


# Save extracted text
output_path = Path("data/itineraries/extracted_itinerary.txt")

output_path.write_text(
    extracted_text,
    encoding="utf-8"
)

doc.close()

print("PDF extraction completed!")
print("Total pages:", len(pymupdf.open(pdf_path)))
print("Extracted text saved at:", output_path)