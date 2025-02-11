import smart_value.tools.macro_monitor as macro_monitor
from smart_value.data import yf_data as yf
from smart_value.data.yq_data import get_price

model_pos = {
    # Left side of the company info
    "symbol": "C3",
    "name": "C4",
    "last_revision": "C5",
    "next_review": "D6",
    "watchlist": "C7",
    "comp_group": "D7",
    # Right side of the company info
    "is_hold": "G2",
    "price": "G3",
    "price_currency": "H3",
    "shares_outstanding": "G4",
    "report_currency": "G6",
    "fx_rate": "G7",
    # US market yields
    "us_riskfree": "C10",
    "us_bbb_yield": "C11",
    "us_required_return": "C12",
    # China market yields
    "cn_riskfree": "C14",
    "cn_on_bbb_yield": "C15",
    "cn_off_bbb_yield": "C16",
    "cn_required_return": "C17",
    # HK and other market yields
    "hk_required_return": "D12",
    "other_required_return": "D17",
    "target_return": "G20",
    "investment_horizon": "H20",
    # ROE & Cost Structure
    "ROE": 'C20',
    "EBIT_Margin": 'C21',
    "Leverage_ratio": 'C23',
    "Asset_Turnover": 'C22',
    "interest": 'C24',
    "change_of_wc": 'C25',
    "mcx": 'C26',
    # Price Indicators
    "pb_ratio": 'G23',
    "ep_ratio": 'G24',
    "payout_ratio": 'G25',
    "dp_ratio": 'G26',
    # Valuation
    "lower_value": 'C29',
    "upper_value": 'D29',
    "value": 'F29'
}


def update_dash_marco(dash_sheet):
    """Update the marco parameters of the Dashboard sheet.

    :param dash_sheet: the xlwings object of the dashboard sheet in the model
    """

    marco = macro_monitor.read_marco()
    dash_sheet.range(model_pos["us_riskfree"]).value = marco.us_riskfree
    dash_sheet.range(model_pos["us_bbb_yield"]).value = marco.us_bbb_yield
    dash_sheet.range(model_pos["us_required_return"]).value = marco.us_required_return
    dash_sheet.range(model_pos["cn_riskfree"]).value = marco.cn_riskfree
    dash_sheet.range(model_pos["cn_on_bbb_yield"]).value = marco.cn_on_bbb_yield
    dash_sheet.range(model_pos["cn_off_bbb_yield"]).value = marco.cn_off_bbb_yield
    dash_sheet.range(model_pos["cn_required_return"]).value = marco.cn_required_return
    dash_sheet.range(model_pos["hk_required_return"]).value = marco.hk_required_return
    dash_sheet.range(model_pos["other_required_return"]).value = marco.other_required_return
    dash_sheet.range(model_pos["target_return"]).value = marco.target_return
    dash_sheet.range(model_pos["investment_horizon"]).value = marco.investment_horizon


def update_dash_market(dash_sheet, forex_dict, price_dict):
    """Update the price and forex parameters of the Dashboard sheet.

    :param dash_sheet: the xlwings object of the dashboard sheet in the model
    :param forex_dict: forex dictionary contains the updated forex rates
    :param price_dict: price dictionary contains the updated stock prices
    """

    price_data = get_price(dash_sheet.range(model_pos["symbol"]).value, price_dict)
    dash_sheet.range(model_pos["price"]).value = price_data[0]  # Stock price
    price_currency = price_data[1]
    report_currency = dash_sheet.range(model_pos["report_currency"]).value
    dash_sheet.range(model_pos["price_currency"]).value = price_currency

    forex_str = report_currency + price_currency
    if forex_str in forex_dict:
        dash_sheet.range(model_pos["fx_rate"]).value = forex_dict[forex_str]
    elif report_currency == price_currency:
        dash_sheet.range(model_pos["fx_rate"]).value = 1
    else:  # Use the better yfinance Forex
        print("updating Forex rate...")
        dash_sheet.range(model_pos["fx_rate"]).value = yf.get_forex(report_currency, price_currency)
