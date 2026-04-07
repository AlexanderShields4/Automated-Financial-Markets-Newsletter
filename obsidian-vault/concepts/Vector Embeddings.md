# Vector Embeddings

## What Are Embeddings?

An embedding is a **numerical representation of text** (or images, audio, etc.) as a list of floating-point numbers (a vector). The key property: **semantically similar text produces similar vectors**.

## Intuition

Imagine compressing the "meaning" of a sentence into a point in space:

```
"The stock market crashed today"     → [0.82, -0.15, 0.43, ...]
"Equities tumbled in heavy trading"  → [0.79, -0.18, 0.41, ...]  ← Similar!
"I like pizza"                       → [-0.32, 0.67, -0.11, ...] ← Very different
```

The first two sentences are about the same thing (market decline), so their vectors are close together in 768-dimensional space. "I like pizza" is unrelated, so its vector points in a completely different direction.

## How They're Created

A neural network (the embedding model) has been trained on massive text corpora to learn relationships between words and concepts. When you pass text through it:

```
Input text → Neural network → 768 floats
```

The model has learned that:
- "crash" and "tumble" appear in similar contexts → similar vectors
- "bull market" and "bear market" are related but opposite → nearby but different vectors
- "Federal Reserve" and "interest rates" are related → vectors in same region

## Dimensions

This project uses **768-dimensional** embeddings (from `text-embedding-004`).

**What does 768 dimensions mean?**
- Each number captures some aspect of meaning
- No single dimension maps to a human-interpretable concept
- More dimensions = more expressive (but more storage)
- Common sizes: 384, 768, 1024, 1536, 3072

**Storage math for this project:**
- 768 floats × 4 bytes = ~3KB per embedding
- 365 briefs/year × 3KB = ~1.1MB/year
- Trivial storage cost, even at scale

## Why Not Just Use Keywords?

| Keyword Matching | Embeddings |
|---|---|
| "oil prices" only matches "oil prices" | "crude petroleum cost" also matches |
| No understanding of meaning | Captures semantic similarity |
| Exact match or nothing | Graded similarity scores |
| Fast, simple | Requires model inference |
| Misses synonyms, paraphrases | Handles them naturally |

## How They're Used in This Project

### Document Embedding (at ingestion time)
```python
# Each newsletter brief is embedded once when created
embed_response = client.models.embed_content(
    model="text-embedding-004",
    contents=newsletter_text  # ~1000 words
)
embedding = embed_response.embeddings[0].values  # [float] × 768
```

### Query Embedding (at search time)
```python
# User's question is embedded with the SAME model
embed_response = client.models.embed_content(
    model="text-embedding-004",
    contents="What happened to oil last week?"
)
query_vector = embed_response.embeddings[0].values
```

### Similarity Search
```python
# Find briefs whose embeddings are closest to the query
results = supabase.rpc("match_daily_briefs", {
    "query_embedding": query_vector,
    "match_threshold": 0.5,
    "match_count": 5
})
```

> See [[Cosine Similarity]] for how "closest" is measured.

## Critical Rule: Same Model for Documents and Queries

You **must** use the same embedding model for both documents and queries. Different models produce different vector spaces - comparing vectors from different models is like comparing coordinates on different maps.

## Interview Talking Points

- "Embeddings convert text into numerical vectors where semantic similarity maps to geometric proximity"
- "We use 768-dimensional embeddings from Google's text-embedding-004 model"
- "The same model must be used for both document and query embeddings"
- "This enables semantic search - users can ask natural questions without exact keyword matches"
- "Stored in PostgreSQL using the pgvector extension, indexed with HNSW for fast retrieval"

## Related Notes
- [[Cosine Similarity]] - How similarity is measured
- [[HNSW Index]] - How the index makes search fast
- [[RAG Explained]] - How embeddings power the Q&A system
- [[Database Design]] - Where embeddings are stored
- [[Google Gemini]] - The embedding model provider
