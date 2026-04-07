# Prompt Engineering

## What is Prompt Engineering?

The practice of designing and structuring inputs to LLMs to get reliable, high-quality outputs. In this project, the prompt is what turns raw market data into a professional newsletter.

## Prompt Structure in This Project

The newsletter generation prompt follows a proven pattern:

```
┌─────────────────────────────┐
│ 1. ROLE ASSIGNMENT          │  "You are a financial markets analyst..."
├─────────────────────────────┤
│ 2. TASK DESCRIPTION         │  "Write a PM Market Brief..."
├─────────────────────────────┤
│ 3. DATA INJECTION           │  All collected market data
├─────────────────────────────┤
│ 4. OUTPUT STRUCTURE         │  Requested sections and format
├─────────────────────────────┤
│ 5. CONSTRAINTS              │  "No markdown", "Plain text only"
└─────────────────────────────┘
```

### 1. Role Assignment

```
You are a financial markets analyst writing a PM Market Brief
for institutional portfolio managers.
```

**Why?** Setting a role:
- Establishes expertise level and vocabulary
- Sets the appropriate tone (professional, data-driven)
- Reduces the need for explicit style instructions

### 2. Task Description

```
Analyze all the provided market data and synthesize it into
a comprehensive daily brief. Focus on what matters to a PM
making allocation decisions.
```

### 3. Data Injection

```
Here is today's data:

Treasury Yields:
DGS2: 4.32% (prev: 4.28%)
DGS10: 4.56% (prev: 4.51%)
...

Key Spreads:
10Y-2Y: 0.24% (prev: 0.23%)
...

Market Indices:
S&P 500: 5,234.18 (+1.2%)
...

News Headlines:
- "Fed signals patience on rate cuts..."
- "Oil prices rise on Middle East tensions..."
...
```

**Key principle:** Provide data in a clean, structured format. The model processes structured input better than wall-of-text.

### 4. Output Structure

```
Structure your brief in these sections:
1. Market Summary - Indices, VIX, overall sentiment
2. Fixed Income & Macro - Spreads, dollar, rate expectations
3. Commodities & Energy - Oil, gold, energy trends
4. Economic Data - Recent releases, upcoming calendar
5. Key Takeaways & Outlook - 3-5 bullet points
```

**Why explicit sections?**
- Ensures consistent output across daily briefs
- Makes the output parseable/displayable
- Prevents the model from focusing only on "exciting" topics
- Guarantees coverage of all asset classes

### 5. Constraints

```
Important:
- Write in plain text only. Do NOT use markdown formatting.
- Do NOT use asterisks, hashes, or bullet point characters.
- Keep the brief between 800-1200 words.
- Reference specific numbers from the provided data.
- If data is missing for a section, acknowledge it briefly and move on.
```

**Why plain text?** The brief is displayed in multiple contexts (Streamlit, Next.js, potential email). Markdown formatting creates rendering inconsistencies. Plain text is universally compatible.

## Key Prompt Engineering Principles

### 1. Be Specific, Not Vague

```
❌ "Write a good market summary"
✅ "Write a 1000-word PM Market Brief covering indices, fixed income,
    commodities, and economic data, targeting institutional portfolio managers"
```

### 2. Show, Don't Tell

Instead of saying "be professional," assign a role that implies professionalism.

### 3. Structured Input → Structured Output

Clean, labeled data sections produce clean, labeled output sections.

### 4. Constrain the Output Format

Explicit formatting instructions prevent the model from making its own formatting choices.

### 5. Handle Missing Data

```
"If data is missing for a section, acknowledge it briefly and move on."
```

The pipeline may have partial failures. The prompt must account for this.

### 6. Ground in Provided Data

```
"Reference specific numbers from the provided data."
```

This reduces hallucination by forcing the model to cite the data you gave it.

## RAG Prompt (for Q&A)

The RAG system uses a different prompt pattern:

```
Based on the following market briefs from our database:

[Brief from 2024-01-15]:
{full_text}

[Brief from 2024-01-16]:
{full_text}

Answer the following question using ONLY information from these briefs.
If the answer isn't in the briefs, say "I don't have data on that."

Question: {user_question}
```

**Key differences from generation prompt:**
- Explicitly limits the model to provided context ("ONLY information from these briefs")
- Includes a fallback instruction for when data is missing
- Sources are dated so the model can reference specific days

## Interview Talking Points

- "The prompt assigns a professional analyst role, provides structured data, requests a specific output format, and includes constraints to prevent formatting issues"
- "We explicitly tell the model to reference provided numbers to reduce hallucination"
- "The prompt handles partial data gracefully - if a data source fails, the model works with what's available"
- "For RAG, we constrain the model to only use retrieved context, preventing it from fabricating market data"

## Related Notes
- [[AI Synthesis Pipeline]] - Where this prompt is used
- [[RAG System]] - The RAG prompt pattern
- [[Google Gemini]] - The model executing the prompt
