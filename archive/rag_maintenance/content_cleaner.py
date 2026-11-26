
import re


def clean_content(text):

    if not text:
        return ""

    # 1. Normalize whitespace
    text = text.replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)

    lines = text.splitlines()
    cleaned_lines = []

    # 2. Remove standalone promotional CTA lines
    cta_pattern = re.compile(
        r"^\s*(book|reserve|enquire|subscribe)\b",
        re.IGNORECASE
    )

    for line in lines:

        line = line.strip()

        if not line:
            continue

        # Remove lines beginning with promotional CTAs
        if cta_pattern.match(line):
            continue

        cleaned_lines.append(line)

    # 3. Join cleaned lines
    cleaned_text = "\n".join(cleaned_lines)

    # 4. Remove excessive blank lines
    cleaned_text = re.sub(r"\n{3,}", "\n\n", cleaned_text)

    return cleaned_text.strip()
