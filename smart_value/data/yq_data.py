from yahooquery import Ticker
from smart_value.data.yf_data import get_price_yfinance
import os
import time


def get_price_dict(model_paths, max_retries=1, wait_time=10):
    """Fetch stock prices for given model paths using yahooquery in batch,
    falling back to yfinance with retries for failed symbols.

    Args:
        model_paths (list): List of file paths to Excel files.
        max_retries (int): Number of retry attempts for yfinance.
        wait_time (int): Seconds to wait between retries for yfinance.

    Returns:
        dict: Dictionary mapping stock symbols to their current prices.
    """
    price_dict = {}
    suffix = '_Valuation.xlsx'

    # Extract symbols from model_paths
    symbols = []
    for path in model_paths:
        file_name = os.path.basename(str(path))
        if file_name.endswith(suffix):
            symbol = file_name[:-len(suffix)]
            symbols.append(symbol)

    if not symbols:
        print("No valid model files found.")
        return price_dict

    # Batch fetch with yahooquery
    try:
        ticker = Ticker(symbols)
        price_data = ticker.price
        for symbol in symbols:
            quote = price_data.get(symbol)
            if quote and isinstance(quote, dict):
                price = quote.get('regularMarketPrice')
                if isinstance(price, (int, float)):
                    price_dict[symbol] = price
                else:
                    print(f"No valid price for {symbol} from yahooquery")
            else:
                print(f"No data for {symbol} from yahooquery")
    except Exception as e:
        print(f"Batch fetch with yahooquery failed: {str(e)}")
        failed_symbols = symbols
    else:
        failed_symbols = [s for s in symbols if s not in price_dict]

    # Retry failed symbols with yfinance
    print(f"Retry failed symbols, {failed_symbols}, with yfinance")
    for symbol in failed_symbols:
        yahoo_symbol = symbol
        for attempt in range(max_retries):
            try:
                price = get_price_yfinance(yahoo_symbol)
                if price is not None:
                    price_dict[symbol] = price
                    break
                else:
                    raise ValueError("Price is None")
            except Exception as e:
                if attempt < max_retries - 1:
                    print(
                        f"Attempt {attempt + 1} failed for {yahoo_symbol} with yfinance: {str(e)}. "
                        f"Retrying in {wait_time} seconds..."
                    )
                    time.sleep(wait_time)
                else:
                    print(
                        f"Failed to fetch price for {yahoo_symbol} after {max_retries} "
                        f"attempts with yfinance: {str(e)}"
                    )

    return price_dict
