import requests
from datetime import datetime, timedelta
from smart_value.data.yf_data import get_rate_from_yfinance


def get_fallback_rate(from_currency: str, to_currency: str) -> float:
    """Hardcoded fallback rates for critical pairs"""
    fallback_rates = {
        "HKDHKD": 1.0,
        "CNYHKD": 1.07,     # ≈ 1 CNY = 1.07 HKD
        "USDHKD": 7.8,
        "HKDUSD": 1 / 7.8,
        "USDCNY": 7.22,
        "CNYUSD": 1 / 7.22,
    }
    key = f"{from_currency.upper()}{to_currency.upper()}"
    return fallback_rates.get(key, 1.0)


class ForexData:
    def __init__(self):
        self.cache = {}
        self.cache_expiration = timedelta(hours=1)

    def _fetch_rate_from_api(self, base: str, target: str) -> float:
        """Fetch all rates with base currency from exchangerate-api"""
        url = f"https://open.er-api.com/v6/latest/{base}"

        try:
            r = requests.get(url, timeout=(3, 5))
            r.raise_for_status()
            data = r.json()

            if data.get("result") != "success":
                raise RuntimeError(f"API returned failure: {data}")

            rates = data.get("rates", {})
            now = datetime.now()

            # Cache all returned rates + inverses
            for currency, value in rates.items():
                fwd_key = f"{base}{currency}"
                rev_key = f"{currency}{base}"
                rate = float(value)

                self.cache[fwd_key] = {"rate": rate, "timestamp": now}
                if rate != 0:
                    self.cache[rev_key] = {"rate": 1.0 / rate, "timestamp": now}

            if target not in rates:
                raise KeyError(f"Target currency {target} not found in response")

            return float(rates[target])

        except Exception as e:
            raise RuntimeError(f"exchangerate API failed for {base}->{target}: {e}")

    def get_rate(self, from_currency: str, to_currency: str) -> float:
        """
        Returns exchange rate from_currency → to_currency (how many to_currency per 1 from_currency)
        Returns 1.0 if from_currency == to_currency
        """
        # Normalize currency codes
        base = from_currency.upper()
        target = to_currency.upper()

        print(f"get_rate  {base} → {target}")

        if base == target:
            return 1.0

        cache_key = f"{base}{target}"
        inverse_key = f"{target}{base}"
        now = datetime.now()

        # Check cache (forward or inverse)
        for key in (cache_key, inverse_key):
            if key in self.cache:
                entry = self.cache[key]
                if now - entry["timestamp"] < self.cache_expiration:
                    rate = entry["rate"] if key == cache_key else 1.0 / entry["rate"]
                    # Update both directions while we're here
                    self.cache[cache_key] = {"rate": rate, "timestamp": entry["timestamp"]}
                    self.cache[inverse_key] = {"rate": 1.0 / rate, "timestamp": entry["timestamp"]}
                    return rate

        # Try primary source
        try:
            rate = self._fetch_rate_from_api(base, target)
            print(f"API success {base}{target}")
        except Exception as api_err:
            print(f"API failed {base}{target}: {api_err}")

            # Try yfinance
            try:
                rate = get_rate_from_yfinance(base, target)
                print(f"yfinance success {base}{target}")
            except Exception as yf_err:
                print(f"yfinance failed {base}{target}: {yf_err}")

                # Last resort: hardcoded fallback
                rate = get_fallback_rate(base, target)
                print(f"Using fallback {base}{target} = {rate}")

        # Cache the result
        self.cache[cache_key] = {"rate": rate, "timestamp": now}
        self.cache[inverse_key] = {"rate": 1.0 / rate, "timestamp": now}

        return rate
