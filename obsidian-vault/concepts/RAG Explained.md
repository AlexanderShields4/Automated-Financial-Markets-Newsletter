# RAG Explained

## Retrieval-Augmented Generation (RAG)

RAG is a technique that **grounds LLM responses in your own data** by retrieving relevant documents before generating an answer.

## The Problem RAG Solves

LLMs have two fundamental limitations:
1. **Knowledge cutoff** - They don't know about events after their training date
2. **No access to private data** - They can't see your database, documents, or proprietary information

**Without RAG:**
> User: "What happened to Treasury yields last Tuesday?"
> LLM: "I don't have access to real-time market data..." ❌

**With RAG:**
> User: "What happened to Treasury yields last Tuesday?"
> System: *retrieves Tuesday's brief from database*
> LLM: "Based on last Tuesday's market brief, the 10-year Treasury yield rose 8bps to 4.32%, driven by..." ✅

## How RAG Works

### The Three Steps

```
┌─────────────┐     ┌──────────────┐     ┌────────────────┐
│  1. RETRIEVE │ ──▶ │  2. AUGMENT  │ ──▶ │  3. GENERATE   │
│  Find relevant│     │  Add to prompt│     │  LLM answers   │
│  documents    │     │  as context   │     │  with context   │
└─────────────┘     └──────────────┘     └────────────────┘
```

### Step 1: Retrieve

Convert the user's question into an embedding, then search for similar document embeddings:

```python
# Embed the question
query_vector = embed("What happened to oil last week?")

# Find similar documents
matches = vector_search(query_vector, threshold=0.5, top_k=5)
# Returns: [Brief from Mon, Brief from Tue, Brief from Wed, ...]
```

### Step 2: Augment

Inject the retrieved documents into the LLM prompt as context:

```python
prompt = f"""
You are a financial markets analyst. Use ONLY the following market briefs
to answer the question. If the information isn't in the briefs, say so.

MARKET BRIEFS:
{brief_1_text}
{brief_2_text}
{brief_3_text}

QUESTION: {user_question}
"""
```

### Step 3: Generate

The LLM reads the context and generates a grounded answer:

```python
response = gemini.generate_content(prompt)
# "Based on the market briefs from last week, WTI crude fell 3.2% from
#  $78.45 to $75.93, driven by increased OPEC+ supply concerns..."
```

## Why RAG Over Fine-Tuning?

| | RAG | Fine-Tuning |
|---|---|---|
| **Data freshness** | Real-time (just add to DB) | Requires retraining |
| **Cost** | Cheap (API calls only) | Expensive (GPU training) |
| **Transparency** | Can show sources | Black box |
| **Accuracy** | Cites specific data | May hallucinate details |
| **Setup complexity** | Moderate | High |
| **Best for** | Factual Q&A over documents | Changing model behavior/style |

For this project, RAG is the clear choice because:
- New briefs are added daily (fine-tuning can't keep up)
- Answers must reference specific dates and numbers (grounding)
- The dataset is small enough for simple retrieval
- We want to cite which briefs informed the answer

## Why RAG Over Just Searching?

Why not just return the matched briefs directly?

Because RAG adds an **intelligence layer**:
- **Synthesis** - Combines information across multiple briefs
- **Interpretation** - Explains trends, not just data points
- **Natural language** - Answers in conversational prose
- **Reasoning** - Can compare, contrast, and draw conclusions

## RAG Architecture Patterns

### Naive RAG (What This Project Uses)
```
Query → Embed → Search → Stuff into prompt → Generate
```
Simple and effective for small document sets.

### Advanced RAG (Future improvements)
- **Query rewriting** - Rephrase the query for better retrieval
- **Hybrid search** - Combine vector + keyword search
- **Re-ranking** - Use a cross-encoder to re-rank results
- **Chunking** - Split documents into smaller pieces for more precise retrieval

### This Project's Approach

Each brief is treated as a **single document** (no chunking). This works because:
- Briefs are ~1000 words (small enough for one embedding)
- The whole brief is contextually coherent
- No risk of splitting a topic across chunks

If briefs were 10,000+ words, you'd want to chunk them.

## Common Interview Questions

**Q: What's the difference between RAG and fine-tuning?**
> RAG retrieves relevant context at query time and passes it to the LLM. Fine-tuning permanently modifies the model's weights. RAG is better for factual, up-to-date information; fine-tuning is better for changing the model's behavior or style.

**Q: How do you handle hallucination in RAG?**
> 1. Set a similarity threshold (0.5) to avoid retrieving irrelevant docs
> 2. Instruct the LLM to only use provided context
> 3. Include source dates so users can verify
> 4. If no relevant docs are found, say "I don't have data on that"

**Q: What would you improve about this RAG system?**
> 1. Add hybrid search (vector + keyword) for better recall
> 2. Implement re-ranking with a cross-encoder
> 3. Add metadata filtering (e.g., date range constraints)
> 4. Chunk briefs by section for more precise retrieval
> 5. Add evaluation metrics (relevance, faithfulness)

## Related Notes
- [[RAG System]] - Implementation in this project
- [[Vector Embeddings]] - The retrieval mechanism
- [[Cosine Similarity]] - How matches are scored
- [[Google Gemini]] - The generation model
