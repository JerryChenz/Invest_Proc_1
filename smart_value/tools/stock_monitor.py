import xlwings as xw
import re
from smart_value.data.forex_data import get_forex_dict
from smart_value.tools import market_update
from smart_value.tools.find_docs import stock_monitor_file_path, get_model_paths
from smart_value.data.model_data import thesis_pos
from smart_value.tools.market_update import get_price_dict

"""
Task: Summarize valuation results from multiple Excel models into a monitor file using Python and xlwings.

Coding Approach:
1. Read Model Paths and Initialize Data: Retrieve paths to all Excel valuation models and initialize dictionaries 
for forex rates and stock prices if updates are required.
2. Process Each Model: For each model, read the necessary data, update market data if not in quick mode, and extract 
relevant information using a helper class.
3. Data Mapping: Ensure correct mapping between cell positions in Excel sheets and attribute names in the helper class 
to avoid discrepancies.
4. Update Monitor File: Write the extracted data into the monitor file, ensuring correct column mappings and 
handling formula cells appropriately.
"""


def update_monitor(skip=True):
    """Update the stock monitor file with the latest valuation data from models.

    Args:
        skip (bool): If True, skip updating prices and forex rates. Defaults to True.
    """
    model_paths = get_model_paths()
    forex_dict = get_forex_dict() if not skip else {}
    price_dict = get_price_dict(model_paths) if not skip else {}

    # Read and process each valuation model
    opportunities = []
    for path in model_paths:
        print(f"Processing {path}...")
        opportunity = read_opportunity(path, skip, forex_dict, price_dict)
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
                market_update.update_dash_marco(thesis_sheet)
                market_update.update_market_data(thesis_sheet, forex_dict, price_dict)
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
        (6, 'market_annual_return'), (7, 'target_price'), (8, 'expected_equity_value'),
        (10, 'fcfe_yield'), (11, 'dividend_yield'), (12, 'comp_group'),
        (13, 'investment_type'), (14, 'update_after'), (16, 'is_hold')
    ]

    for row_idx, opportunity in enumerate(opportunities, start=start_row):
        # Write standard attributes
        for col, attr in COLUMNS:
            sheet.range((row_idx, col)).value = getattr(opportunity, attr)
        # Set the margin of safety formula in column I (9)
        sheet.range((row_idx, 9)).formula = f'=IFERROR(G{row_idx}/H{row_idx}-1, "nm")'
        # Set the price alert formula in column O (15)
        sheet.range((row_idx, 15)).formula = f'=IFERROR(D{row_idx}/H{row_idx}-1, "nm")'

    print(f"Successfully updated {len(opportunities)} opportunities.")


class MonitorStock:
    """Represents a stock opportunity with data extracted from a valuation model."""
    # Attribute mapping: (attribute_name, model_pos_key)
    _ATTR_MAP = [
        ('symbol', 'symbol'), ('name', 'name'), ('price', 'price'),
        ('price_currency', 'price_currency'), ('market_annual_return', 'market_annual_return'),
        ('target_price', 'target_price'), ('expected_equity_value', 'expected_equity_value'),
        ('fcfe_yield', 'fcfe_yield'), ('dividend_yield', 'dividend_yield'),
        ('comp_group', 'comp_group'), ('investment_type', 'investment_type'),
        ('update_after', 'update_after'), ('is_hold', 'is_hold')
    ]

    def __init__(self, thesis_sheet):
        """Initialize attributes by reading from the Thesis sheet."""
        for attr, pos_key in self._ATTR_MAP:
            setattr(self, attr, thesis_sheet.range(thesis_pos[pos_key]).value)
