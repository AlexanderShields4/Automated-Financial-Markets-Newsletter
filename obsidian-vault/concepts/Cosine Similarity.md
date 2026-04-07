# Cosine Similarity

## What is Cosine Similarity?

A measure of how similar two vectors are based on the **angle between them**, regardless of their magnitude (length).

```
similarity = cos(θ) = (A · B) / (||A|| × ||B||)
```

- **1.0** = identical direction (same meaning)
- **0.0** = perpendicular (unrelated)
- **-1.0** = opposite direction (opposite meaning)

## Visual Intuition

```
        ↑ B (similar to A)
       /
      / θ = small angle → high similarity
     /
    /
   A ──────────────→

        ↑ C (unrelated to A)
        │
        │  θ = 90° → similarity ≈ 0
        │
   A ──────────────→
```

## Why Cosine Over Euclidean Distance?

| | Cosine Similarity | Euclidean Distance |
|---|---|---|
| **Measures** | Direction (angle) | Absolute position |
| **Magnitude matters?** | No | Yes |
| **Range** | [-1, 1] | [0, ∞) |
| **Best for** | Text embeddings | Spatial data |

**Why cosine for text embeddings?**
Embedding models produce vectors where the **direction** encodes meaning and the **magnitude** can vary based on text length. Cosine similarity ignores magnitude, focusing purely on semantic direction.

Example:
- A 500-word brief about oil might have magnitude 12.3
- A 1000-word brief about oil might have magnitude 15.7
- Cosine similarity: ~0.95 (very similar - both about oil)
- Euclidean distance: 3.4 (seems different due to magnitude)

## In This Project

### pgvector Operator

```sql
-- <=> is the cosine DISTANCE operator (not similarity!)
-- distance = 1 - similarity

SELECT
    1 - (embedding <=> query_embedding) as similarity
FROM daily_briefs
ORDER BY embedding <=> query_embedding  -- Sort by distance (ascending)
LIMIT 5;
```

**Important distinction:**
- `<=>` returns **distance** (0 = identical, 2 = opposite)
- **similarity** = `1 - distance` (1 = identical, -1 = opposite)
- We filter on similarity > 0.5 threshold

### The Threshold: 0.5

```python
supabase.rpc("match_daily_briefs", {
    "match_threshold": 0.5,  # Only return results above this similarity
    ...
})
```

- **0.5** means "at least somewhat related"
- Below 0.5 = likely noise/irrelevant
- Above 0.8 = very closely related
- This threshold is tunable based on desired precision/recall

## The Math (Simplified)

For two vectors A = [a₁, a₂, ...] and B = [b₁, b₂, ...]:

```
Dot product:   A · B = a₁b₁ + a₂b₂ + ... + aₙbₙ
Magnitude:     ||A|| = √(a₁² + a₂² + ... + aₙ²)

Cosine sim = (a₁b₁ + a₂b₂ + ... + a₇₆₈b₇₆₈) / (||A|| × ||B||)
```

With 768 dimensions, this is 768 multiplications + additions. The HNSW index avoids doing this for every row.

## Interview Talking Points

- "We use cosine similarity because it measures semantic direction, ignoring text length differences"
- "pgvector's `<=>` operator computes cosine distance; we convert to similarity with `1 - distance`"
- "A threshold of 0.5 filters out noise while capturing semantically related briefs"
- "The HNSW index makes this O(log n) instead of computing similarity against every row"

## Related Notes
- [[Vector Embeddings]] - What's being compared
- [[HNSW Index]] - How the search is made fast
- [[Database Design]] - The `match_daily_briefs` function
- [[RAG System]] - Where similarity search is used
