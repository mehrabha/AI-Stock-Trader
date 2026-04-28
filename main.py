from src.data_fetcher import get_price_data, get_news_data_v2, get_market_context
from datetime import datetime

if __name__ == "__main__":
    symbol = "AAPL"
    start_date = "2024-01-01"
    end_date = "2024-01-10"

    start_t = datetime(2026, 1, 6, 14, 30, 0)   # 9:30 AM represented as UTC
    end_t = datetime(2026, 1, 6, 20, 30, 0)     # 3:30 AM represented as UTC

    prices = get_price_data(symbol, start_date, end_date)
    print("PRICE DATA:")
    for item in prices[:3]:
        print(item)

    news = get_news_data_v2(symbol, start_t, end_t) # news api v2

    print(f"\nNEWS DATA: {news}")

    context = get_market_context("SPY", "2026-04-24 14:30:00")
    print(context)