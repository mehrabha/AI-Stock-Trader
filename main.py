from data_fetcher import get_price_data, get_news_data

if __name__ == "__main__":
    symbol = "SPY"
    start_date = "2024-01-01"
    end_date = "2024-01-10"

    prices = get_price_data(symbol, start_date, end_date)
    print("PRICE DATA:")
    for item in prices[:3]:
        print(item)

    news = get_news_data(symbol, start_date, end_date)
    print("\nNEWS DATA:")
    for item in news[:3]:
        print(item)