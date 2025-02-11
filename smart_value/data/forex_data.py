from forex_python.converter import CurrencyRates
from smart_value.data import yf_data as yf


def get_forex_dict():
    """Retrieve the latest forex data, return the forex dict"""

    forex_dict = {"CNYHKD": yf.get_forex("CNY", "HKD"),
                  "USDHKD": yf.get_forex("USD", "HKD")}

    return forex_dict


def get_forex_rate(buy, sell):
    """get exchange rate, buy means ask and sell means bid

    :param buy: report currency
    :param sell: price currency
    """

    try:
        if buy != sell:
            c = CurrencyRates()
            return c.get_rate(buy, sell)
        elif buy == "HKD" and sell == "MOP":
            return 0.97  # MOP to HKD not available
        else:
            return 1
    except:
        print("fx_rate error: Currency Rates Not Available")
        # will return None
