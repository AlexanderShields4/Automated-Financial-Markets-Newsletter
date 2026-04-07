# Yield Curve and Spreads

## What is a Yield Curve?

The yield curve plots **interest rates of US Treasury bonds** across different maturities (time to repayment):

```
Yield %
  5.0 │                                          ●  30Y
  4.8 │                                    ●  20Y
  4.6 │                              ●  10Y
  4.4 │                       ●  7Y
  4.2 │                 ●  5Y
  4.0 │           ●  3Y
  3.8 │      ●  2Y
  3.6 │ ●  1Y
  3.4 │●  6M
  3.2 │●  3M
      └─────────────────────────────────────────────
        3M  6M  1Y  2Y  3Y  5Y  7Y  10Y 20Y 30Y
                        Maturity
```

**Normal yield curve:** Slopes upward (longer maturity = higher yield). Makes sense - you demand more return for locking money up longer.

## Why the Yield Curve Matters

The yield curve is one of the most watched indicators in finance because it reflects **market expectations about the economy**:

| Shape | What It Signals |
|-------|----------------|
| **Normal (upward)** | Economic growth expected, inflation under control |
| **Flat** | Uncertainty, possible transition period |
| **Inverted (downward)** | Recession expected; markets think the Fed will cut rates |
| **Steep** | Strong growth expected, possibly rising inflation |

## What is a Yield Spread?

A spread is the **difference between two yields**. This project tracks four key spreads:

### 10-Year minus 2-Year (10Y-2Y)

```
Spread = 10Y yield - 2Y yield
```

- **The classic recession indicator**
- When **positive**: normal, economy healthy
- When **negative (inverted)**: has preceded every US recession since 1970
- **Why it works**: Inversion means investors expect the Fed to cut short-term rates (due to recession), driving long-term yields below short-term yields

### 10-Year minus 3-Month (10Y-3M)

- **The Federal Reserve's preferred recession predictor**
- More directly reflects Fed policy (3M is closely tied to the Fed Funds Rate)
- Academic research shows this spread has the best predictive power

### 30-Year minus 5-Year (30Y-5Y)

- Reflects **long-term growth expectations**
- A wide spread suggests optimism about long-term economic growth
- A narrow/inverted spread suggests long-term pessimism

### 5-Year minus 2-Year (5Y-2Y)

- Captures **medium-term expectations**
- Often the first spread to invert in a cycle
- Useful as an early warning signal

## How Spreads Are Computed in This Project

```python
# From newsletter_collector.py
spreads = {
    '10Y-2Y': {},
    '10Y-3M': {},
    '30Y-5Y': {},
    '5Y-2Y': {}
}

for date in common_dates:
    spreads['10Y-2Y'][date] = yields['DGS10'][date] - yields['DGS2'][date]
    spreads['10Y-3M'][date] = yields['DGS10'][date] - yields['DGS3MO'][date]
    spreads['30Y-5Y'][date] = yields['DGS30'][date] - yields['DGS5'][date]
    spreads['5Y-2Y'][date]  = yields['DGS5'][date]  - yields['DGS2'][date]
```

## Treasury Tenors Tracked

| Series | Maturity | Significance |
|--------|----------|-------------|
| DGS3MO | 3 months | Proxy for Fed Funds Rate |
| DGS6MO | 6 months | Short-term rates |
| DGS1 | 1 year | Short-term expectations |
| DGS2 | 2 years | Fed policy expectations (1-2 years out) |
| DGS3 | 3 years | Medium-term |
| DGS5 | 5 years | Medium-term expectations |
| DGS7 | 7 years | Intermediate |
| DGS10 | 10 years | **Benchmark rate** (mortgages, corporate bonds priced off this) |
| DGS20 | 20 years | Long-term |
| DGS30 | 30 years | Longest maturity, reflects very long-term expectations |

## The 10-Year Yield: Why It's King

The 10-year Treasury yield is the most important rate in finance:
- **Mortgage rates** are priced as a spread over the 10Y
- **Corporate bonds** are benchmarked against it
- **Stock valuations** use it as the "risk-free rate" in DCF models
- **Dollar strength** correlates with 10Y yield changes
- **Global benchmark** - other countries' rates are compared to it

## Interview Talking Points

- "We track 10 Treasury tenors from 3-month to 30-year, sourced from the Federal Reserve's FRED API"
- "The 10Y-2Y spread has inverted before every US recession since 1970 - it's one of the most reliable recession indicators"
- "We compute 4 key spreads daily and visualize them over time to show trend changes"
- "The spread data is stored as JSONB in Supabase and rendered as area charts in both the Streamlit and Next.js frontends"

## Related Notes
- [[Data Collection Pipeline]] - How yield data is fetched
- [[Frontend Architecture]] - How spreads are visualized
- [[ETL Pipelines]] - The data processing pattern
