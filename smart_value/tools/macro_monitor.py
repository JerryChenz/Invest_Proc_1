import xlwings
from smart_value.data.fred_data import get_riskfree_rate, get_us_bbb_yield
from smart_value.data.hkma_data import get_hk_riskfree
from smart_value.tools.find_docs import macro_monitor_file_path as macro_monitor_file_path
from openpyxl import load_workbook

# Define the positions of the Marco data
macro_pos = {
    "us_riskfree": "C3",
    "us_bbb_yield": "C4",
    "us_required_return": "C6",
    "cn_riskfree": "D3",
    "cn_on_bbb_yield": "D4",
    "cn_off_bbb_yield": "D5",
    "cn_required_return": "D6",
    "hk_riskfree": "E3",
    "hk_required_return": "E6",
    "other_required_return": "F6",
    "target_return": "C8",
    "investment_horizon": "D8"
}


def update_marco(monitor_path, source="Free"):
    """Update the marco data in the Macro_Monitor.xlsx file.

    :param monitor_path: path of the Macro_Monitor.xlsx file
    :param source: the API option
    """

    print("Updating Marco data...")
    us_riskfree = None
    hk_riskfree = None
    us_bbb_yield = None

    if source == "Free":
        us_riskfree = get_riskfree_rate("us")
        # print(us_riskfree)
        us_bbb_yield = get_us_bbb_yield()
        hk_riskfree = get_hk_riskfree()
        # print(hk_riskfree)

    with xlwings.App(visible=False) as app:
        marco_book = app.books.open(monitor_path)
        macro_sheet = marco_book.sheets('Macro')
        macro_sheet.range(macro_pos["us_riskfree"]).value = us_riskfree
        macro_sheet.range(macro_pos["us_bbb_yield"]).value = us_bbb_yield
        macro_sheet.range(macro_pos["hk_riskfree"]).value = hk_riskfree
        marco_book.save(monitor_path)
        marco_book.close()
    print("Finished Marco data Update")


def read_marco():

    # Marco data
    monitor_wb = load_workbook(macro_monitor_file_path, read_only=True, data_only=True)
    macro_sheet = monitor_wb["Macro"]
    macro = MonitorMarco(macro_sheet)
    monitor_wb.close()
    return macro


class MonitorMarco:
    """Monitor class for Macro

    Defines what data can be extracted from the valuation model and used in the Monitor.
    """

    def __init__(self, macro_sheet):
        self.us_riskfree = macro_sheet[macro_pos["us_riskfree"]].value
        self.us_bbb_yield = macro_sheet[macro_pos["us_bbb_yield"]].value
        self.us_required_return = macro_sheet[macro_pos["us_required_return"]].value
        self.cn_riskfree = macro_sheet[macro_pos["cn_riskfree"]].value
        self.cn_on_bbb_yield = macro_sheet[macro_pos["cn_on_bbb_yield"]].value
        self.cn_off_bbb_yield = macro_sheet[macro_pos["cn_off_bbb_yield"]].value
        self.cn_required_return = macro_sheet[macro_pos["cn_required_return"]].value
        self.hk_required_return = macro_sheet[macro_pos["hk_required_return"]].value
        self.other_required_return = macro_sheet[macro_pos["other_required_return"]].value
        self.target_return = macro_sheet[macro_pos["target_return"]].value
        self.investment_horizon = macro_sheet[macro_pos["investment_horizon"]].value
