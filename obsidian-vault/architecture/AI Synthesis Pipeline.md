# AI Synthesis Pipeline

## Overview

After data collection, the system uses **Google Gemini 2.5-Flash** to transform raw market data into a professional PM Market Brief. This is a two-step process: text generation, then embedding creation.

## Step 1: Text Generation

### The Prompt

The prompt is ~1800 words and follows a structured format:

```
You are a financial markets analyst writing a PM Market Brief...

Here is today's data:
- Treasury yields: [data]
- Yield spreads: [data]
- Index performance: [data]
- Stock prices: [data]
- Economic indicators: [data]
- News headlines: [data]

Structure your brief as:
1. Market Summary (indices, VIX, sentiment)
2. Fixed Income & Macro (spreads, dollar)
3. Commodities & Energy (oil, gold)
4. Economic Data (releases, calendar)
5. Key Takeaways & Outlook
```

### Key Prompt Design Choices

1. **Plain text output** - Explicitly requests no markdown formatting. This prevents rendering issues across different display contexts.
2. **Professional tone** - Targets the voice of a portfolio manager writing for institutional clients
3. **Section structure** - Ensures consistent output format that can be reliably parsed/displayed
4. **Data-driven** - The prompt forces the model to reference specific numbers from the provided data, reducing hallucination

> See [[Prompt Engineering]] for the general principles behind this approach.

### Model Choice: Gemini 2.5-Flash

**Why Flash over Pro?**
- **Cost efficiency** - This runs daily, costs add up. Flash is significantly cheaper.
- **Speed** - Flash generates faster, important for a pipeline that runs on schedule
- **Sufficient quality** - The task is structured summarization, not creative reasoning. Flash handles this well.
- **Context window** - All the data fits comfortably in Flash's context

### Generation Code

```python
from google import genai

client = genai.Client(api_key=os.getenv("GOOGLE_KEY"))

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt
)

newsletter_text = response.text
```

## Step 2: Embedding Generation

After generating the text, the system creates a **768-dimensional vector embedding** of the full newsletter text.

```python
embed_response = client.models.embed_content(
    model="text-embedding-004",
    contents=newsletter_text
)

embedding = embed_response.embeddings[0].values  # List of 768 floats
```

### Why Embed the Newsletter?

The embedding enables **semantic search** over historical briefs. Instead of keyword matching ("show me briefs mentioning oil"), users can ask natural questions ("What happened when crude prices spiked last month?") and the system finds semantically relevant briefs.

> See [[Vector Embeddings]] and [[RAG Explained]] for deep dives on these concepts.

### Model: text-embedding-004

- **Dimensions:** 768
- **Why this model?** It's Google's latest embedding model, optimized for retrieval tasks. The 768 dimensions provide a good balance of expressiveness and storage efficiency.

## Step 3: Data Sanitization

Before storing, the system cleans the structured data:

```python
import json
import math

def clean_for_json(obj):
    """Replace NaN/Inf with None for JSON compatibility"""
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
    if isinstance(obj, dict):
        return {k: clean_for_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [clean_for_json(i) for i in obj]
    return obj
```

**Why?** Financial APIs sometimes return `NaN` or `Infinity` for missing/computed values. JSON doesn't support these, and PostgreSQL JSONB will reject them.

## Step 4: Upsert to Supabase

```python
supabase.table("daily_briefs").upsert({
    "date": target_date,
    "full_text": newsletter_text,
    "structured_data": clean_structured_data,
    "embedding": embedding
}).execute()
```

**Upsert vs Insert:** Using upsert (insert or update on conflict) means re-running the pipeline for an existing date will update the record rather than failing with a unique constraint violation. This is important for the backfill workflow.

## Pipeline Timing

The full pipeline from collection to storage typically completes in **30-60 seconds**:
- Data collection: ~10-20s (API calls in sequence)
- Gemini generation: ~5-15s
- Embedding: ~1-2s
- Database write: ~1-2s

## Related Notes
- [[Data Collection Pipeline]] - What feeds into this step
- [[Database Design]] - Where the output is stored
- [[Google Gemini]] - More about the AI platform
- [[Prompt Engineering]] - Prompt design principles
- [[Vector Embeddings]] - How embeddings work
