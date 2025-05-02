from yahooquery import Ticker
from smart_value.data.yf_data import get_price_yfinance
import re
import time


def clean_hk_symbol(symbol):
    """Convert HK symbols to 4-digit format required by Yahoo.
    Example: '83.HK' becomes '0083.HK', '0083.HK' remains '0083.HK'.
    """
    if symbol.endswith('.HK'):
        base = symbol[:-3].zfill(4)  # Pad numeric part to 4 digits
        return f'{base}.HK'
    return symbol


def get_price_dict(model_paths, max_retries=3, wait_time=10):
    """Fetch stock prices for given model paths, retrying with yahooquery and falling back to yfinance if necessary."""
    price_dict = {}
    for path in model_paths:
        if not re.search(r'Valuation\.xlsx$', str(path)):
            continue

        # Extract symbol from file path
        symbol_match = re.search(r'(\d{4})\.HK', str(path))
        if not symbol_match:
            continue
        symbol = symbol_match.group(0)
        yahoo_symbol = clean_hk_symbol(symbol)

        price_fetched = False
        for attempt in range(max_retries):
            try:
                ticker = Ticker(yahoo_symbol)
                price_data = ticker.price
                if not isinstance(price_data, dict):
                    raise ValueError(f"Unexpected data format: {price_data}")
                quote = price_data.get(yahoo_symbol)
                if not isinstance(quote, dict):
                    raise ValueError(f"Unexpected quote format: {quote}")
                price = quote.get('regularMarketPrice')
                if price is not None:
                    price_dict[symbol] = price
                    price_fetched = True
                    break
                else:
                    raise ValueError("Price is None")
            except Exception as e:
                if attempt < max_retries - 1:
                    print(
                        f"Attempt {attempt + 1} failed for {yahoo_symbol}: {str(e)}. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    print(
                        f"Failed to fetch price for {yahoo_symbol} after {max_retries} attempts with yahooquery: {str(e)}")

        if not price_fetched:
            print(f"Switching to yfinance for {symbol}")
            price = get_price_yfinance(yahoo_symbol)
            if price is not None:
                price_dict[symbol] = price
            else:
                print(f"Failed to fetch price for {symbol} with yfinance")

    return price_dict
