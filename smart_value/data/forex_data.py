import yfinance as yf


def get_forex_dict():
    """Retrieve latest CNY/HKD and USD/HKD forex rates using yfinance."""
    # Define currency pairs
    currency_pairs = ["CNY.HKD=X", "USD.HKD=X"]

    # Download historical data for currency pairs
    data = yf.download(currency_pairs, period="1d")["Close"]

    # Extract latest rates
    latest_rates = data.iloc[-1].to_dict()

    # Format keys to show currency pair
    return {key.replace(".HKD=X", "/HKD"): value for key, value in latest_rates.items()}
