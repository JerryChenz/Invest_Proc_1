import os
import time
from datetime import datetime, timedelta
from alpha_vantage.foreignexchange import ForeignExchange


class ForexData:
    def __init__(self):
        self.api_key = os.getenv('ALPHA_VANTAGE_API_KEY', 'KSZMAKF6SIRDVE1Y')
        self.fx = ForeignExchange(key=self.api_key)
        self.cache = {}
        self.cache_expiration = timedelta(hours=1)

    def get_rate(self, from_currency, to_currency):
        """Get exchange rate with retry logic and cache."""
        if from_currency == to_currency:
            return 1.0

        cache_key = f"{from_currency}{to_currency}"
        if cache_key in self.cache:
            if datetime.now() - self.cache[cache_key]['timestamp'] < self.cache_expiration:
                return self.cache[cache_key]['rate']

        max_retries = 3
        for attempt in range(max_retries):
            try:
                if from_currency == 'USD' or to_currency == 'USD':
                    data, _ = self.fx.get_currency_exchange_rate(
                        from_currency=from_currency,
                        to_currency=to_currency
                    )
                    rate = float(data['5. Exchange Rate'])
                else:
                    # Calculate cross rate via USD
                    usd_from = self.get_rate(from_currency, 'USD')
                    usd_to = self.get_rate('USD', to_currency)
                    rate = usd_from * usd_to

                self.cache[cache_key] = {
                    'rate': rate,
                    'timestamp': datetime.now()
                }
                return rate

            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"Failed to get {from_currency}{to_currency} after {max_retries} attempts: {str(e)}")
                    return self.get_fallback_rate(from_currency, to_currency)
                time.sleep(2 ** attempt)

    def get_fallback_rate(self, from_currency, to_currency):
        """Fallback rates for critical currency pairs"""
        fallback_rates = {
            'HKDHKD': 1.0,
            'CNYHKD': 0.86,
            'USDHKD': 7.8,
            'CNYUSD': 6.7,
            'USDCNY': 1 / 6.7,
            'HKDUSD': 1 / 7.8
        }
        return fallback_rates.get(f"{from_currency}{to_currency}", 1.0)


def get_forex_dict():
    """Return a dictionary with common currency pairs for Hong Kong/China stocks"""
    forex = ForexData()
    return {
        'HKDHKD': forex.get_rate('HKD', 'HKD'),  # Will return 1.0
        'CNYHKD': forex.get_rate('CNY', 'HKD'),
        'USDHKD': forex.get_rate('USD', 'HKD'),
        'HKDUSD': forex.get_rate('HKD', 'USD'),
        'CNYUSD': forex.get_rate('CNY', 'USD'),
        'USDCNY': forex.get_rate('USD', 'CNY')
    }
