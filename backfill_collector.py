#!/usr/bin/env python3
"""
Backfill script for missing economic news data in the daily_briefs Supabase table.

Usage:
    python backfill_collector.py --start 2026-01-01 --end 2026-03-03

Identifies missing weekday dates and collects data for each, then upserts to Supabase.
"""

import argparse
import time
import pandas as pd
import json
import requests
import sys
import yfinance as yf
from datetime import datetime, timedelta, date
import os
from fredapi import Fred
from google import genai
from dotenv import load_dotenv
import unicodedata
from supabase import create_client, Client
from langchain_google_genai import GoogleGenerativeAIEmbeddings


def get_existing_dates(supabase: Client) -> set:
    """Query Supabase for all existing dates in daily_briefs."""
    result = supabase.table("daily_briefs").select("date").execute()
    return {row["date"] for row in result.data}


def get_expected_weekdays(start: date, end: date) -> list:
    """Return sorted list of weekday dates between start and end (inclusive)."""
    days = []
    current = start
    while current <= end:
        if current.weekday() < 5:  # Mon-Fri
            days.append(current)
        current += timedelta(days=1)
    return days


def collect_fred_data(fred: Fred, target_date: date):
    """Collect yield curve and economic indicator data from FRED for a target date."""
    start_date = target_date - timedelta(days=7)

    yield_curves = {
        '3M': 'DGS3MO', '6M': 'DGS6MO', '1Y': 'DGS1', '2Y': 'DGS2',
        '3Y': 'DGS3', '5Y': 'DGS5', '7Y': 'DGS7', '10Y': 'DGS10',
        '20Y': 'DGS20', '30Y': 'DGS30'
    }

    yield_data = {}
    spread_series = {}
    for tenor, series_id in yield_curves.items():
        try:
            series = fred.get_series(series_id, observation_start=start_date, observation_end=target_date)
            yield_data[tenor] = {d.strftime('%Y-%m-%d'): v for d, v in series.to_dict().items()}
            spread_series[tenor] = series
        except Exception as e:
            print(f"  Error fetching {series_id}: {e}")

    # Calculate spreads
    spreads = {}
    spread_names = {
        '10Y-2Y': ('10Y', '2Y'),
        '10Y-3M': ('10Y', '3M'),
        '30Y-5Y': ('30Y', '5Y'),
        '5Y-2Y': ('5Y', '2Y'),
    }
    for name, (long, short) in spread_names.items():
        if long in spread_series and short in spread_series:
            calc = spread_series[long] - spread_series[short]
            spreads[name] = {d.strftime('%Y-%m-%d'): v for d, v in calc.to_dict().items()}

    # Format spread lists
    def format_spread(spread_dict):
        return [f"{d}: {v:.2f}" for d, v in spread_dict.items() if pd.notnull(v)]

    tenyrtwoyr = format_spread(spreads.get('10Y-2Y', {}))
    tenthreem = format_spread(spreads.get('10Y-3M', {}))
    thirtyfivey = format_spread(spreads.get('30Y-5Y', {}))
    fiveytwoyr = format_spread(spreads.get('5Y-2Y', {}))

    # Latest spread date
    try:
        latest_spread_date = max(*(list(s.keys()) for s in spreads.values()))
    except Exception:
        latest_spread_date = str(target_date)

    # Economic indicators
    economic_indicators = {
        'Initial Jobless Claims': 'ICSA',
        'CPI': 'CPIAUCSL',
        'PPI': 'PPIACO',
        'Retail Sales': 'RSAFS',
        'Manufacturing PMI': 'NAPM',
        'Consumer Confidence': 'UMCSENT',
        'Industrial Production': 'INDPRO',
        'Housing Starts': 'HOUST',
        'GDP Growth Rate': 'A191RL1Q225SBEA'
    }

    latest_economic_data = {}
    for indicator_name, series_id in economic_indicators.items():
        try:
            series = fred.get_series(series_id, observation_start=start_date, observation_end=target_date)
            if not series.empty:
                latest_date = series.index[-1]
                latest_value = series.iloc[-1]
                latest_economic_data[indicator_name] = f"{latest_date.strftime('%Y-%m-%d')}: {latest_value:.2f}"
        except Exception as e:
            print(f"  Error fetching {series_id}: {e}")

    return {
        'yield_data': yield_data,
        'spreads': spreads,
        'tenyrtwoyr': tenyrtwoyr,
        'tenthreem': tenthreem,
        'thirtyfivey': thirtyfivey,
        'fiveytwoyr': fiveytwoyr,
        'latest_spread_date': latest_spread_date,
        'economic_indicators': latest_economic_data,
    }


def collect_stock_data(target_date: date):
    """Collect stock ticker and index data from yfinance for a target date."""
    start_date = target_date - timedelta(days=7)

    # Magnificent 7 tickers
    tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA"]
    data = yf.download(tickers, start=start_date, end=target_date + timedelta(days=1), interval="1d", group_by='ticker')
    ticker_data = ""
    latest_ticker_date = None
    for ticker in tickers:
        if ticker in data:
            df = data[ticker]
            for idx, row in df.iterrows():
                if idx.weekday() < 5:
                    open_price = row['Open']
                    close_price = row['Close']
                    date_str = idx.strftime('%Y-%m-%d')
                    if latest_ticker_date is None or date_str > latest_ticker_date:
                        latest_ticker_date = date_str
                    ticker_data += f"{ticker} {date_str}: Open: ${open_price:.2f} Close: ${close_price:.2f}. "

    # Market indices
    indices = ["^GSPC", "^DJI", "^IXIC", "^RUT", "^VIX", "CL=F", "BZ=F", "GC=F", "DX-Y.NYB"]
    data = yf.download(indices, start=target_date, end=target_date + timedelta(days=1), interval="1d", group_by='ticker')

    symbol_names = {
        "^GSPC": "S&P 500", "^DJI": "Dow Jones", "^IXIC": "NASDAQ", "^RUT": "Russell 2000",
        "^VIX": "VIX", "CL=F": "WTI Crude", "BZ=F": "Brent Crude", "GC=F": "Gold",
        "DX-Y.NYB": "US Dollar Index"
    }

    indice_data_str = ""
    for index in indices:
        try:
            if isinstance(data.columns, pd.MultiIndex):
                try:
                    if index not in data.columns.levels[0]:
                        continue
                    ticker_df = data[index]
                    if ticker_df.empty or pd.isna(ticker_df['Open'].iloc[0]):
                        continue
                    open_price = ticker_df['Open'].iloc[0]
                    close_price = ticker_df['Close'].iloc[0]
                except KeyError:
                    continue
            else:
                if 'Open' not in data.columns or data.empty:
                    continue
                open_price = data['Open'].iloc[0]
                close_price = data['Close'].iloc[0]

            name = symbol_names.get(index, index)
            indice_data_str += f"{name}: Open: {float(open_price):.2f} Close: {float(close_price):.2f}. "
        except (KeyError, IndexError, ValueError):
            pass

    return {
        'ticker_data': ticker_data,
        'latest_ticker_date': latest_ticker_date,
        'indice_data_str': indice_data_str,
    }


def collect_news(target_date: date, api_key: str):
    """Collect news headlines from NewsAPI. Gracefully returns empty if unavailable."""
    if not api_key:
        print("  NewsAPI key not set, skipping news collection.")
        return f"\n📰 Broad Market News for {target_date}: No news data available.\n"

    # NewsAPI free plan only goes back ~30 days
    days_ago = (date.today() - target_date).days
    if days_ago > 30:
        print(f"  Skipping NewsAPI — date is {days_ago} days ago (free plan limit ~30 days).")
        return f"\n📰 Broad Market News for {target_date}: News data unavailable (beyond NewsAPI free plan range).\n"

    yesterday = target_date - timedelta(days=1)
    url = "https://newsapi.org/v2/everything"

    queries = [
        "stock market OR equities OR shares OR S&P 500 OR NASDAQ OR Dow Jones",
        "Apple OR Microsoft OR Google OR Amazon OR Nvidia OR Meta OR Tesla",
        "inflation OR CPI OR PPI OR interest rates OR Federal Reserve",
        "recession OR GDP OR economy OR job market OR payrolls",
        "oil prices OR crude OR energy OR commodities OR gold",
        "housing market OR mortgage OR real estate OR home sales"
    ]

    base_params = {
        "from": yesterday.isoformat(),
        "to": target_date.isoformat(),
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 100,
        "apiKey": api_key
    }

    all_articles = []
    newsstr = f"\n📰 Broad Market News for {target_date}:\n"

    for query in queries:
        params = base_params.copy()
        params["q"] = query
        try:
            response = requests.get(url, params=params)
            if response.status_code != 200:
                print(f"  NewsAPI error {response.status_code} for query: {query}")
                continue
            data = response.json()
            if data.get("status") == "ok":
                all_articles.extend(data.get("articles", []))
        except Exception as e:
            print(f"  NewsAPI request failed: {e}")

    for i, article in enumerate(all_articles):
        title = article['title']
        source = article['source']['name']
        article_url = article['url']
        newsstr += f"{i}. {title}   Source: {source}  URL: {article_url}\n"
        if i >= 40:
            break

    return newsstr


def generate_newsletter(target_date: date, fred_data: dict, stock_data: dict, newsstr: str, google_key: str) -> str:
    """Generate the newsletter text via Gemini."""
    data_date_notes = (
        f"Latest available spread data date: {fred_data['latest_spread_date']}.\n"
        f"Latest available ticker data date: {stock_data['latest_ticker_date'] or 'N/A'}.\n"
    )

    message = (
        f"You are an experienced economist and financial analyst specializing in market dynamics, bond markets, and Treasury yields. Format your response in plain text only, avoiding any special formatting or markdown.\n\n"
        f"You are the author of a daily PM financial newsletter that summarizes the key market developments of the day. "
        f"The market brief should be titled 'PM Market Brief by Gemini' in plain text. Be sure to reformat all of the information taken from brent crude oil as it is an issue in your past editions "
        f"Your goal is to highlight the most important news, notable market movements, and any meaningful economic signals. "
        f"If the date corresponds to a weekend, do not include market tickers or Magnificent 7 stock data.\n\n"
        f"Your task is to analyze and interpret the following financial data:\n"
        f"• The 10-Year minus 2-Year Treasury yield spread\n"
        f"• Major stock indices (daily open and close)\n"
        f"• Market Volatility (VIX)\n"
        f"• Commodities (WTI Crude, Brent Crude, Gold)\n"
        f"• Currency Markets (US Dollar Index)\n"
        f"• The Magnificent 7 stock prices (daily open and close, last seven days)\n"
        f"• Recent and scheduled economic releases\n"
        f"• Key market news headlines from the last 24 hours\n\n"
        f"Please organize your analysis into these sections: \n"
        f"1. Market Summary\n"
        f"   - Major Indices Performance\n"
        f"   - VIX and Market Sentiment\n"
        f"2. Fixed Income & Macro\n"
        f"   - Treasury Spreads Analysis\n"
        f"   - Dollar Index Movements\n"
        f"3. Commodities & Energy\n"
        f"   - Oil Markets (WTI/Brent)\n"
        f"   - Gold Price Action\n"
        f"4. Economic Data\n"
        f"   - Today's Releases\n"
        f"   - Forward Calendar\n"
        f"5. Key Takeaways & Outlook\n\n"
        f"Also include a neatly formatted table summarizing key numerical data (excluding news headlines).\n\n"
        f"Data for analysis (Date: {target_date}):\n"
        f"Note on data currency:\n{data_date_notes}\n"
        f"— Last 5 days of 10-Year minus 2-Year Treasury yield spread, the 30 yr five yr spread, the ten three month spread and the five year 2 yr spread: {fred_data['tenyrtwoyr'], fred_data['thirtyfivey'], fred_data['tenthreem'], fred_data['fiveytwoyr']}\n"
        f"— Market indices and indicators: {stock_data['indice_data_str']}\n"
        f"— Magnificent 7 stock prices (last seven days, daily open and close): {stock_data['ticker_data']}\n"
        f"— Economic releases from FRED: \n"
        f"— Market news headlines (past 24h): {newsstr}\n"
        f"create a nicely formatted table summarizing key numerical data (excluding news headlines). All of this information should be suitable for the syntax and style of the streamlit application\n\n"
    )

    client = genai.Client(api_key=google_key)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=message
    )
    text = str(response.text)
    return unicodedata.normalize("NFKD", text)


def clean_json_data(obj):
    """Sanitize data for JSON compliance (handle NaN, Inf)."""
    if isinstance(obj, float):
        return None if pd.isna(obj) or obj == float('inf') or obj == float('-inf') else obj
    elif isinstance(obj, dict):
        return {k: clean_json_data(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_json_data(v) for v in obj]
    return obj


def backfill_date(target_date: date, fred: Fred, supabase: Client, embeddings, news_api_key: str, google_key: str):
    """Collect data, generate newsletter, and upsert to Supabase for a single date."""
    print(f"\n{'='*60}")
    print(f"Processing {target_date} ...")
    print(f"{'='*60}")

    # Collect data
    print("  Collecting FRED data...")
    fred_data = collect_fred_data(fred, target_date)

    print("  Collecting stock data...")
    stock_data = collect_stock_data(target_date)

    print("  Collecting news...")
    newsstr = collect_news(target_date, news_api_key)

    # Build market_data structure
    market_data = {
        'tenyrtwoyr': fred_data['tenyrtwoyr'],
        'indice_data_str': stock_data['indice_data_str'],
        'ticker_data': stock_data['ticker_data'],
        'newsstr': newsstr,
        'economic_indicators': fred_data['economic_indicators'],
        'yield_data': fred_data['yield_data'],
        'yield_spreads': fred_data['spreads'],
    }

    # Generate newsletter
    print("  Generating newsletter via Gemini...")
    newsletter_text = generate_newsletter(target_date, fred_data, stock_data, newsstr, google_key)

    # Generate embedding
    print("  Generating embedding...")
    vector = embeddings.embed_query(newsletter_text)

    # Upsert to Supabase
    data_payload = clean_json_data({
        "date": str(target_date),
        "full_text": newsletter_text,
        "structured_data": market_data,
        "embedding": vector
    })

    try:
        supabase.table("daily_briefs").upsert(data_payload, on_conflict="date").execute()
        print(f"  Successfully saved {target_date} to Supabase!")
    except Exception as e:
        print(f"  Error saving {target_date} to Supabase: {e}")


def main():
    parser = argparse.ArgumentParser(description="Backfill missing daily briefs in Supabase.")
    parser.add_argument("--start", required=True, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", default=None, help="End date (YYYY-MM-DD), defaults to yesterday")
    parser.add_argument("--sleep", type=float, default=2.0, help="Seconds to sleep between dates (default: 2)")
    args = parser.parse_args()

    start = date.fromisoformat(args.start)
    end = date.fromisoformat(args.end) if args.end else date.today() - timedelta(days=1)

    if start > end:
        print(f"Error: start date {start} is after end date {end}")
        sys.exit(1)

    load_dotenv()

    # Validate required env vars
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    google_key = os.getenv("GOOGLE_KEY")
    fred_api_key = os.getenv("fred_api_key")

    missing = []
    if not supabase_url:
        missing.append("SUPABASE_URL")
    if not supabase_key:
        missing.append("SUPABASE_SERVICE_KEY")
    if not google_key:
        missing.append("GOOGLE_KEY")
    if not fred_api_key:
        missing.append("fred_api_key")
    if missing:
        print(f"Error: Missing required environment variables: {', '.join(missing)}")
        sys.exit(1)

    supabase = create_client(supabase_url, supabase_key)
    fred = Fred(api_key=fred_api_key)
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=os.getenv("GOOGLE_EMBEDDING_KEY"),
        output_dimensionality=768
    )
    news_api_key = os.getenv("NewsApikey")

    # Find missing dates
    print(f"Checking for missing dates between {start} and {end}...")
    existing_dates = get_existing_dates(supabase)
    expected_dates = get_expected_weekdays(start, end)
    missing_dates = [d for d in expected_dates if str(d) not in existing_dates]

    print(f"Expected weekdays: {len(expected_dates)}")
    print(f"Already in Supabase: {len(expected_dates) - len(missing_dates)}")
    print(f"Missing (to backfill): {len(missing_dates)}")

    if not missing_dates:
        print("Nothing to backfill!")
        return

    print(f"\nDates to backfill: {', '.join(str(d) for d in missing_dates)}")

    for i, target_date in enumerate(missing_dates):
        backfill_date(target_date, fred, supabase, embeddings, news_api_key, google_key)
        # Rate limiting between iterations (skip sleep after last one)
        if i < len(missing_dates) - 1:
            print(f"  Sleeping {args.sleep}s before next date...")
            time.sleep(args.sleep)

    print(f"\nBackfill complete! Processed {len(missing_dates)} dates.")


if __name__ == "__main__":
    main()
