import xlwings as xw
from smart_value.data.fred_data import get_riskfree_rate, get_us_prime_rate
from smart_value.tools.find_docs import macro_monitor_file_path
from smart_value.data.model_data import thesis_pos

market_yield_pos = {
    "target_return": "C3",
    "holding_period": "D3",
    "equity_cost": "C4",
    "us_riskfree": "C8",
    "us_prime": "D8",
    "cn_riskfree": "C9",
    "cn_prime": "D9",
    "hk_riskfree": "C10",
    "hk_prime": "D10"
}


def update_macro(macro_path):
    """Update macro data in Macro_Monitor.xlsx."""
    print("Updating Macro data...")
    try:
        us_riskfree = get_riskfree_rate("us")
        us_prime = get_us_prime_rate()

        with xw.App(visible=False) as app:
            macro_book = app.books.open(macro_path)
            yield_sheet = macro_book.sheets['Market_Yield']
            yield_sheet.range(market_yield_pos["us_riskfree"]).value = us_riskfree
            yield_sheet.range(market_yield_pos["us_prime"]).value = us_prime
            macro_book.save()
            macro_book.close()
        print("Macro data updated successfully.")
    except Exception as e:
        print(f"Error updating macro data: {e}")


class MonitorMarco:
    """Extracts macro parameters from Market_Yield sheet."""

    def __init__(self, macro_sheet):
        self.equity_cost = macro_sheet.range(market_yield_pos["equity_cost"]).value
        self.target_return = macro_sheet.range(market_yield_pos["target_return"]).value
        self.holding_period = macro_sheet.range(market_yield_pos["holding_period"]).value
