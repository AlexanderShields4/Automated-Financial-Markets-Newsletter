#!/usr/bin/env python3

import argparse
import pandas as pd
import requests
import sys
import yfinance as yf
from datetime import datetime, timedelta
import os
from fredapi import Fred
from google import genai
from dotenv import load_dotenv
import unicodedata
from supabase import create_client

def main(target_date=None):
    load_dotenv()
    
    # Initialize Supabase
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    if not supabase_url or not supabase_key:
        print("Error: SUPABASE_URL and SUPABASE_SERVICE_KEY are required in .env")
        return
    supabase = create_client(supabase_url, supabase_key)

    # Initialize FRED API
    fred = Fred(api_key=os.getenv("fred_api_key"))
    
    # Get dates
    today = target_date if target_date is not None else datetime.now().date()
    start_date = today - timedelta(days=7)
    
    # Get Treasury yield curve data
    yield_curves = {
        '3M': 'DGS3MO',
        '6M': 'DGS6MO',
        '1Y': 'DGS1',
        '2Y': 'DGS2',
        '3Y': 'DGS3',
        '5Y': 'DGS5',
        '7Y': 'DGS7',
        '10Y': 'DGS10',
        '20Y': 'DGS20',
        '30Y': 'DGS30'
    }
    
    # Get historical data for each tenor
    yield_data = {}
    spread_series = {}
    for tenor, series_id in yield_curves.items():
        try:
            series = fred.get_series(series_id, observation_start=start_date, observation_end=today)
            # Convert timestamps to string format
            yield_data[tenor] = {date.strftime('%Y-%m-%d'): value 
                               for date, value in series.to_dict().items()}
            spread_series[tenor] = series
        except Exception as e:
            print(f"Error fetching {series_id}: {e}")
    
    # Calculate important spreads
    spreads = {}
    spread_calcs = {
        '10Y-2Y': (spread_series['10Y'] - spread_series['2Y']),  # Classic recession indicator
        '10Y-3M': (spread_series['10Y'] - spread_series['3M']),  # Fed's preferred spread
        '30Y-5Y': (spread_series['30Y'] - spread_series['5Y']),  # Long-term growth expectations
        '5Y-2Y': (spread_series['5Y'] - spread_series['2Y'])  # Medium-term expectations
    }
    # print(spread_calcs) # Debug print removed

    for name, series in spread_calcs.items():
        spreads[name] = {date.strftime('%Y-%m-%d'): value 
                        for date, value in series.to_dict().items()}
    
  
    tenyrtwoyr = [] #the ten year two year spread list 
    for date, value in spreads['10Y-2Y'].items():
        if pd.notnull(value):
            tenyrtwoyr.append(f"{date}: {value:.2f}")
    tenthreem = [] # the ten three month spread list 
    for date, value in spreads['10Y-3M'].items():
        if pd.notnull(value): 
            tenthreem.append(f"{date}: {value:.2f}")
    thirtyfivey= [] #the thirty five year spread list
    for date, value in spreads['30Y-5Y'].items():
        if pd.notnull(value):
            thirtyfivey.append(f"{date}: {value:.2f}")
    fiveytwoyr = []  # the five two year spread list 
    for date, value in spreads['5Y-2Y'].items():    
        if pd.notnull(value):
            fiveytwoyr.append(f"{date}: {value:.2f}")

    # Determine latest available dates for spreads/yields so we can report them
    try:
        latest_spread_date = max(*(list(s.keys()) for s in spreads.values()))
    except Exception:
        # fallback: inspect one spread series
        latest_spread_date = max(spreads.get('10Y-2Y', {}).keys()) if spreads.get('10Y-2Y') else str(today)
     # Get economic indicators
    economic_indicators = {
        'Initial Jobless Claims': 'ICSA',
        'CPI': 'CPIAUCSL',
        'PPI': 'PPIACO',
        'Retail Sales': 'RSAFS',
        'Durable Goods Orders': 'DGORDER',  # Manufacturers New Orders: Durable Goods
        'Consumer Confidence': 'UMCSENT',  # University of Michigan Consumer Sentiment
        'Industrial Production': 'INDPRO',  # Industrial Production Index
        'Housing Starts': 'HOUST',  # New Privately-Owned Housing Units Started
        'GDP Growth Rate': 'A191RL1Q225SBEA'  # Real GDP Growth Rate
    }
    
    latest_economic_data = {}
    for indicator_name, series_id in economic_indicators.items():
        try:
            series = fred.get_series(series_id, observation_start=start_date, observation_end=today)
            if not series.empty:
                latest_date = series.index[-1]
                latest_value = series.iloc[-1]
                latest_economic_data[indicator_name] = f"{latest_date.strftime('%Y-%m-%d')}: {latest_value:.2f}"
        except Exception as e:
            print(f"Error fetching {series_id}: {e}")
    

    # Get stock data
    tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA"]
    data = yf.download(tickers, start=start_date, end=today + timedelta(days=1), interval="1d", group_by='ticker')
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
                    # track latest ticker data date
                    if latest_ticker_date is None or date_str > latest_ticker_date:
                        latest_ticker_date = date_str
                    ticker_data += f"{ticker} {date_str}: Open: ${open_price:.2f} Close: ${close_price:.2f}. "
    
    # Get market indices
    indices = [
        "^GSPC", "^DJI", "^IXIC", "^RUT",
        "^VIX",
        "CL=F", "BZ=F",
        "GC=F",
        "DX-Y.NYB"
    ]
    
    data = yf.download(indices, start=today, end=today + timedelta(days=1), interval="1d", group_by='ticker')
    
    symbol_names = {
        "^GSPC": "S&P 500",
        "^DJI": "Dow Jones",
        "^IXIC": "NASDAQ",
        "^RUT": "Russell 2000",
        "^VIX": "VIX",
        "CL=F": "WTI Crude",
        "BZ=F": "Brent Crude",
        "GC=F": "Gold",
        "DX-Y.NYB": "US Dollar Index"
    }
    
    indice_data_str = ""
    for index in indices:
        try:
            # Handle potential MultiIndex columns from yfinance
            if isinstance(data.columns, pd.MultiIndex):
                # Try to access using the ticker level
                try:
                    if index not in data.columns.levels[0]:
                         # Ticker not in the downloaded data at all
                         continue
                    
                    ticker_df = data[index]
                    
                    if ticker_df.empty or pd.isna(ticker_df['Open'].iloc[0]):
                        # print(f"No data available for {index}") # Optional logging
                        continue
                        
                    open_price = ticker_df['Open'].iloc[0]
                    close_price = ticker_df['Close'].iloc[0]
                except KeyError:
                    print(f"Could not find data for {index}")
                    continue
            else:
                 # If not multi-index, check if 'Open' exists
                 if 'Open' not in data.columns or data.empty:
                     continue
                 open_price = data['Open'].iloc[0]
                 close_price = data['Close'].iloc[0]

            name = symbol_names.get(index, index)
            # converting to float to avoid series printing issues
            open_val = float(open_price)
            close_val = float(close_price)
            
            indice_data = f"{name}: Open: {open_val:.2f} Close: {close_val:.2f}"
            indice_data_str += indice_data + '. '
        except (KeyError, IndexError, ValueError) as e:
            # print(f"Error getting data for {index}: {e}")
            pass
            # Continue anyway
    
    # Get news
    API_KEY = os.getenv("NewsApikey")
    yesterday = today - timedelta(days=1)
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
        "to": today.isoformat(),
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 100,
        "apiKey": API_KEY
    }
    
    all_articles = []
    newsstr = f"\n📰 Broad Market News for {today}:\n"
    
    for query in queries:
        print(f"Fetching news for query: {query}")
        params = base_params.copy()
        params["q"] = query
        
        response = requests.get(url, params=params)
        if response.status_code != 200:
            print(f"Error {response.status_code} for query '{query}':", response.json().get("message"))
            continue
            
        data = response.json()
        if data.get("status") == "ok":
            articles = data.get("articles", [])
            all_articles.extend(articles)
        else:
            print(f"Failed to fetch articles for query '{query}':", data.get("message"))
    
    for i, article in enumerate(all_articles):
        title = article['title']
        source = article['source']['name']
        url = article['url']
        newsstr += f"{i}. {title}   Source: {source}  URL: {url}\n"
        if i >= 40:
            break
    
    # Structure market data
    market_data = {
        'tenyrtwoyr': tenyrtwoyr,
        'indice_data_str': indice_data_str,
        'ticker_data': ticker_data,
        'newsstr': newsstr,
        'economic_indicators': latest_economic_data,
        'yield_data': yield_data,
        'yield_spreads': spreads
    }
    
    # Generate daily writeup
    data_date_notes = (
        f"Latest available spread data date: {latest_spread_date}.\n"
        f"Latest available ticker data date: {latest_ticker_date or 'N/A'}.\n"
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
    f"Data for analysis (Date: {today}):\n"
    f"Note on data currency:\n{data_date_notes}\n"
    f"— Last 5 days of 10-Year minus 2-Year Treasury yield spread, the 30 yr five yr spread, the ten three month spread and the five year 2 yr spread: {tenyrtwoyr,thirtyfivey, tenthreem, fiveytwoyr}\n"
        f"— Market indices and indicators: {indice_data_str}\n"
        f"— Magnificent 7 stock prices (last seven days, daily open and close): {ticker_data}\n"
        f"— Economic releases from FRED: \n"
        f"— Market news headlines (past 24h): {newsstr}\n"
        f"create a nicely formatted table summarizing key numerical data (excluding news headlines). All of this information should be suitable for the syntax and style of the streamlit application\n\n"

    )
    
    client = genai.Client(api_key=os.getenv("GOOGLE_KEY"))
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=message
    ) 
    newsletter_text = str(response.text)
    newsletter_text = unicodedata.normalize("NFKD", newsletter_text)

    # --- SUPABASE UPSERT ---
    print("Generating embedding for the newsletter...")
    embed_response = client.models.embed_content(
        model="models/gemini-embedding-001",
        contents=newsletter_text,
        config={"output_dimensionality": 768}
    )
    vector = embed_response.embeddings[0].values
    
    # Sanitize data for JSON compliance
    def clean_json_data(obj):
        if isinstance(obj, float):
            return None if pd.isna(obj) or obj == float('inf') or obj == float('-inf') else obj
        elif isinstance(obj, dict):
            return {k: clean_json_data(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [clean_json_data(v) for v in obj]
        return obj

    data_payload = clean_json_data({
        "date": str(today),
        "full_text": newsletter_text,
        "structured_data": market_data,
        "embedding": vector
    })
    
    try:
        data = supabase.table("daily_briefs").upsert(data_payload, on_conflict="date").execute()
        print("Successfully saved to Supabase!")
    except Exception as e:
        print(f"Error saving to Supabase: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Collect market data and generate newsletter")
    parser.add_argument("--date", type=lambda s: datetime.strptime(s, "%Y-%m-%d").date(),
                        default=None, help="Target date in YYYY-MM-DD format (default: today)")
    args = parser.parse_args()
    main(target_date=args.date)
