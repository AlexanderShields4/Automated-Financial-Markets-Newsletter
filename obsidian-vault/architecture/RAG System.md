# RAG System

## What is RAG?

**Retrieval-Augmented Generation** - instead of relying solely on an LLM's training data, you first *retrieve* relevant documents from your own database, then feed them as context to the LLM for generation.

> See [[RAG Explained]] for the full conceptual deep dive.

## Implementation in This Project

The RAG system is implemented in `rag_engine.py` and powers the "Market Chat" feature in the Streamlit dashboard.

### Architecture

```
User Question: "What happened to oil prices last week?"
         │
         ▼
┌─────────────────────────┐
│  1. EMBED THE QUESTION  │
│  Google Embedding-001    │
│  → 768-d vector         │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│  2. VECTOR SEARCH       │
│  match_daily_briefs()   │
│  Cosine similarity      │
│  Top 5 matches          │
│  Threshold: 0.5         │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│  3. BUILD CONTEXT       │
│  Concatenate matched    │
│  briefs with dates      │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│  4. GENERATE ANSWER     │
│  Google Gemini           │
│  System prompt +        │
│  Retrieved context +    │
│  User question          │
└────────────┬────────────┘
             │
             ▼
    Contextual Answer
```

### Code Walkthrough

```python
# rag_engine.py - Simplified flow

class MarketRAG:
    def __init__(self):
        self.supabase = create_client(url, key)
        self.client = genai.Client(api_key=rag_bot_key)

    def get_relevant_briefs(self, query: str, match_count=5):
        # Step 1: Embed the query
        embed_response = self.client.models.embed_content(
            model="text-embedding-004",
            contents=query
        )
        query_embedding = embed_response.embeddings[0].values

        # Step 2: Vector search via RPC
        result = self.supabase.rpc("match_daily_briefs", {
            "query_embedding": query_embedding,
            "match_threshold": 0.5,
            "match_count": match_count
        }).execute()

        return result.data

    def ask(self, question: str):
        # Step 2: Get relevant briefs
        briefs = self.get_relevant_briefs(question)

        # Step 3: Build context
        context = "\n\n".join([
            f"Brief from {b['date']}:\n{b['full_text']}"
            for b in briefs
        ])

        # Step 4: Generate answer
        prompt = f"""Based on these market briefs:
        {context}

        Answer this question: {question}"""

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text
```

### Key Design Choices

**Match threshold: 0.5**
- Below 0.5 similarity, results are likely irrelevant
- Too high (e.g., 0.8) would miss related but not identical topics
- 0.5 is a common starting point; could be tuned with evaluation data

**Match count: 5**
- Balances context richness with token budget
- 5 briefs × ~1000 words = ~5000 words of context
- Well within Gemini's context window

**Same embedding model for queries and documents**
- Critical: the query embedding must be from the same model as the document embeddings
- Different models produce incompatible vector spaces

### Why Not Just Search Keywords?

| Keyword Search | Semantic/Vector Search |
|---|---|
| "oil prices" only matches "oil prices" | "What happened with crude?" matches briefs about oil |
| Exact match required | Understands synonyms and related concepts |
| Fast, simple | Slightly slower, more complex |
| Misses paraphrases | Catches semantic similarity |
| No ranking by relevance | Natural relevance ranking via similarity scores |

## LangChain Integration

The project uses LangChain for RAG orchestration:
- `langchain-google-genai` - Google model integrations
- `langchain-core` - Base abstractions (prompts, chains)
- `langchain-community` - Community integrations

LangChain provides abstractions for:
- **Document loaders** - Standardized document format
- **Embeddings** - Uniform interface for embedding models
- **Vector stores** - Pluggable vector database backends
- **Chains** - Composable pipelines (retrieve → generate)

## Related Notes
- [[RAG Explained]] - Conceptual deep dive
- [[Vector Embeddings]] - How text becomes vectors
- [[Database Design]] - The `match_daily_briefs` function
- [[Cosine Similarity]] - How matches are scored
- [[Google Gemini]] - The models used
