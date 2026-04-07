# Project Walkthrough Script

## The 2-Minute Elevator Pitch

> "I built an automated financial intelligence platform that collects market data from multiple APIs every day, uses Google Gemini to synthesize it into professional market briefs, stores everything with vector embeddings in Supabase, and serves it through a Next.js web app with semantic search. The whole pipeline runs hands-free via GitHub Actions - I haven't touched it manually in months, and it produces a new brief every weekday at market close."

## The 5-Minute Deep Dive

### 1. The Problem (30 seconds)

> "Portfolio managers and analysts spend significant time every day gathering market data from multiple sources - treasury yields, stock prices, economic indicators, news. I wanted to automate this into a daily brief that synthesizes everything into actionable insights."

### 2. Architecture (1 minute)

> "The system has three main components:
>
> **First, the data pipeline.** A Python script collects data from 4 APIs: FRED for treasury yields and economic indicators, yfinance for stock prices and indices, and NewsAPI for financial headlines. It also computes derived metrics like yield spreads - for example, the 10Y-2Y spread which is a classic recession indicator.
>
> **Second, the AI synthesis.** All the collected data is fed to Google Gemini 2.5-Flash with a carefully structured prompt that produces a professional PM Market Brief. The brief is then embedded into a 768-dimensional vector using Gemini's embedding model.
>
> **Third, the storage and serving layer.** Everything goes into Supabase - which is PostgreSQL with the pgvector extension. I store the text, the raw structured data as JSONB, and the embedding vector. The frontend is a Next.js app with server-side rendering, interactive charts via Recharts, and an archives section."

### 3. The Interesting Parts (2 minutes)

> "A few things I'm proud of:
>
> **RAG-powered market chat.** Users can ask natural language questions like 'What happened to oil last week?' and the system uses vector similarity search to find relevant historical briefs, then Gemini synthesizes an answer grounded in actual data. This uses an HNSW index on pgvector for fast cosine similarity search.
>
> **Resilient pipeline design.** Each data source is independently error-handled. If NewsAPI is down, the pipeline still runs with treasury, stock, and economic data. The AI prompt is designed to work with partial data.
>
> **Backfill capability.** I built a separate workflow that can fill in missing dates for any historical range. It's aware of business days, checks existing data to avoid duplicates, and warns about NewsAPI's 30-day limitation."

### 4. The Stack (30 seconds)

> "Python backend with yfinance, fredapi, and the Google GenAI SDK. Supabase for PostgreSQL with pgvector. Next.js 16 with TypeScript and Tailwind for the frontend. Docker for containerization. GitHub Actions for scheduling and CI/CD."

## Key Points to Hit

1. **It's fully automated** - Runs daily without intervention
2. **Multiple data sources** - Not just one API, but 4+ sources synthesized together
3. **AI is used intelligently** - Not just "chatbot", but structured data synthesis + semantic search
4. **Production patterns** - Docker, CI/CD, error handling, idempotent operations
5. **Full stack** - Python backend, Next.js frontend, PostgreSQL database, vector search

## Adapting for Different Audiences

### For a Backend/Data Engineering Role
Focus on: ETL pipeline, error handling, idempotency, API integration, data modeling, JSONB vs normalized schema

### For a Full-Stack Role
Focus on: Next.js SSR, TypeScript, component architecture, Supabase integration, responsive design

### For an AI/ML Role
Focus on: RAG architecture, embedding strategy, prompt engineering, HNSW indexing, cosine similarity, LLM evaluation

### For a DevOps/Platform Role
Focus on: GitHub Actions, Docker layer caching, secrets management, cron scheduling, automated workflows

## Related Notes
- [[Common Questions]] - What they'll ask next
- [[Key Design Decisions]] - Why you made the choices you did
- [[Tradeoffs and Limitations]] - Honest self-assessment
