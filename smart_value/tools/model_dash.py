import smart_value.tools.macro_monitor as macro_monitor
from smart_value.data import yf_data as yf
from smart_value.data.yq_data import get_price
from smart_value.data.model_data import thesis_pos


def update_dash_marco(dash_sheet):
    """Update the marco parameters of the Dashboard sheet.

    :param dash_sheet: the xlwings object of the dashboard sheet in the model
    """

    marco = macro_monitor.read_marco()
    dash_sheet.range(thesis_pos["us_riskfree"]).value = marco.us_riskfree
    dash_sheet.range(thesis_pos["us_bbb_yield"]).value = marco.us_bbb_yield
    dash_sheet.range(thesis_pos["us_required_return"]).value = marco.us_required_return
    dash_sheet.range(thesis_pos["cn_riskfree"]).value = marco.cn_riskfree
    dash_sheet.range(thesis_pos["cn_on_bbb_yield"]).value = marco.cn_on_bbb_yield
    dash_sheet.range(thesis_pos["cn_off_bbb_yield"]).value = marco.cn_off_bbb_yield
    dash_sheet.range(thesis_pos["cn_required_return"]).value = marco.cn_required_return
    dash_sheet.range(thesis_pos["hk_required_return"]).value = marco.hk_required_return
    dash_sheet.range(thesis_pos["other_required_return"]).value = marco.other_required_return
    dash_sheet.range(thesis_pos["target_return"]).value = marco.target_return
    dash_sheet.range(thesis_pos["investment_horizon"]).value = marco.investment_horizon


def update_dash_market(dash_sheet, forex_dict, price_dict):
    """Update the price and forex parameters of the Dashboard sheet.

    :param dash_sheet: the xlwings object of the dashboard sheet in the model
    :param forex_dict: forex dictionary contains the updated forex rates
    :param price_dict: price dictionary contains the updated stock prices
    """

    price_data = get_price(dash_sheet.range(thesis_pos["symbol"]).value, price_dict)
    dash_sheet.range(thesis_pos["price"]).value = price_data[0]  # Stock price
    price_currency = price_data[1]
    report_currency = dash_sheet.range(thesis_pos["report_currency"]).value
    dash_sheet.range(thesis_pos["price_currency"]).value = price_currency

    forex_str = report_currency + price_currency
    if forex_str in forex_dict:
        dash_sheet.range(thesis_pos["fx_rate"]).value = forex_dict[forex_str]
    elif report_currency == price_currency:
        dash_sheet.range(thesis_pos["fx_rate"]).value = 1
    else:  # Use the better yfinance Forex
        print("updating Forex rate...")
        dash_sheet.range(thesis_pos["fx_rate"]).value = yf.get_forex(report_currency, price_currency)
