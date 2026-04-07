# Data Collection Pipeline

## Overview

The `newsletter_collector.py` script orchestrates data collection from **4 independent sources**, computes derived metrics, and compiles everything into a structured payload. Each source is wrapped in its own try/except block, so a single API failure doesn't crash the entire pipeline.

## Data Sources

### 1. Treasury Yields (FRED API)

**Library:** `fredapi`
**Authentication:** API key

Fetches the last 7 days of data for **10 Treasury tenors**:

| Series ID | Tenor |
|-----------|-------|
| DGS3MO | 3-Month |
| DGS6MO | 6-Month |
| DGS1 | 1-Year |
| DGS2 | 2-Year |
| DGS3 | 3-Year |
| DGS5 | 5-Year |
| DGS7 | 7-Year |
| DGS10 | 10-Year |
| DGS20 | 20-Year |
| DGS30 | 30-Year |

**Why 7 days?** Financial data has gaps (weekends, holidays). Fetching a week ensures we always get the most recent available value.

### 2. Yield Spread Calculations (Computed)

**Not an API call** - derived from Treasury data. Four critical spreads:

| Spread | Significance |
|--------|-------------|
| **10Y - 2Y** | Classic recession indicator. Inversion (negative) has preceded every US recession since 1970 |
| **10Y - 3M** | The Federal Reserve's preferred recession predictor |
| **30Y - 5Y** | Reflects long-term growth expectations |
| **5Y - 2Y** | Medium-term economic expectations |

> See [[Yield Curve and Spreads]] for the financial theory behind this.

### 3. Economic Indicators (FRED API)

Nine key macroeconomic series:

| Series | Name | Frequency |
|--------|------|-----------|
| ICSA | Initial Jobless Claims | Weekly |
| CPIAUCSL | Consumer Price Index | Monthly |
| PPIACO | Producer Price Index | Monthly |
| RSAFS | Retail Sales | Monthly |
| DGORDER | Durable Goods Orders | Monthly |
| UMCSENT | Consumer Confidence | Monthly |
| INDPRO | Industrial Production | Monthly |
| HOUST | Housing Starts | Monthly |
| A191RL1Q225SBEA | GDP Growth Rate | Quarterly |

**Implementation detail:** Fetches 90 days of history for each and takes the latest non-null value. This handles the varying release schedules.

### 4. Stock Prices (yfinance)

**The "Magnificent 7":** AAPL, MSFT, GOOGL, AMZN, NVDA, META, TSLA

- Fetches 7 days of daily OHLC (Open, High, Low, Close) data
- Used for daily price changes and trend analysis

### 5. Market Indices (yfinance)

| Symbol | Index |
|--------|-------|
| ^GSPC | S&P 500 |
| ^DJI | Dow Jones Industrial Average |
| ^IXIC | NASDAQ Composite |
| ^RUT | Russell 2000 (small caps) |
| ^VIX | CBOE Volatility Index |
| CL=F | WTI Crude Oil Futures |
| BZ=F | Brent Crude Oil Futures |
| GC=F | Gold Futures |
| DX-Y.NYB | US Dollar Index |

### 6. Financial News (NewsAPI)

**6 independent queries** to maximize coverage:

1. Stock market / equities / S&P 500
2. Apple / Microsoft / Google / Amazon / Nvidia / Meta / Tesla
3. Inflation / CPI / PPI / interest rates / Federal Reserve
4. Recession / GDP / economy / job market
5. Oil prices / crude / energy / commodities
6. Housing market / mortgage / real estate

**Limitation:** NewsAPI free tier only returns articles from the last 30 days. The backfill script warns about this.

## Data Compilation

All collected data is assembled into a Python dictionary:

```python
{
    'tenyrtwoyr': [...],           # Spread time series
    'indice_data_str': "...",       # Formatted index data
    'ticker_data': "...",           # Formatted stock data
    'newsstr': "...",               # Concatenated news headlines
    'economic_indicators': {...},   # Latest indicator values
    'yield_data': {                 # Full yield curves
        'DGS3MO': {'2024-01-15': 5.23, ...},
        ...
    },
    'yield_spreads': {              # Computed spreads
        '10Y-2Y': {'2024-01-15': 0.45, ...},
        ...
    }
}
```

## Error Handling Strategy

```python
# Each source is independent
try:
    treasury_data = fetch_treasury_yields()
except Exception as e:
    print(f"Treasury fetch failed: {e}")
    treasury_data = {}  # Pipeline continues with partial data
```

This means the AI synthesis step always runs, even if some data is missing. The prompt is designed to work with partial data.

## Related Notes
- [[AI Synthesis Pipeline]] - What happens after collection
- [[FRED API]] - More about the Federal Reserve data service
- [[ETL Pipelines]] - The pattern this follows
- [[Yield Curve and Spreads]] - Financial domain knowledge
