import xlwings as xw
import re
from smart_value.data.forex_data import ForexData
from smart_value.data.yq_data import get_price_dict
from smart_value.tools.find_docs import stock_monitor_file_path, get_model_paths
from smart_value.data.model_data import thesis_pos
from smart_value.data.monitor_data import (market_yield_pos, portfolio_mgmt_pos, opportunities_headers,
                                           opportunities_start_row)
from smart_value.data.fred_data import get_riskfree_rate, get_us_prime_rate
import pandas as pd

"""
Task: Summarize valuation results from multiple Excel models into a monitor file using Python and xlwings.

Coding Approach:
1. Read Model Paths and Initialize Data: Retrieve paths to all Excel valuation models and initialize dictionaries for 
forex rates and stock prices if updates are required.
2. Update the and market yield data if not in quick mode.
3. Process Each Model: For each model, read the necessary data, update market price, and forex rate if not in quick 
mode, and extract relevant information using a helper class.
4. Update Monitor File: Write the extracted data into the monitor file using, ensuring correct column mappings and 
handling formula cells appropriately.

Note: Ensure correct data mapping between cell positions in Excel sheets and attribute names in the helper class to 
avoid discrepancies.
"""


def update_monitor(skip=True):
    """The main function to update the stock monitor."""
    model_paths = get_model_paths()

    if not skip:
        try:
            update_market_data(stock_monitor_file_path, model_paths)
        except Exception as e:
            print(f"Skipping market yield update due to error: {e}")

    opportunities = []
    for model_path in model_paths:
        print(f"Processing {model_path}...")
        opportunity = read_opportunity(model_path)
        if opportunity:
            opportunities.append(opportunity)

    print("Updating monitor file...")
    with xw.App(visible=False) as app:
        monitor_wb = app.books.open(stock_monitor_file_path)
        calculate_allocation_weights(monitor_wb, opportunities)  # First, set weights
        update_monitor_data(monitor_wb, opportunities)           # Then, write data
        monitor_wb.save()
        monitor_wb.close()
    print("Update completed successfully.")


def read_opportunity(model_path):
    """Read opportunity data from a model file

    Args:
        model_path (str): Path to the model file

    Returns:
        MonitorStock: Object containing extracted opportunity data, or None if not a stock model
    """
    opportunity = None
    is_stock_model = re.compile(r".*Valuation.*").match(str(model_path))

    if is_stock_model:
        with xw.App(visible=False) as app:
            workbook = app.books.open(model_path)
            thesis_sheet = workbook.sheets['Thesis']
            opportunity = MonitorStock(thesis_sheet)
            workbook.close()
    return opportunity


class MonitorStock:
    """Represents a stock opportunity with data extracted from a valuation model.

    Attributes are dynamically created based on thesis_pos mapping.
    Only includes attributes that exist in both thesis_pos and opportunities_headers.
    """

    def __init__(self, thesis_sheet):
        """Initialize attributes by reading from the Thesis sheet.

        Args:
            thesis_sheet (xlwings.Sheet): The 'Thesis' sheet from a valuation model.
        """
        # Get all attributes that exist in both thesis_pos and opportunities_headers
        valid_attrs = set(thesis_pos.keys()) & set(opportunities_headers.keys())

        for attr in valid_attrs:
            try:
                value = thesis_sheet.range(thesis_pos[attr]).value
                setattr(self, attr, value)
            except Exception as e:
                print(f"Warning: Could not set attribute {attr}: {str(e)}")
                setattr(self, attr, None)


def calculate_allocation_weights(monitor_wb, opportunities):
    """
    Calculate allocation weights for the portfolio based on the given opportunities and portfolio management rules.

    Steps:
    1. Retrieve parameters (benchmark return, cash yield, max holdings, etc.).
    2. Filter eligible opportunities (Selected Flag = 'Y', ERB > 0).
    3. Enforce max holdings and growth classification limits during selection.
    4. Calculate provisional weights (Single Investment Cap), delta adjustment, and allocation weights.
    5. Adjust allocations if total exceeds investable capital, respecting ERB ranking.
    6. Calculate projected cash reserve and portfolio return.
    """
    portfolio_mgmt_sheet = monitor_wb.sheets['Portfolio_Mgmt']

    # Retrieve parameters from Portfolio_Mgmt sheet
    benchmark_return = float(portfolio_mgmt_sheet.range(portfolio_mgmt_pos["benchmark_return"]).value)
    cash_yield = float(portfolio_mgmt_sheet.range(portfolio_mgmt_pos["cash_yield"]).value)
    max_holdings = int(portfolio_mgmt_sheet.range(portfolio_mgmt_pos["max_holdings"]).value)
    single_investment_cap = float(portfolio_mgmt_sheet.range(portfolio_mgmt_pos["single_investment_cap"]).value)
    negative_low_growth_cap = int(portfolio_mgmt_sheet.range(portfolio_mgmt_pos["negative_low_growth"]).value)
    high_growth_cap = int(portfolio_mgmt_sheet.range(portfolio_mgmt_pos["high_growth"]).value)
    target_return = float(portfolio_mgmt_sheet.range(portfolio_mgmt_pos["target_return"]).value)
    min_cash_reserve = float(portfolio_mgmt_sheet.range(portfolio_mgmt_pos["min_cash_reserve"]).value)

    # Filter eligible opportunities (Selected Flag = 'Y' and ERB > 0)
    eligible_opportunities = [
        opp for opp in opportunities
        if getattr(opp, 'is_selected', '') == 'Y' and (getattr(opp, 'market_annual_return', 0) - benchmark_return) > 0
    ]

    # Enforce max holdings and growth classification limits during selection
    sorted_eligible = sorted(
        eligible_opportunities,
        key=lambda opp: (getattr(opp, 'market_annual_return', 0) - benchmark_return),
        reverse=True
    )

    selected_opportunities = []
    hg_count = 0
    nlg_count = 0

    for opp in sorted_eligible:
        growth_class = getattr(opp, 'growth_class', '')
        if growth_class == 'High Growth':
            if hg_count >= high_growth_cap:
                continue
            hg_count += 1
        elif growth_class in ['Negative', 'Low Growth']:
            if nlg_count >= negative_low_growth_cap:
                continue
            nlg_count += 1
        # Check if max_holdings is reached
        if len(selected_opportunities) >= max_holdings:
            break
        selected_opportunities.append(opp)

    # Handle no eligible investments case
    if not selected_opportunities:
        projected_cash = 1.0
        projected_portfolio_return = cash_yield
    else:
        # Calculate provisional weights and delta adjustments
        for opp in selected_opportunities:
            r_i = getattr(opp, 'market_annual_return', 0)
            delta = max(0, (target_return - r_i) / target_return)
            provisional_weight = single_investment_cap
            opp.allocation_weight = provisional_weight * (1 - delta)

        allocated_weight = sum(getattr(opp, 'allocation_weight', 0) for opp in selected_opportunities)
        investable_capital = 1 - min_cash_reserve

        # Adjust allocation if exceeds investable capital
        if allocated_weight > investable_capital:
            # Sort by ERB descending
            sorted_by_erb = sorted(
                selected_opportunities,
                key=lambda opp: (getattr(opp, 'market_annual_return', 0) - benchmark_return),
                reverse=True
            )
            cumulative = 0.0
            index = 0
            for i, opp in enumerate(sorted_by_erb):
                current_weight = getattr(opp, 'allocation_weight', 0)
                if cumulative + current_weight <= investable_capital:
                    cumulative += current_weight
                else:
                    # Allocate remaining to this opp, set others to 0
                    remaining = investable_capital - cumulative
                    opp.allocation_weight = remaining
                    cumulative = investable_capital
                    index = i + 1
                    break
            # Set remaining to 0
            for opp in sorted_by_erb[index:]:
                opp.allocation_weight = 0.0
            allocated_weight = cumulative

        projected_cash = 1 - allocated_weight
        investment_return = sum(
            getattr(opp, 'allocation_weight', 0.0) * getattr(opp, 'market_annual_return', 0.0)
            for opp in selected_opportunities
        )
        projected_portfolio_return = investment_return + (projected_cash * cash_yield)

    # Set allocation_weight to 0 for non-selected opportunities
    for opp in opportunities:
        if opp not in selected_opportunities:
            opp.allocation_weight = 0.0

    # Write results to Portfolio_Mgmt sheet
    portfolio_mgmt_sheet.range(portfolio_mgmt_pos["projected_cash"]).value = projected_cash
    portfolio_mgmt_sheet.range(portfolio_mgmt_pos["projected_portfolio_return"]).value = projected_portfolio_return


def update_monitor_data(monitor_wb, opportunities):
    """
    Update the "Opportunities" sheet with the latest opportunity data.

    Steps:
    1. Sort opportunities by market_annual_return (descending).
    2. Clear existing data in the specified range.
    3. Write all opportunity data (e.g., symbol, price, allocation_weight) to the sheet.
    4. Set ERB and ERC formulas for each row.

    Args:
        monitor_wb (xlwings.Book): The monitor workbook.
        opportunities (list): List of MonitorStock objects with allocation_weight set.
    """
    sheet = monitor_wb.sheets['Opportunities']
    start_row = opportunities_start_row

    # Sort opportunities by market_annual_return descending
    opportunities.sort(key=lambda opp: getattr(opp, 'market_annual_return', float('-inf')), reverse=True)

    # Clear old data
    buffer = 100  # Extra rows to ensure all old data is cleared
    last_row = start_row + buffer - 1
    sheet.range(f"B{start_row}:X{last_row}").clear_contents()

    # Write new data
    column_order = sorted(opportunities_headers.keys(), key=lambda x: opportunities_headers[x])
    data = [{attr: getattr(opp, attr, None) for attr in column_order} for opp in opportunities]
    df = pd.DataFrame(data, columns=column_order)
    sheet.range(f"B{int(start_row)}").options(pd.DataFrame, header=False, index=False).value = df

    # Set ERB and ERC formulas
    if opportunities:
        try:
            last_data_row = start_row + len(opportunities) - 1
            benchmark_ref = ("Portfolio_Mgmt!" +
                             (monitor_wb.sheets['Portfolio_Mgmt'].range(portfolio_mgmt_pos["benchmark_return"]).
                              get_address(row_absolute=True, column_absolute=True)))
            cash_yield_ref = ("Portfolio_Mgmt!" +
                              monitor_wb.sheets['Portfolio_Mgmt'].range(portfolio_mgmt_pos["cash_yield"]).
                              get_address(row_absolute=True, column_absolute=True))
            erb_formula = f"=F{int(start_row)} - {benchmark_ref}"
            erc_formula = f"=F{int(start_row)} - {cash_yield_ref}"
            sheet.range(f"G{int(start_row)}:G{int(last_data_row)}").formula = erb_formula
            sheet.range(f"H{int(start_row)}:H{int(last_data_row)}").formula = erc_formula
        except Exception as e:
            print(f"Error setting formulas: {e}")
            # Fallback: Set formulas row-by-row
            for row in range(int(start_row), int(last_data_row) + 1):
                sheet.range(f"G{row}").formula = f"=F{row} - {benchmark_ref}"
                sheet.range(f"H{row}").formula = f"=F{row} - {cash_yield_ref}"

    print(f"Successfully updated {len(opportunities)} opportunities.")


def update_market_data(monitor_path, model_paths):
    """Update market data in stock monitor, and update market price, forex rate, and market yield assumptions in the
    models.

    Args:
        monitor_path (str): Path to the stock monitor file
        model_paths (list): List of paths to valuation model files
    """

    print("Updating market yields...")
    # Initialize model assumption variables to None in case retrieval fails
    equity_cost = None
    target_return = None
    entry_yield = None
    holding_period = None
    benchmark_return = None

    # Update market yields and retrieve assumptions
    try:
        us_riskfree = get_riskfree_rate("us")
        us_prime = get_us_prime_rate()

        with xw.App(visible=False) as app:
            monitor_wb = app.books.open(monitor_path)
            # Update market yields
            market_yield_sheet = monitor_wb.sheets['Market_Yield']
            market_yield_sheet.range(market_yield_pos["us_riskfree"]).value = us_riskfree
            market_yield_sheet.range(market_yield_pos["us_prime"]).value = us_prime
            # Retrieve model assumptions
            portfolio_mgmt_sheet = monitor_wb.sheets['Portfolio_Mgmt']
            equity_cost = portfolio_mgmt_sheet.range(portfolio_mgmt_pos["equity_cost"]).value
            target_return = portfolio_mgmt_sheet.range(portfolio_mgmt_pos["target_return"]).value
            entry_yield = portfolio_mgmt_sheet.range(portfolio_mgmt_pos["entry_yield"]).value
            holding_period = portfolio_mgmt_sheet.range(portfolio_mgmt_pos["holding_period"]).value
            benchmark_return = portfolio_mgmt_sheet.range(portfolio_mgmt_pos["benchmark_return"]).value
            monitor_wb.save()
            monitor_wb.close()
        print("Market yields updated successfully.")
    except Exception as e:
        print(f"Error updating Market yields or retrieving assumptions: {e}")

    # Retrieve forex data, set to None if it fails
    forex_data = None
    try:
        forex_data = ForexData()
    except Exception as e:
        print(f"Error retrieving Forex data: {e}")

    # Retrieve price dictionary, set to None if it fails
    price_dict = None
    try:
        price_dict = get_price_dict(model_paths)
    except Exception as e:
        print(f"Error retrieving price dictionary: {e}")

    # Update each model's market data and assumptions
    for path in model_paths:
        try:
            with xw.App(visible=False) as app:
                model_wb = app.books.open(path)
                thesis_sheet = model_wb.sheets['Thesis']

                # Update market price only if price_dict is available
                symbol = thesis_sheet.range(thesis_pos['symbol']).value
                if price_dict is not None and symbol in price_dict:
                    thesis_sheet.range(thesis_pos['price']).value = price_dict[symbol]

                # Update forex rate only if forex_data is available
                price_currency = thesis_sheet.range(thesis_pos['price_currency']).value
                report_currency = thesis_sheet.range(thesis_pos['report_currency']).value
                if forex_data is not None:
                    try:
                        fx_rate = forex_data.get_rate(report_currency, price_currency)
                        thesis_sheet.range(thesis_pos['fx_rate']).value = fx_rate
                    except Exception as e:
                        print(f"Error getting forex rate for {report_currency}/{price_currency} in {path}: {e}")

                # Update market yield assumptions only if they were retrieved
                if target_return is not None:
                    thesis_sheet.range(thesis_pos["target_return"]).value = target_return
                if holding_period is not None:
                    thesis_sheet.range(thesis_pos["holding_period"]).value = holding_period
                if entry_yield is not None:
                    thesis_sheet.range(thesis_pos["entry_yield"]).value = entry_yield
                if equity_cost is not None:
                    thesis_sheet.range(thesis_pos["base_equity_cost"]).value = equity_cost
                if benchmark_return is not None:
                    thesis_sheet.range(thesis_pos["benchmark_return"]).value = benchmark_return

                model_wb.save()
                model_wb.close()
                print(f"Updated {path}")
        except Exception as e:
            print(f"Error updating {path}: {e}")
