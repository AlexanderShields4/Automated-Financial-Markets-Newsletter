# Automated Financial Markets Newsletter & Dashboard

This project is an automated, AI-powered specialized financial intelligence tool. It collects daily market data, economic indicators, and news, then uses Google's Gemini LLM to synthesize a professional PM Market Brief. The output is stored in a Supabase database with vector embeddings, allowing for historical retrieval and Q&A via RAG (Retrieval-Augmented Generation).

## Core Features/Components

### 1. Data Collection & Analysis (`newsletter_collector.py`)
- **Market Data**: Fetches yields, spreads, major indices, VIX, commodities, currencies, and "Magnificent 7" stock data using `yfinance` and `fredapi`.
- **News Aggregation**: Pulls relevant headlines via NewsAPI.
- **AI Synthesis**: Uses Google Gemini to generate a structured, professional-grade market write-up.
- **Vector Storage**: Generates embeddings for the write-up and stores both text and structured data in Supabase (Postgres with `pgvector`).

### 2. Interactive Dashboard (`newsletter_dashboard.py`)
- **Professional UI**: Built with Streamlit, featuring multiple themes (Classic, Dark, Forest, Ocean) and dynamic layouts.
- **Yield Curve Analysis**: Interactive visualizations of the current Treasury yield curve and historical spread trends (e.g., 10Y-2Y).
- **Market Chat (RAG)**: An integrated chatbot that allows users to ask questions about historical market data (e.g., "What happened to oil prices in October?"). It retrieves context from past newsletters in the database to answer accurately.

### 3. Database Architecture (Supabase)
- **Table**: `daily_briefs`
- **Columns**:
  - `date`: Primary unique key.
  - `full_text`: The AI-generated newsletter.
  - `structured_data`: JSON blob containing raw market numbers (yields, prices) for charting.
  - `embedding`: Vector representation (768 dimensions) for semantic search.

## Setup & configuration

### Prerequisites
- Python 3.9+
- A Supabase project with `pgvector` enabled.
- API Keys for Google Gemini, FRED, and NewsAPI.

### Environment Variables
Create a `.env` file in the root directory:

```env
# Database Credentials (Supabase)
SUPABASE_URL="https://your-project.supabase.co"
SUPABASE_SERVICE_KEY="your-service-role-key"

# AI & Data Providers
GOOGLE_KEY="your-gemini-api-key"
GOOGLE_EMBEDDING_KEY="your-gemini-api-key" # Can be same as above
FRED_API_KEY="your-fred-api-key"
NewsApikey="your-newsapi-key"
