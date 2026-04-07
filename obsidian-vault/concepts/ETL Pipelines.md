# ETL Pipelines

## What is ETL?

**Extract, Transform, Load** - a data engineering pattern for moving data from source systems to a destination.

```
┌───────────┐     ┌─────────────┐     ┌──────────┐
│  EXTRACT  │ ──▶ │  TRANSFORM  │ ──▶ │   LOAD   │
│ Get data  │     │ Clean/shape │     │  Store    │
│ from APIs │     │ the data    │     │  in DB    │
└───────────┘     └─────────────┘     └──────────┘
```

## How This Project Implements ETL

### Extract

Pull raw data from 4+ external sources:

```python
# FRED API → Treasury yields, economic indicators
fred = Fred(api_key=os.getenv("fred_api_key"))
yields = fred.get_series("DGS10", start_date, end_date)

# yfinance → Stock prices, indices
data = yf.download(["AAPL", "MSFT", ...], period="7d")

# NewsAPI → Headlines
response = requests.get("https://newsapi.org/v2/everything", params={...})
```

**Key challenge:** Each source has its own format, frequency, and failure modes.

### Transform

Shape the raw data into a consistent structure:

```python
# Compute derived metrics (spreads)
spreads["10Y-2Y"] = yields["DGS10"] - yields["DGS2"]

# Format for AI consumption
indice_data_str = format_indices(raw_indices)
ticker_data_str = format_tickers(raw_tickers)

# AI synthesis (the most complex transformation)
newsletter_text = gemini.generate(prompt_with_all_data)

# Create embedding vector
embedding = gemini.embed(newsletter_text)

# Sanitize for JSON storage
clean_data = clean_for_json(structured_data)  # NaN → None
```

The AI synthesis is the most distinctive transformation - it converts raw numbers and headlines into a coherent narrative.

### Load

Store everything in Supabase:

```python
supabase.table("daily_briefs").upsert({
    "date": target_date,
    "full_text": newsletter_text,
    "structured_data": clean_data,
    "embedding": embedding
}).execute()
```

**Upsert pattern:** Insert if new, update if exists. Idempotent - running the pipeline twice for the same date produces the same result.

## ETL vs ELT

| | ETL | ELT |
|---|---|---|
| **Transform location** | Before loading | After loading |
| **Best for** | Structured destinations | Data warehouses (BigQuery, Snowflake) |
| **This project** | ✅ ETL | |

This project uses ETL because transformations (AI synthesis, embedding) must happen before loading. The database stores the final product, not raw data.

## Idempotency

A critical property of good ETL pipelines: running the same operation multiple times produces the same result.

```python
# Idempotent: upsert (insert or update on conflict)
supabase.table("daily_briefs").upsert({...}).execute()

# NOT idempotent: insert (would fail on duplicate)
supabase.table("daily_briefs").insert({...}).execute()  # ❌ Duplicate key error
```

The backfill workflow relies on this - you can safely re-run any date.

## Error Handling Patterns

### Graceful Degradation
```python
try:
    news = fetch_news()
except Exception:
    news = "News data unavailable"
    # Pipeline continues with partial data
```

### Retry Logic
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1))
def fetch_with_retry():
    return requests.get(url)
```

### Logging and Observability
The backfill script tracks success/failure counts:
```
Backfill complete: 18 success, 1 failed
Failed dates: [2024-01-22]
```

## Scheduling: Cron vs Event-Driven

| | Cron (This Project) | Event-Driven |
|---|---|---|
| **Trigger** | Fixed time schedule | Market close event, data arrival |
| **Pros** | Simple, predictable | Immediate, efficient |
| **Cons** | May run when no data, fixed delay | More complex infrastructure |

**Why cron?** Simplicity. The 4:45 PM ET schedule is reliable enough for daily briefs. Markets close at 4:00 PM, and 45 minutes is enough for closing data to propagate.

## Interview Talking Points

- "This project implements a daily ETL pipeline that extracts financial data from 4+ APIs, transforms it through AI synthesis and vectorization, and loads it into Supabase"
- "The pipeline is idempotent through upsert operations, enabling safe re-runs and backfills"
- "Each data source is independently error-handled so partial failures don't block the entire pipeline"
- "The most interesting transformation step is the AI synthesis, which converts raw numbers into a coherent market narrative"

## Related Notes
- [[Data Collection Pipeline]] - The Extract phase
- [[AI Synthesis Pipeline]] - The Transform phase
- [[Database Design]] - The Load destination
- [[CI-CD Pipeline]] - How the pipeline is scheduled
