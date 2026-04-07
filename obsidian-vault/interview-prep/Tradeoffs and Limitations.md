# Tradeoffs and Limitations

Knowing the limitations of your system shows maturity. Interviewers value honest self-assessment.

## Current Limitations

### 1. No Monitoring or Alerting

**Problem:** If the daily pipeline fails, there's no notification. You'd only notice by checking the GitHub Actions dashboard or the database manually.

**What you'd add:**
- Slack/Discord webhook on workflow failure
- Health check endpoint that verifies the latest brief is from today
- Dead man's switch (alert if no brief for 2+ business days)

### 2. No Automated Testing

**Problem:** No unit tests, integration tests, or data quality checks.

**What you'd add:**
- Unit tests for spread calculations and data sanitization
- Integration tests that verify API responses parse correctly
- Data quality assertions (e.g., yields should be 0-20%, not -500%)
- Snapshot tests for the prompt template

### 3. NewsAPI 30-Day Limitation

**Problem:** NewsAPI's free tier only returns articles from the last 30 days. Backfilling historical dates produces briefs without news context.

**Mitigation:** The prompt handles missing data gracefully, but the briefs are less comprehensive.

**Alternative:** Use a different news source (GDELT, media APIs with longer retention) or cache articles as they're collected.

### 4. No Rate Limiting or Retry Logic on All APIs

**Problem:** If an API rate-limits or has a transient failure, that data source is lost for the day.

**What you'd add:**
- `tenacity` retry decorators on all API calls (the library is already in requirements)
- Exponential backoff to avoid hammering failing services
- Circuit breaker pattern for persistent failures

### 5. Single Point of Failure: Gemini

**Problem:** If Google's Gemini API is down, no brief is generated.

**What you'd add:**
- Fallback to a secondary LLM (OpenAI, Anthropic)
- Or: store raw data and generate the brief later when the API recovers
- Health check before synthesis to fail fast

### 6. No User Authentication

**Problem:** The Next.js app and Supabase data are either public or protected only by Supabase RLS.

**What you'd add for production:**
- Supabase Auth with email/OAuth login
- Row Level Security policies on `daily_briefs`
- Protected API routes in Next.js

### 7. No Chunking in RAG

**Problem:** Each brief is embedded as a single ~1000-word document. If briefs grow longer, embedding quality degrades (the vector must compress more information).

**What you'd add:**
- Split briefs by section (Market Summary, Fixed Income, etc.)
- Embed each section independently
- Return the most relevant *section*, not the whole brief

## Architectural Tradeoffs

### JSONB vs Normalized (Chose JSONB)

**What you gave up:**
- SQL aggregation across days (e.g., "average VIX this month")
- Indexing on specific fields (e.g., "all days where S&P > 5000")
- Data validation at the schema level

**What you gained:**
- Simplicity (one table, one query per day)
- Schema flexibility (add data sources without migrations)
- Natural document-oriented storage for a write-once pattern

### Cron vs Event-Driven (Chose Cron)

**What you gave up:**
- Immediate processing when data becomes available
- Flexibility for non-standard market days

**What you gained:**
- Extreme simplicity (one cron line)
- Predictable execution time
- No event infrastructure to maintain

### Single DB vs Polyglot Persistence (Chose Single)

**What you gave up:**
- Optimized vector search performance at scale
- Separate scaling for vector vs relational workloads

**What you gained:**
- No data sync issues
- One connection string
- Atomic operations (text + embedding stored together)
- Lower operational complexity

## How to Discuss These in Interviews

**Framework:** "I chose X because Y, and I'm aware that Z is a limitation. If I were taking this to production / scaling it, I'd address that by..."

**Example:**
> "I use a single Supabase database for both relational data and vector search. The tradeoff is that a dedicated vector database would perform better at millions of documents, but for my current scale of hundreds of briefs, pgvector is more than sufficient and eliminates the complexity of syncing data between two systems. If I needed to scale to millions of documents, I'd migrate the vector search to Pinecone or Qdrant while keeping the structured data in PostgreSQL."

**Key principle:** Never present limitations as excuses. Present them as conscious choices with a clear path to improvement.

## Related Notes
- [[Key Design Decisions]] - The positive framing
- [[Common Questions]] - "What would you improve?"
- [[System Overview]] - The architecture being assessed
