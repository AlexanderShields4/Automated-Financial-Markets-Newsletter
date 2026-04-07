# Key Design Decisions

## Decision 1: Single Database for Everything

**Choice:** Supabase PostgreSQL with pgvector for relational data AND vector embeddings

**Alternatives considered:**
- PostgreSQL + Pinecone (separate vector DB)
- PostgreSQL + Weaviate
- MongoDB + Atlas Vector Search

**Why this choice:**
- Eliminates data synchronization between two databases
- One connection string, one SDK, one billing
- PostgreSQL's JSONB handles semi-structured market data well
- pgvector's HNSW is more than sufficient for hundreds of documents
- Supabase provides managed hosting, auto REST API, and client SDKs

**When you'd choose differently:**
- Millions of vectors → dedicated vector DB for better performance
- Complex vector operations (filtering + search) → Weaviate/Qdrant
- Multi-tenant SaaS → separate vector indexes per tenant

---

## Decision 2: Gemini Flash Over Frontier Models

**Choice:** Gemini 2.5-Flash for generation, text-embedding-004 for embeddings

**Alternatives considered:**
- GPT-4o / GPT-4o-mini
- Claude 3.5 Sonnet
- Gemini Pro

**Why this choice:**
- Task is structured summarization, not complex reasoning
- Cost is ~10x lower than frontier models
- Both generation and embedding from one provider (single SDK)
- Generous free tier for development
- Quality is excellent for data-to-text transformation

**When you'd choose differently:**
- Complex multi-step reasoning → Gemini Pro or Claude
- Need function calling / tool use → GPT-4o
- Sensitive financial advice → larger model with better calibration

---

## Decision 3: JSONB Over Normalized Tables

**Choice:** Store all daily market data in a single JSONB column

**Alternatives considered:**
- Normalized tables: `yields`, `spreads`, `stocks`, `indices`, `news`
- Separate time-series database (TimescaleDB, InfluxDB)

**Why this choice:**
- Data is always consumed as a unit (one day = one object)
- No cross-day aggregation queries needed (charts use client-side data)
- Schema can evolve without migrations (add new data sources freely)
- Simpler queries: one SELECT returns everything

**When you'd choose differently:**
- Need SQL aggregations across days ("avg S&P 500 this quarter") → normalized
- Time-series analysis at scale → TimescaleDB
- Need to index specific JSON paths for filtering → normalized or GIN indexes

---

## Decision 4: GitHub Actions for Scheduling

**Choice:** GitHub Actions cron for daily pipeline execution

**Alternatives considered:**
- AWS Lambda + EventBridge
- Google Cloud Functions + Cloud Scheduler
- Self-hosted cron (VPS)
- Airflow / Prefect / Dagster

**Why this choice:**
- Code and CI/CD in one place (GitHub)
- Free for public repos, generous free tier for private
- Docker support with layer caching
- Secrets management built in
- No infrastructure to manage

**When you'd choose differently:**
- Complex DAGs with dependencies → Airflow/Prefect
- Sub-minute scheduling → Lambda/Cloud Functions
- Need monitoring/alerting → Prefect/Dagster
- Cost-sensitive at scale → self-hosted

---

## Decision 5: Upsert Over Insert

**Choice:** `upsert` (insert or update on conflict) for all writes

**Why this choice:**
- Makes the pipeline idempotent (safe to re-run)
- Enables the backfill workflow without special-casing existing dates
- No need to check-before-write (avoids race conditions)
- If data quality improves (better API response), re-running updates the record

---

## Decision 6: Dual Frontend

**Choice:** Both Streamlit and Next.js

**Why both exist:**
- Streamlit was built first as a prototype/data exploration tool
- Next.js was built for a polished, production-ready web experience
- They serve different audiences and use cases

**When you'd consolidate:**
- If maintaining two frontends becomes burdensome
- If the RAG chat moves to the Next.js app
- If Streamlit Cloud hosting becomes a concern

---

## Decision 7: Plain Text Newsletter (No Markdown)

**Choice:** Explicitly request plain text output from Gemini

**Why:**
- Displayed in multiple contexts (Streamlit, Next.js, potential email)
- Markdown rendering is inconsistent across platforms
- `react-markdown` could handle it, but Streamlit's `st.write` renders it differently
- Plain text is universally compatible

---

## Decision 8: 768-Dimensional Embeddings

**Choice:** text-embedding-004 with 768 dimensions

**Alternatives:**
- OpenAI text-embedding-3-small (1536 dimensions)
- Cohere embed-english-v3 (1024 dimensions)
- Local model (all-MiniLM-L6, 384 dimensions)

**Why this choice:**
- Good balance of expressiveness and storage efficiency
- Same provider as generation model (one SDK)
- ~3KB per embedding (trivial storage)
- Optimized for retrieval tasks

## Related Notes
- [[Tradeoffs and Limitations]] - Honest assessment
- [[Common Questions]] - How to discuss these in interviews
- [[System Overview]] - The architecture these decisions shaped
