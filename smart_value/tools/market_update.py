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

