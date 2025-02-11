import xlwings
import re
from smart_value.data.forex_data import get_forex_dict
from smart_value.tools import *
from smart_value.tools.find_docs import stock_monitor_file_path, get_model_paths
from smart_value.tools.model_dash import model_pos
from smart_value.tools.model_update import get_price_dict


def update_monitor(quick=True):
    """Update the Monitor file

    :param quick: the option to update the monitor sheet without updating the price and forex
    """

    opportunities_path_list = get_model_paths()
    forex_dict = {}
    price_dict = {}
    if quick is False:
        forex_dict = get_forex_dict()
        price_dict = get_price_dict(opportunities_path_list)

    # Step 1: load and update the new valuation xlsx
    opportunities = []
    for opportunities_path in opportunities_path_list:
        print(f"Reading {opportunities_path}...")
        op = read_opportunity(opportunities_path, quick, forex_dict, price_dict)  # load and update
        opportunities.append(op)

    # Step 2: Update the stock monitor.
    print("Updating Monitor...")
    with xlwings.App(visible=False) as app:
        s_monitor = app.books.open(stock_monitor_file_path)
        update_opportunities(s_monitor, opportunities)
        s_monitor.save(stock_monitor_file_path)
        s_monitor.close()
    print("Update completed")


def read_opportunity(opportunities_path, quick, forex_dict, price_dict):
    """Read all the opportunities at the opportunities_path.

    :param opportunities_path: path of the model in the opportunities' folder
    :param quick: the option to skip updating the models
    :param forex_dict: forex dictionary contains the updated forex rates
    :param price_dict: price dictionary contains the updated stock prices
    :return: an Asset object
    """

    r_stock = re.compile(".*Valuation.*")
    # get the formula results using xlwings because openpyxl doesn't evaluate formula
    with xlwings.App(visible=False) as app:
        xl_book = app.books.open(opportunities_path)
        dash_sheet = xl_book.sheets('Dashboard')
        if r_stock.match(str(opportunities_path)):
            if quick is False:
                model_dash.update_dash_marco(dash_sheet)
                model_dash.update_dash_market(dash_sheet, forex_dict, price_dict)
                xl_book.save(opportunities_path)  # xls must be saved to update the values
            op = MonitorStock(dash_sheet)  # the MonitorStock object representing an opportunity
        else:
            print(f"'{opportunities_path}' is incorrect")
        xl_book.close()

    return op


def update_opportunities(s_monitor, op_list):
    """Update the opportunities sheet in the stock_monitor file

    :param op_list: list of stock objects
    :param s_monitor: xlwings stock monitor file object
    """

    monitor_sheet = s_monitor.sheets('Opportunities')
    r = 5  # the starting row
    final_row = len(op_list) + r + 30  # the estimated final row
    monitor_sheet.range(f'B5:W{final_row}').clear_contents()

    for op in op_list:
        monitor_sheet.range((r, 2)).value = op.symbol
        monitor_sheet.range((r, 3)).value = op.name
        # Price section
        monitor_sheet.range((r, 4)).value = op.price
        monitor_sheet.range((r, 5)).value = op.price_currency
        monitor_sheet.range((r, 6)).value = op.ep_ratio
        monitor_sheet.range((r, 7)).value = op.dp_ratio
        # Valuation section
        monitor_sheet.range((r, 8)).value = op.value
        monitor_sheet.range((r, 9)).value = op.lower_value
        monitor_sheet.range((r, 10)).value = op.upper_value
        # Miscellaneous section
        monitor_sheet.range((r, 11)).value = op.watchlist
        monitor_sheet.range((r, 12)).value = op.comp_group
        monitor_sheet.range((r, 13)).value = op.last_revision
        monitor_sheet.range((r, 14)).value = op.next_review
        # Cost Structure section
        monitor_sheet.range((r, 15)).value = op.roe
        monitor_sheet.range((r, 16)).value = op.ebit_margin
        monitor_sheet.range((r, 17)).value = op.asset_turnover
        monitor_sheet.range((r, 18)).value = op.leverage_ratio
        monitor_sheet.range((r, 19)).value = op.interest
        monitor_sheet.range((r, 20)).value = op.change_of_wc
        monitor_sheet.range((r, 21)).value = op.mcx
        # Price Alert
        monitor_sheet.range((r, 22)).value = f'=IFERROR((D{r}-I{r})/(H{r}-I{r}),"nm")'
        monitor_sheet.range((r, 23)).value = op.is_hold
        r += 1
    print(f"Total {len(op_list)} opportunities Updated")


class MonitorStock:
    """Monitor class

    Defines what data can be extracted from the valuation model and used in the Monitor.
    """

    def __init__(self, dash_sheet):
        self.symbol = dash_sheet.range(model_pos["symbol"]).value
        self.name = dash_sheet.range(model_pos["name"]).value
        # Price section
        self.price = dash_sheet.range(model_pos["price"]).value
        self.price_currency = dash_sheet.range(model_pos["price_currency"]).value
        self.ep_ratio = dash_sheet.range(model_pos["ep_ratio"]).value
        self.dp_ratio = dash_sheet.range(model_pos["dp_ratio"]).value
        # Valuation section
        self.value = dash_sheet.range(model_pos["value"]).value
        self.lower_value = dash_sheet.range(model_pos["lower_value"]).value
        self.upper_value = dash_sheet.range(model_pos["upper_value"]).value
        # Miscellaneous section
        self.watchlist = dash_sheet.range(model_pos["watchlist"]).value
        self.comp_group = dash_sheet.range(model_pos["comp_group"]).value
        self.last_revision = dash_sheet.range(model_pos["last_revision"]).value
        self.next_review = dash_sheet.range(model_pos["next_review"]).value
        # Cost Structure section
        self.roe = dash_sheet.range(model_pos["ROE"]).value
        self.leverage_ratio = dash_sheet.range(model_pos["Leverage_ratio"]).value
        self.asset_turnover = dash_sheet.range(model_pos["Asset_Turnover"]).value
        self.ebit_margin = dash_sheet.range(model_pos["EBIT_Margin"]).value
        self.interest = dash_sheet.range(model_pos["interest"]).value
        self.change_of_wc = dash_sheet.range(model_pos["change_of_wc"]).value
        self.mcx = dash_sheet.range(model_pos["mcx"]).value
        self.is_hold = dash_sheet.range(model_pos["is_hold"]).value
