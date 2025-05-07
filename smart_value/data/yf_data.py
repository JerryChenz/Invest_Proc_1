import yfinance as yf

'''
Available yfinance features:
attrs = [
    'info', 'financials', 'quarterly_financials', 'major_holders',
    'institutional_holders', 'balance_sheet', 'quarterly_balance_sheet',
    'cashflow', 'quarterly_cashflow', 'earnings', 'quarterly_earnings',
    'sustainability', 'recommendations', 'calendar'
]
'''


def get_price_yfinance(symbol):
    """Fetch stock price using yfinance as a fallback."""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        return info.get('regularMarketPrice')
    except Exception as e:
        print(f"Error fetching price for {symbol} with yfinance: {e}")
        return None


def get_rate_from_yfinance(from_currency, to_currency):
    ticker_direct = f"{from_currency}{to_currency}=X"
    ticker_inverse = f"{to_currency}{from_currency}=X"
    try:
        data = yf.Ticker(ticker_direct)
        hist = data.history(period="1d")
        if not hist.empty:
            rate = hist['Close'].iloc[-1]
            return rate
        # Try inverse
        data = yf.Ticker(ticker_inverse)
        hist = data.history(period="1d")
        if hist.empty:
            raise ValueError(f"No data for {ticker_direct} or {ticker_inverse}")
        rate = 1 / hist['Close'].iloc[-1]
        return rate
    except Exception as e:
        raise ValueError(f"Failed to get rate from yfinance for {from_currency}{to_currency}: {str(e)}")
