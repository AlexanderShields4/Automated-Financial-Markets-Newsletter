# Python Backend

## Core Runtime

**Python 3.9** - Chosen for broad library compatibility and Docker base image availability.

## Dependencies Breakdown

### Data Collection Libraries

**`yfinance`** - Yahoo Finance API wrapper
- Fetches stock prices, indices, commodities, ETFs
- No API key required (scrapes Yahoo Finance)
- Returns pandas DataFrames
- Limitation: Rate limiting, occasional data gaps

**`fredapi`** - Federal Reserve Economic Data client
- Official Python wrapper for the FRED API
- Requires free API key from fred.stlouisfed.org
- Returns pandas Series with date index
- Covers 800,000+ economic time series

**`requests`** - HTTP client library
- Used for NewsAPI REST calls
- Standard Python HTTP library

**`beautifulsoup4`** - HTML/XML parser
- Available for web scraping if needed
- Parses HTML responses for data extraction

### AI/ML Libraries

**`google-genai`** - Google's Generative AI SDK
- Direct interface to Gemini models
- Text generation and embedding creation
- Replaces older `google-generativeai` package

**`langchain-google-genai`** - LangChain + Google integration
- Wraps Google models in LangChain's abstraction layer
- Enables use in LangChain chains and agents

**`langchain-core`** - LangChain framework core
- Prompt templates, output parsers
- Runnable interface for composable pipelines
- Document abstractions

**`langchain-community`** - Community integrations
- Vector store integrations
- Additional embedding providers
- Third-party tool wrappers

### Database Libraries

**`supabase`** - Supabase Python client
- Wraps Supabase's REST API (PostgREST)
- Table operations: select, insert, upsert, delete
- RPC function calls
- Auth and storage APIs

**`psycopg2-binary`** - PostgreSQL adapter
- Direct SQL connection to PostgreSQL
- Used in `db_setup.py` for DDL operations (CREATE TABLE, etc.)
- `binary` variant includes pre-compiled C extensions (no build tools needed)
- Not used for routine data operations (Supabase client handles those)

### Data Processing

**`pandas`** - DataFrame library
- Manipulates tabular data from APIs
- Date handling, aggregations, transformations
- Core data structure throughout the pipeline

**`numpy`** - Numerical computing
- Array operations used by pandas
- Mathematical functions for data processing

**`plotly`** - Interactive visualization
- Used in Streamlit dashboard for charts
- Yield curve and spread visualizations
- Client-side rendering with zoom, hover, pan

### UI Framework

**`streamlit`** - Data app framework
- Turns Python scripts into web apps
- Built-in widgets (charts, tables, inputs, chat)
- Session state for interactivity
- Hot reload during development

### Utilities

**`python-dotenv`** - `.env` file loader
- Loads environment variables from `.env` file
- `load_dotenv()` called at script startup
- Keeps secrets out of code

**`pydantic`** - Data validation
- Type-safe data models
- Used by Supabase client internally

**`tenacity`** - Retry logic
- Decorator-based retry with backoff
- Handles transient API failures

## Code Organization Pattern

The project follows a **script-based architecture** (not a package):

```
newsletter_collector.py   # Main pipeline (entry point for CI)
backfill_collector.py     # Extended pipeline for historical data
backfill.py               # CLI wrapper
rag_engine.py             # RAG class (imported by dashboard)
db_setup.py               # One-time schema setup
newsletter_dashboard.py   # Streamlit app (entry point for UI)
```

Each script is self-contained with its own imports and configuration. No shared module or package structure - appropriate for a small project with distinct entry points.

## Related Notes
- [[Data Collection Pipeline]] - How these libraries are used
- [[Google Gemini]] - AI model details
- [[Supabase]] - Database platform
- [[Docker]] - How the Python environment is containerized
