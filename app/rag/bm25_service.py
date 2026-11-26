
import json
import re

from rank_bm25 import BM25Okapi


# 1. Load all chunks
with open(
    "data/varanasi_chunks.json",
    "r",
    encoding="utf-8"
) as file:
    data = json.load(file)

chunks = data["chunks"]


# 2. Tokenization function
def tokenize(text):

    return re.findall(
        r"\b\w+\b",
        text.lower()
    )


# 3. Prepare tokenized corpus
tokenized_corpus = [
    tokenize(chunk["content"])
    for chunk in chunks
]


# 4. Build BM25 index
bm25 = BM25Okapi(tokenized_corpus)


# 5. Search function
def search_bm25(query, n_results=5):

    tokenized_query = tokenize(query)

    scores = bm25.get_scores(tokenized_query)

    ranked_indices = scores.argsort()[::-1][:n_results]

    results = []

    for index in ranked_indices:

        results.append({
            "chunk_id": chunks[index]["chunk_id"],
            "content": chunks[index]["content"],
            "metadata": chunks[index]["metadata"],
            "score": float(scores[index])
        })

    return results
