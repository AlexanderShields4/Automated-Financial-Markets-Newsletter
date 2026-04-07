# HNSW Index

## What is HNSW?

**Hierarchical Navigable Small World** - an algorithm for **approximate nearest neighbor (ANN) search** in high-dimensional spaces. It's the index type used in this project for fast vector similarity search.

## The Problem It Solves

Given a query vector (768 dimensions), find the most similar vectors in the database.

**Brute force approach:** Compare the query to every single vector. O(n) comparisons.
- 100 vectors: instant
- 1,000 vectors: fast
- 1,000,000 vectors: slow (seconds)
- 1,000,000,000 vectors: impractical

**HNSW approach:** Build a graph structure that enables finding approximate nearest neighbors in O(log n) time.

## How HNSW Works

### Intuition: A Multi-Layer Map

Imagine you're in New York and need to find the closest coffee shop:

**Layer 0 (detailed):** Shows every single building
**Layer 1 (neighborhoods):** Shows just major landmarks per block
**Layer 2 (city):** Shows just borough names

You'd start at Layer 2 (city view), identify the right borough, zoom into Layer 1 (neighborhood), find the right block, then zoom into Layer 0 to find the exact building.

HNSW does the same with vectors:

```
Layer 2 (few nodes):    A -------- B -------- C
                                   |
Layer 1 (more nodes):   A -- D --- B -- E --- C -- F
                              |         |
Layer 0 (all nodes):    A D G H I B J E K C F L M N
                        ↑                     ↑
                        Start here             Find nearest
```

### The Algorithm

**Building the index:**
1. Each vector is assigned to layers probabilistically (higher layers = fewer nodes)
2. At each layer, the vector connects to its nearest neighbors
3. Result: a multi-layer graph where higher layers provide "highways" for fast navigation

**Searching:**
1. Start at the top layer with an entry point
2. Greedily move to the neighbor closest to the query
3. When no closer neighbor exists, drop to the next layer
4. Repeat until reaching Layer 0
5. Explore the local neighborhood at Layer 0 for final results

### Key Parameters

**`m` (max connections per node, default: 16)**
- Higher m = more connections = better recall, but more memory and slower builds
- 16 is a good default for most use cases

**`ef_construction` (search width during build, default: 64)**
- Higher = better index quality, slower build
- Only affects build time, not query time

**`ef_search` (search width during query)**
- Higher = better recall, slower queries
- Can be tuned at query time for accuracy/speed tradeoff

## HNSW in This Project

```sql
CREATE INDEX daily_briefs_embedding_idx
ON daily_briefs
USING hnsw (embedding vector_cosine_ops);
```

- `USING hnsw` - Use the HNSW algorithm
- `vector_cosine_ops` - Use [[Cosine Similarity]] as the distance metric
- Default parameters are used (m=16, ef_construction=64)

### Why Default Parameters Are Fine Here

The dataset is small (hundreds of briefs, not millions). With this size:
- Even brute force would be fast
- The index exists for correctness/API compatibility
- Default parameters provide excellent recall at this scale

## HNSW vs IVFFlat (The Other pgvector Index)

| | HNSW | IVFFlat |
|---|---|---|
| **Algorithm** | Multi-layer graph | Inverted file with clustering |
| **Build time** | Slower | Faster |
| **Query time** | Faster | Slower |
| **Recall** | Higher (>99%) | Lower (~95%) |
| **Memory** | 2-3x more | Less |
| **Updates** | Handles inserts well | Needs periodic retraining |
| **Best for** | Production, real-time search | Prototyping, batch processing |

**HNSW is better for this project** because:
- New briefs are inserted daily (HNSW handles inserts without retraining)
- High recall is important (don't miss relevant briefs)
- Dataset is small, so memory overhead is negligible

## "Approximate" - What Does That Mean?

HNSW doesn't guarantee finding the absolute nearest neighbor. It finds an **approximate** nearest neighbor with very high probability (>99% recall with default settings).

**Why is approximate OK?**
- For RAG, getting the top 5 most similar briefs is sufficient
- Missing the #3 most similar brief and getting the #7 instead doesn't materially affect answer quality
- The speed gain is worth the tiny accuracy tradeoff

## Interview Talking Points

- "HNSW builds a multi-layer navigable graph that enables O(log n) approximate nearest neighbor search"
- "It's the gold standard for vector search - used by Pinecone, Weaviate, and pgvector"
- "We use it with cosine distance in PostgreSQL via the pgvector extension"
- "For our dataset size, even brute force would work, but HNSW gives us correct semantics and will scale if the dataset grows"

## Related Notes
- [[Vector Embeddings]] - What's being indexed
- [[Cosine Similarity]] - The distance metric
- [[Database Design]] - Where the index lives
- [[Supabase]] - The platform providing pgvector
