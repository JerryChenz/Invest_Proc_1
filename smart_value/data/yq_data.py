from yahooquery import Ticker
import re


def clean_hk_symbol(symbol):
    """Convert HK symbols to 4-digit format required by Yahoo.
    Example: '83.HK' becomes '0083.HK', '0083.HK' remains '0083.HK'.
    """
    if symbol.endswith('.HK'):
        base = symbol[:-3].zfill(4)  # Pad numeric part to 4 digits
        return f'{base}.HK'
    return symbol


def get_price_dict(model_paths):
    price_dict = {}
    for path in model_paths:
        try:
            if not re.search(r'Valuation\.xlsx$', str(path)):
                continue

            # Extract symbol from file path
            symbol_match = re.search(r'(\d{4})\.HK', str(path))
            if not symbol_match:
                continue
            symbol = symbol_match.group(0)
            yahoo_symbol = clean_hk_symbol(symbol)

            ticker = Ticker(yahoo_symbol)
            price_data = ticker.price

            # Check if price_data is a dictionary
            if isinstance(price_data, dict):
                quote = price_data.get(yahoo_symbol, {})
            else:
                print(f"Unexpected data format for {yahoo_symbol}: {price_data}")
                quote = {}

            if quote.get('regularMarketPrice'):
                price_dict[symbol] = quote['regularMarketPrice']
            else:
                print(f"Price unavailable for {symbol} (Yahoo: {yahoo_symbol})")

        except Exception as e:
            print(f"Error processing {path}: {str(e)}")

    return price_dict
