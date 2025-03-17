from forex_python.converter import CurrencyRates
import smart_value.tools.macro_monitor as macro_monitor
from smart_value.data.yq_data import get_price
from smart_value.data.model_data import thesis_pos
from openpyxl.reader.excel import load_workbook
from smart_value.data.yq_data import get_quotes
import re

"""Note: Requires internet access"""


def update_dash_marco(thesis_sheet):
    """
    Update the macro parameters of the Dashboard sheet.

    :param thesis_sheet: The xlwings object of the Thesis sheet in the model
    """
    marco = macro_monitor.read_marco()
    thesis_sheet.range(thesis_pos["base_equity_cost"]).value = marco.us_riskfree
    thesis_sheet.range(thesis_pos["target_return"]).value = marco.target_return
    thesis_sheet.range(thesis_pos["holding_period"]).value = marco.holding_period


def update_market_data(thesis_sheet, forex_dict, price_dict):
    """
    Update the price and forex parameters of the Thesis sheet.

    :param thesis_sheet: The xlwings object of the Thesis sheet in the model
    :param forex_dict: Forex dictionary containing the updated forex rates
    :param price_dict: Price dictionary containing the updated stock prices
    """
    symbol = thesis_sheet.range(thesis_pos["symbol"]).value
    price, price_currency = get_price(symbol, price_dict)
    thesis_sheet.range(thesis_pos["price"]).value = price
    thesis_sheet.range(thesis_pos["price_currency"]).value = price_currency

    report_currency = thesis_sheet.range(thesis_pos["report_currency"]).value
    forex_str = report_currency + price_currency

    if forex_str in forex_dict:
        thesis_sheet.range(thesis_pos["fx_rate"]).value = forex_dict[forex_str]
    elif report_currency == price_currency:
        thesis_sheet.range(thesis_pos["fx_rate"]).value = 1
    else:
        print("Updating Forex rate...")
        # Use forex-python to get the forex rate
        c = CurrencyRates()
        try:
            rate = c.get_rate(report_currency, price_currency)
            thesis_sheet.range(thesis_pos["fx_rate"]).value = rate
        except Exception as e:
            print(f"Failed to fetch Forex rate: {e}")


def get_price_dict(model_paths):
    """Fetch current prices for all symbols found in model files."""
    ticker_list = []
    for model_path in model_paths:
        try:
            # Open each model file to extract the symbol
            opp_wb = load_workbook(model_path, read_only=True, data_only=True)
            thesis_sheet = opp_wb["Thesis"]
            symbol = thesis_sheet[thesis_pos["symbol"]].value
            ticker_list.append(symbol)
            opp_wb.close()
        except Exception as e:
            print(f"Error reading symbol from {model_path.name}: {str(e)}")
            continue  # Skip this model but continue processing others

    try:
        return get_quotes(ticker_list)
    except Exception as e:
        print(f"Failed to fetch market prices: {str(e)}. Proceeding without market data.")
        return {}
