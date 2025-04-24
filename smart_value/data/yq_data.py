from yahooquery import Ticker
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

def get_price_dict(model_paths, max_retries=3, wait_time=10 ):
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

        ticker = Ticker(yahoo_symbol)

        # Retry logic for fetching price data
        price_data = None
        for attempt in range(max_retries):
            try:
                price_data = ticker.price
                break  # Exit retry loop on success
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"Attempt {attempt + 1} failed for {yahoo_symbol}: {str(e)}. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    print(f"Failed to fetch price for {yahoo_symbol} after {max_retries} attempts.")

        # Process price data if fetch was successful
        if price_data is not None:
            if isinstance(price_data, dict):
                quote = price_data.get(yahoo_symbol, {})
            else:
                print(f"Unexpected data format for {yahoo_symbol}: {price_data}")
                quote = {}

            if quote.get('regularMarketPrice'):
                price_dict[symbol] = quote['regularMarketPrice']
            else:
                print(f"Price unavailable for {symbol} (Yahoo: {yahoo_symbol})")
        else:
            print(f"Skipping {symbol} due to fetch failure.")

    return price_dict
