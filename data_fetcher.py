import os
from typing import List, Dict, Any

import requests
import yfinance as yf
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()


def _format_price_points(rows, max_points: int) -> str:
    if rows.empty:
        return "No data available."

    rows = rows.tail(max_points)

    price_parts = []
    for idx, row in rows.iterrows():
        if hasattr(idx, "strftime"):
            label = idx.strftime("%Y-%m-%d %H:%M") if max_points == 7 else idx.strftime("%Y-%m-%d")
        else:
            label = str(idx)
        close = float(row["Close"])
        price_parts.append(f"{label}: ${close:.2f}")

    last_row = rows.iloc[-1]
    trend = float(last_row["TrendPct"])
    ma = float(last_row["MA"])
    direction = "up" if trend >= 0 else "down"

    summary = f"trend {direction} {abs(trend):.2f}%, MA ${ma:.2f}"

    return " | ".join(price_parts) + f" | {summary}"

def _add_trend_and_ma(df, ma_window: int = 3):
    """
    Adds moving average and percent trend from first available close.
    """
    if df.empty:
        return df

    df = df.copy()
    df["MA"] = df["Close"].rolling(window=ma_window, min_periods=1).mean()
    first_close = df["Close"].iloc[0]
    df["TrendPct"] = ((df["Close"] - first_close) / first_close) * 100
    return df


def get_market_context(ticker: str, timestamp: str) -> str:
    """
    Builds compact market context for an LLM.

    timestamp format example:
    "2024-04-18 14:30:00"

    Returns:
    Current Market Context for SPY:
    - Intraday: ...
    - This Week: ...
    - Last Month: ...
    - 12 months: ...
    """

    current_time = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    ticker_obj = yf.Ticker(ticker)

    # 1. Intraday: hourly pricing since market opened, up to 7 prices
    market_open = current_time.replace(hour=9, minute=30, second=0, microsecond=0)

    intraday = ticker_obj.history(
        start=market_open,
        end=current_time,
        interval="60m"
    )

    intraday = _add_trend_and_ma(intraday)
    hourly_string = _format_price_points(intraday, max_points=7)

    # 2. This week: daily prices, up to 5 business days
    week_start = current_time - timedelta(days=current_time.weekday())

    daily = ticker_obj.history(
        start=week_start,
        end=current_time,
        interval="1d"
    )

    daily = _add_trend_and_ma(daily)
    daily_string = _format_price_points(daily, max_points=5)

    # 3. Last month: 4 price points
    last_month_start = current_time - timedelta(days=30)

    weekly = ticker_obj.history(
        start=last_month_start,
        end=current_time,
        interval="1wk"
    )

    weekly = _add_trend_and_ma(weekly)
    weekly_string = _format_price_points(weekly, max_points=4)

    # 4. Since January / 12 months: up to 12 monthly points
    twelve_month_start = current_time - timedelta(days=365)

    monthly = ticker_obj.history(
        start=twelve_month_start,
        end=current_time,
        interval="1mo"
    )

    monthly = _add_trend_and_ma(monthly)
    monthly_string = _format_price_points(monthly, max_points=12)

    market_context = f"""
Current Market Context for {ticker}:
- Intraday: {hourly_string}
- This Week: {daily_string}
- Last Month: {weekly_string}
- 12 months: {monthly_string}
""".strip()

    return market_context

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