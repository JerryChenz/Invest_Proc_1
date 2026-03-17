import requests
from datetime import datetime, timedelta
from smart_value.data.yf_data import get_rate_from_yfinance


def get_fallback_rate(from_currency, to_currency):
    """Fallback rates for critical currency pairs"""
    fallback_rates = {
        "HKDHKD": 1.0,
        "CNYHKD": 1.07,
        "USDHKD": 7.8,
        "CNYUSD": 1 / 7.22,
        "USDCNY": 7.22,
        "HKDUSD": 1 / 7.8,
    }
    return fallback_rates.get(
        f"{from_currency}{to_currency}", 1.0
    )


class ForexData:

    def __init__(self):

        self.cache = {}
        self.cache_expiration = timedelta(hours=1)

    # ----------------------------
    # exchangerate.host API
    # ----------------------------

    def _fetch_rate_from_api(
        self,
        from_currency,
        to_currency,
    ):

        url = "https://api.exchangerate.host/convert"

        params = {
            "from": from_currency,
            "to": to_currency,
        }

        r = requests.get(
            url,
            params=params,
            timeout=10,
        )

        r.raise_for_status()

        data = r.json()

        if "result" not in data:
            raise RuntimeError(data)

        return float(data["result"])

    # ----------------------------
    # main
    # ----------------------------

    def get_rate(
        self,
        from_currency,
        to_currency,
    ):

        if from_currency == to_currency:
            return 1.0

        cache_key = f"{from_currency}{to_currency}"
        inverse_key = f"{to_currency}{from_currency}"

        now = datetime.now()

        # ------------------------
        # cache
        # ------------------------

        for key in [cache_key, inverse_key]:

            if key in self.cache:

                entry = self.cache[key]

                if (
                    now - entry["timestamp"]
                    < self.cache_expiration
                ):

                    rate = (
                        entry["rate"]
                        if key == cache_key
                        else 1.0 / entry["rate"]
                    )

                    self.cache[cache_key] = {
                        "rate": rate,
                        "timestamp": entry["timestamp"],
                    }

                    self.cache[inverse_key] = {
                        "rate": 1.0 / rate,
                        "timestamp": entry["timestamp"],
                    }

                    return rate

        # ------------------------
        # exchangerate.host
        # ------------------------

        try:

            rate = self._fetch_rate_from_api(
                from_currency,
                to_currency,
            )

        except Exception as e:

            print(
                f"EXCHANGERATE.HOST failed "
                f"{from_currency}{to_currency}: {e}"
            )

            # ------------------------
            # yfinance fallback
            # ------------------------

            try:

                rate = get_rate_from_yfinance(
                    from_currency,
                    to_currency,
                )

                print(
                    f"yfinance OK "
                    f"{from_currency}{to_currency}"
                )

            except Exception as e:

                print(
                    f"yfinance failed "
                    f"{from_currency}{to_currency}: {e}"
                )

                # ------------------------
                # hardcoded fallback
                # ------------------------

                rate = get_fallback_rate(
                    from_currency,
                    to_currency,
                )

                print(
                    f"fallback used "
                    f"{from_currency}{to_currency}"
                )

        # ------------------------
        # update cache
        # ------------------------

        self.cache[cache_key] = {
            "rate": rate,
            "timestamp": now,
        }

        self.cache[inverse_key] = {
            "rate": 1.0 / rate,
            "timestamp": now,
        }

        return rate
