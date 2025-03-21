from yfinance import Ticker, download
import datetime as dt
import time

'''
Available yfinance features:
attrs = [
    'info', 'financials', 'quarterly_financials', 'major_holders',
    'institutional_holders', 'balance_sheet', 'quarterly_balance_sheet',
    'cashflow', 'quarterly_cashflow', 'earnings', 'quarterly_earnings',
    'sustainability', 'recommendations', 'calendar'
]
'''

# Constants
RETRY_ATTEMPTS = 2
RETRY_DELAY = 60
MOP_HKD_RATE = 0.98  # Hardcoded average rate for MOP to HKD
FOREX_DAYS_BACK = 7
FOREX_DAYS_AVERAGE = 3


def get_quote(symbol: str, option: str) -> float | None:
    """Retrieve real-time market data for a given symbol using yfinance's fast_info.

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL')
        option: Data point to retrieve (e.g., 'lastPrice', 'marketCap')

    Returns:
        Requested financial metric or None if unavailable after retries
    """
    for attempt in range(RETRY_ATTEMPTS):
        try:
            return Ticker(symbol).fast_info[option]
        except Exception as e:
            if attempt < RETRY_ATTEMPTS - 1:
                print(f"Attempt {attempt + 1} failed ({e}), retrying in {RETRY_DELAY}s...")
                time.sleep(RETRY_DELAY)
    return None


def get_forex(base_currency: str, quote_currency: str) -> float:
    """Retrieve average forex rate for currency pair using historical data.

    Args:
        base_currency: Base currency code (e.g., 'USD')
        quote_currency: Quote currency code (e.g., 'HKD')

    Returns:
        Average exchange rate from the last three trading days
    """
    # Handle special cases first
    if base_currency == quote_currency:
        return 1.0
    if (base_currency, quote_currency) == ("MOP", "HKD"):
        return MOP_HKD_RATE

    # Calculate date range for historical data
    end_date = dt.date.today()
    start_date = end_date - dt.timedelta(days=FOREX_DAYS_BACK)

    # Fetch and process historical data
    forex_pair = f"{base_currency}{quote_currency}=X"
    historical_data = download(forex_pair, start=start_date, end=end_date)

    return historical_data['Adj Close'].tail(FOREX_DAYS_AVERAGE).mean().item()
