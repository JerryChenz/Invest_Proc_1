import xlwings as xw
import re
from smart_value.data.forex_data import get_forex_dict
from smart_value.tools import model_dash
from smart_value.tools.find_docs import stock_monitor_file_path, get_model_paths
from smart_value.data.model_data import thesis_pos
from smart_value.tools.model_update import get_price_dict


def update_monitor(quick=True):
    """Update the stock monitor file with the latest valuation data from models.

    Args:
        quick (bool): If True, skip updating prices and forex rates. Defaults to True.
    """
    model_paths = get_model_paths()
    forex_dict = get_forex_dict() if not quick else {}
    price_dict = get_price_dict(model_paths) if not quick else {}

    # Read and process each valuation model
    opportunities = []
    for path in model_paths:
        print(f"Processing {path}...")
        opportunity = read_opportunity(path, quick, forex_dict, price_dict)
        if opportunity:
            opportunities.append(opportunity)

    # Update the monitor file with the collected opportunities
    print("Updating monitor file...")
    with xw.App(visible=False) as app:
        monitor_workbook = app.books.open(stock_monitor_file_path)
        update_opportunities(monitor_workbook, opportunities)
        monitor_workbook.save(stock_monitor_file_path)
        monitor_workbook.close()
    print("Update completed successfully.")


def read_opportunity(model_path, quick, forex_dict, price_dict):
    """Read and process an individual valuation model to extract monitoring data.

    Args:
        model_path (str): Path to the valuation model Excel file.
        quick (bool): If True, skip updating the model's thesis_sheet.
        forex_dict (dict): Updated forex rates for currency conversion.
        price_dict (dict): Updated stock prices.

    Returns:
        MonitorStock: An object containing extracted data, or None if invalid.
    """
    opportunity = None
    is_stock_model = re.compile(r".*Valuation.*").match(str(model_path))

    if is_stock_model:
        with xw.App(visible=False) as app:
            workbook = app.books.open(model_path)
            thesis_sheet = workbook.sheets('Thesis')

            if not quick:
                # Update the model's thesis_sheet with latest data
                model_dash.update_dash_marco(thesis_sheet)
                model_dash.update_dash_market(thesis_sheet, forex_dict, price_dict)
                workbook.save()

            opportunity = MonitorStock(thesis_sheet)
            workbook.close()
    else:
        print(f"Skipping non-valuation model: {model_path}")

    return opportunity


def update_opportunities(monitor_workbook, opportunities):
    """Write the extracted opportunities data into the monitor workbook.

    Args:
        monitor_workbook (xlwings.Book): The target monitor workbook.
        opportunities (list): List of MonitorStock objects to write.
    """
    sheet = monitor_workbook.sheets['Opportunities']
    start_row = 3
    sheet.range(f"B{start_row}:W{start_row + len(opportunities) + 30}").clear_contents()

    # Column mappings: (column_index, attribute_name)
    COLUMNS = [
        (2, 'symbol'), (3, 'name'), (4, 'price'), (5, 'price_currency'),
        (6, 'market_annual_yield'), (7, 'target_price'), (8, 'expected_equity_value'), (9, 'Margin_of_safety'),
        (10, 'fcfe_yield'), (11, 'dividend_yield'), (12, 'comp_group'),
        (13, 'investment_type'), (14, 'update_required_after'), (16, 'is_hold')
    ]

    for row_idx, opportunity in enumerate(opportunities, start=start_row):
        # Write standard attributes
        for col, attr in COLUMNS:
            sheet.range((row_idx, col)).value = getattr(opportunity, attr)
        # Set the price alert formula in column V (22)
        sheet.range((row_idx, 22)).formula = f'=IFERROR(D{row_idx}/H{row_idx}-1, "nm")'

    print(f"Successfully updated {len(opportunities)} opportunities.")


class MonitorStock:
    """Represents a stock opportunity with data extracted from a valuation model."""
    # Attribute mapping: (attribute_name, model_pos_key)
    _ATTR_MAP = [
        ('symbol', 'symbol'), ('name', 'name'), ('price', 'price'),
        ('price_currency', 'price_currency'), ('market_annual_yield', 'market_yield'),
        ('target_price', 'target_price'), ('expected_equity_value', 'equity_value'), ('Margin_of_safety', 'mos'),
        ('fcfe_yield', 'fcfe_yield'), ('dividend_yield', 'dividend_yield'),
        ('comp_group', 'comp_group'), ('investment_type', 'investment_type'),
        ('update_required_after', 'update_after'), ('is_hold', 'is_hold')
    ]

    def __init__(self, thesis_sheet):
        """Initialize attributes by reading from the dashboard sheet."""
        for attr, pos_key in self._ATTR_MAP:
            setattr(self, attr, thesis_sheet.range(thesis_pos[pos_key]).value)
