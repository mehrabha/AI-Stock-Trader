import os
from typing import List, Dict, Any

import requests
import yfinance as yf
from dotenv import load_dotenv

load_dotenv()


def get_price_data(symbol: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
    """
    Fetch historical price data for a given symbol between start_date and end_date.
    Returns a list of dictionaries with date, open, high, low, close, volume.
    """
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(start=start_date, end=end_date)

        if hist.empty:
            return []

        hist = hist.reset_index()

        results = []
        for _, row in hist.iterrows():
            results.append({
                "date": row["Date"].strftime("%Y-%m-%d"),
                "open": float(row["Open"]),
                "high": float(row["High"]),
                "low": float(row["Low"]),
                "close": float(row["Close"]),
                "volume": int(row["Volume"]),
            })

        return results

    except Exception as e:
        print(f"Error fetching price data for {symbol}: {e}")
        return []


def get_news_data(symbol: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
    """
    Fetch news articles related to a symbol between start_date and end_date.
    Returns a list of dictionaries with date, title, summary, source.
    """
    api_key = os.getenv("NEWS_API_KEY")

    if not api_key:
        print("NEWS_API_KEY not found. Returning empty news list.")
        return []

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": symbol,
        "from": start_date,
        "to": end_date,
        "sortBy": "publishedAt",
        "language": "en",
        "apiKey": api_key,
        "pageSize": 10,
    }

    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        articles = data.get("articles", [])
        results = []

        for article in articles:
            results.append({
                "date": article.get("publishedAt", "")[:10],
                "title": article.get("title", ""),
                "summary": article.get("description", ""),
                "source": article.get("source", {}).get("name", ""),
            })

        return results

    except Exception as e:
        print(f"Error fetching news data for {symbol}: {e}")
        return []