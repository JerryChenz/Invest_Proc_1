from forex_python.converter import CurrencyRates


def get_forex_dict():
    """Retrieve latest CNY/HKD and USD/HKD forex rates using forex_python."""
    c = CurrencyRates()
    return {f"{base}{quote}": c.get_rate(base, quote) for base, quote in [("CNY", "HKD"), ("USD", "HKD")]}


def get_forex_rate(buy, sell):
    """Get exchange rate between buy (base) and sell (target) currency, handling MOP with a hardcoded rate."""
    if buy == sell:
        return 1.0

    MOP_RATE = 0.97
    c = CurrencyRates()

    try:
        if buy == "MOP":
            return MOP_RATE * c.get_rate("HKD", sell)
        elif sell == "MOP":
            return c.get_rate(buy, "HKD") / MOP_RATE
        else:
            return c.get_rate(buy, sell)
    except Exception as e:
        print(f"fx_rate error: {e}")
        return None
