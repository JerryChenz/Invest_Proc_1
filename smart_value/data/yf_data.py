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
