import os
import time
from datetime import datetime, timedelta
from alpha_vantage.foreignexchange import ForeignExchange
import yfinance as yf


def get_fallback_rate(from_currency, to_currency):
    """Fallback rates for critical currency pairs"""
    fallback_rates = {
        'HKDHKD': 1.0,
        'CNYHKD': 1.07,
        'USDHKD': 7.8,
        'CNYUSD': 1 / 7.22,
        'USDCNY': 7.22,
        'HKDUSD': 1 / 7.8
    }
    return fallback_rates.get(f"{from_currency}{to_currency}", 1.0)


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


class ForexData:
    def __init__(self):
        self.api_key = os.getenv('ALPHA_VANTAGE_API_KEY', 'KSZMAKF6SIRDVE1Y')
        self.fx = ForeignExchange(key=self.api_key)
        self.cache = {}
        self.cache_expiration = timedelta(hours=1)

    def get_rate(self, from_currency, to_currency):
        """Get exchange rate with caching, using inverse rates when possible."""
        if from_currency == to_currency:
            return 1.0

        cache_key = f"{from_currency}{to_currency}"
        inverse_cache_key = f"{to_currency}{from_currency}"
        now = datetime.now()

        # Check cache for direct or inverse rate
        for key in [cache_key, inverse_cache_key]:
            if key in self.cache:
                entry = self.cache[key]
                if now - entry['timestamp'] < self.cache_expiration:
                    rate = entry['rate'] if key == cache_key else 1.0 / entry['rate']
                    # Update both keys in cache to optimize future requests
                    self.cache[cache_key] = {'rate': rate, 'timestamp': entry['timestamp']}
                    self.cache[inverse_cache_key] = {'rate': 1.0 / rate, 'timestamp': entry['timestamp']}
                    return rate

        # If not found in cache, proceed to fetch rate
        if from_currency == 'USD' or to_currency == 'USD':
            try:
                data, _ = self.fx.get_currency_exchange_rate(
                    from_currency=from_currency,
                    to_currency=to_currency
                )
                rate = float(data['5. Exchange Rate'])
            except Exception as e:
                print(f"Alpha Vantage failed for {from_currency}{to_currency}: {str(e)}")
                try:
                    rate = get_rate_from_yfinance(from_currency, to_currency)
                except Exception as e:
                    print(f"yfinance failed for {from_currency}{to_currency}: {str(e)}")
                    rate = get_fallback_rate(from_currency, to_currency)
        else:
            # Calculate cross rate via USD
            usd_from = self.get_rate(from_currency, 'USD')
            usd_to = self.get_rate('USD', to_currency)
            rate = usd_from * usd_to

        # Update cache with both direct and inverse rates
        self.cache[cache_key] = {'rate': rate, 'timestamp': now}
        self.cache[inverse_cache_key] = {'rate': 1.0 / rate, 'timestamp': now}
        return rate
