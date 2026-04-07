# System Overview

## What This Project Does

This is an **automated financial intelligence platform** that:
1. Collects market data from 7+ sources every weekday at 4:45 PM ET
2. Uses Google Gemini AI to synthesize a professional "PM Market Brief"
3. Stores everything (text + vector embeddings) in Supabase/PostgreSQL
4. Serves it through two frontends: Streamlit (data dashboard) and Next.js (production web app)
5. Provides RAG-powered Q&A over historical market briefs

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                    GITHUB ACTIONS (CRON)                      │
│                 Mon-Fri @ 4:45 PM ET (20:45 UTC)             │
└──────────────────┬───────────────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────────────┐
│               DOCKER CONTAINER (python:3.9-slim)             │
│  ┌────────────────────────────────────────────────────────┐  │
│  │           newsletter_collector.py                       │  │
│  │                                                         │  │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────────┐  │  │
│  │  │ FRED API│ │yfinance │ │ NewsAPI │ │  Computed   │  │  │
│  │  │Treasury │ │ Stocks  │ │Headlines│ │  Spreads    │  │  │
│  │  │Economic │ │ Indices │ │ 6 cats  │ │  4 pairs    │  │  │
│  │  └────┬────┘ └────┬────┘ └────┬────┘ └──────┬──────┘  │  │
│  │       └───────────┴───────────┴──────────────┘         │  │
│  │                       │                                 │  │
│  │                       ▼                                 │  │
│  │           ┌─────────────────────┐                       │  │
│  │           │   GOOGLE GEMINI     │                       │  │
│  │           │  2.5-Flash (Gen)    │                       │  │
│  │           │  Embedding-001      │                       │  │
│  │           └──────────┬──────────┘                       │  │
│  │                      │                                  │  │
│  │              ┌───────┴───────┐                          │  │
│  │              │  full_text    │                          │  │
│  │              │  structured   │                          │  │
│  │              │  embedding    │                          │  │
│  │              └───────┬───────┘                          │  │
│  └──────────────────────┼──────────────────────────────────┘  │
└─────────────────────────┼────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────────┐
│                SUPABASE (PostgreSQL + pgvector)               │
│                                                               │
│  daily_briefs table                                          │
│  ┌────┬──────┬───────────┬─────────────────┬──────────────┐  │
│  │ id │ date │ full_text │ structured_data │ embedding    │  │
│  │UUID│ DATE │   TEXT    │     JSONB       │ VECTOR(768)  │  │
│  └────┴──────┴───────────┴─────────────────┴──────────────┘  │
│                                                               │
│  HNSW index on embedding (cosine similarity)                 │
│  match_daily_briefs() RPC function                           │
└──────────────┬────────────────────────┬──────────────────────┘
               │                        │
               ▼                        ▼
┌──────────────────────┐  ┌──────────────────────────────────┐
│  STREAMLIT DASHBOARD │  │     NEXT.JS WEB APP              │
│  - Interactive charts│  │  - SSR dashboard                 │
│  - RAG Market Chat   │  │  - Archives browser              │
│  - Plotly viz        │  │  - Recharts visualizations       │
│  Port 8501           │  │  - Responsive + animated         │
└──────────────────────┘  └──────────────────────────────────┘
```

## Key Design Principles

1. **Separation of Concerns** - Data collection, AI synthesis, storage, and presentation are independent modules
2. **Resilient Collection** - Each data source fails independently; partial data still produces a brief
3. **Dual Storage** - Both human-readable text (`full_text`) and machine-processable data (`structured_data` as JSONB)
4. **Semantic Search** - Vector embeddings enable natural language queries over historical data
5. **Serverless Execution** - No persistent server needed; GitHub Actions runs the pipeline on schedule

## Related Notes
- [[Data Collection Pipeline]] - Deep dive into data sources
- [[AI Synthesis Pipeline]] - How Gemini generates briefs
- [[Database Design]] - Schema and indexing strategy
- [[CI-CD Pipeline]] - Automation details
