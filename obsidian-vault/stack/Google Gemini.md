# Google Gemini

## Overview

Google Gemini is Google's family of multimodal large language models. This project uses two Gemini capabilities:

1. **Text Generation** - Gemini 2.5-Flash for writing newsletter briefs
2. **Embeddings** - text-embedding-004 for creating vector representations

## Models Used

### Gemini 2.5-Flash (Text Generation)

- **Purpose:** Generates the PM Market Brief from raw data
- **Context window:** 1M tokens
- **Strengths:** Fast, cost-effective, good at structured summarization
- **Cost:** Significantly cheaper than Gemini Pro/Ultra
- **Latency:** ~5-15 seconds for a ~1000-word brief

**Why Flash and not Pro?**
- The task is *structured summarization*, not complex reasoning
- Flash is 10x+ cheaper per token
- Speed matters for a daily automated pipeline
- Quality difference is minimal for this use case

### text-embedding-004 (Embeddings)

- **Purpose:** Converts newsletter text into 768-dimensional vectors
- **Output dimensions:** 768
- **Use case:** Optimized for retrieval tasks (finding similar documents)
- **Task type:** Can specify `RETRIEVAL_DOCUMENT` or `RETRIEVAL_QUERY`

## API Usage

### Text Generation

```python
from google import genai

client = genai.Client(api_key=os.getenv("GOOGLE_KEY"))

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt  # String with market data + instructions
)

text = response.text
```

### Embedding Creation

```python
response = client.models.embed_content(
    model="text-embedding-004",
    contents=newsletter_text
)

embedding = response.embeddings[0].values  # List[float], length 768
```

## Two API Keys

The project uses **two separate Google API keys**:
- `GOOGLE_KEY` - For newsletter generation
- `RAG_BOT_KEY` - For RAG query answering

**Why?** Separation of concerns and rate limiting. The daily pipeline and the interactive RAG bot have different usage patterns. Separate keys mean:
- Independent rate limits
- Independent billing tracking
- Can revoke one without affecting the other

## Gemini vs Other LLMs

| Feature | Gemini | OpenAI GPT | Anthropic Claude |
|---------|--------|-----------|-----------------|
| Embedding + Generation | Same platform | Same platform | No embeddings |
| Free tier | Yes (generous) | Limited | Limited |
| Speed (Flash) | Very fast | GPT-4o-mini comparable | Haiku comparable |
| Context window | 1M tokens | 128K (GPT-4o) | 200K (Claude) |

**Why Gemini for this project?**
1. Both generation and embeddings from one provider (simpler integration)
2. Generous free tier for development
3. Flash model hits the quality/cost sweet spot
4. `google-genai` SDK is clean and simple

## Related Notes
- [[AI Synthesis Pipeline]] - How Gemini generates briefs
- [[Vector Embeddings]] - What embeddings are and how they work
- [[RAG System]] - How embeddings power search
- [[Prompt Engineering]] - How the generation prompt is structured
