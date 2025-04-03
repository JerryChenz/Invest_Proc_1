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
    Calculate allocation weights for the portfolio based on the given opportunities and portfolio management parameters.

    Steps:
    1. Retrieve portfolio parameters from the "Portfolio_Mgmt" sheet (e.g., benchmark return, caps).
    2. Filter opportunities with 'Selected' flag and ERB > 0.
    3. Select top opportunities up to the maximum holdings limit, ranked by ERB.
    4. Calculate attractiveness scores (A_i = ERB_i / Benchmark Return).
    5. Compute projected portfolio return with initial cash allocation.
    6. Adjust cash allocation if projected return is below target.
    7. Distribute weights, enforcing single investment and growth classification caps.
    8. Set allocation_weight on each opportunity (0 for unselected).
    9. Calculate adjusted portfolio return with cash yield.
    10. Write adjusted cash allocation and portfolio return to "Portfolio_Mgmt" sheet.

    Args:
        monitor_wb (xlwings.Book): The monitor workbook.
        opportunities (list): List of MonitorStock objects representing investment opportunities.
    """
    portfolio_mgmt_sheet = monitor_wb.sheets['Portfolio_Mgmt']

    # Retrieve parameters from Portfolio_Mgmt sheet
    benchmark_return = float(portfolio_mgmt_sheet.range(portfolio_mgmt_pos["benchmark_return"]).value)
    cash_yield = float(portfolio_mgmt_sheet.range(portfolio_mgmt_pos["cash_yield"]).value)
    max_holdings = int(portfolio_mgmt_sheet.range(portfolio_mgmt_pos["max_holdings"]).value)
    single_investment_cap = float(portfolio_mgmt_sheet.range(portfolio_mgmt_pos["single_investment_cap"]).value)
    negative_low_growth_cap = float(portfolio_mgmt_sheet.range(portfolio_mgmt_pos["negative_low_growth"]).value)
    high_growth_cap = float(portfolio_mgmt_sheet.range(portfolio_mgmt_pos["high_growth"]).value)
    target_return = float(portfolio_mgmt_sheet.range(portfolio_mgmt_pos["target_return"]).value)
    min_cash_reserve = float(portfolio_mgmt_sheet.range(portfolio_mgmt_pos["min_cash_reserve"]).value)
    sensitivity_factor = float(portfolio_mgmt_sheet.range(portfolio_mgmt_pos["sensitivity_factor"]).value)
    max_cash_allocation = float(portfolio_mgmt_sheet.range(portfolio_mgmt_pos["max_cash_allocation"]).value)

    # Filter eligible opportunities (Selected and ERB > 0)
    eligible_opportunities = [
        opp for opp in opportunities
        if getattr(opp, 'is_selected', False) and (getattr(opp, 'market_annual_return', 0) - benchmark_return) > 0
    ]

    # Sort by ERB descending and select top max_holdings
    sorted_eligible = sorted(
        eligible_opportunities,
        key=lambda opp: (getattr(opp, 'market_annual_return', 0) - benchmark_return),
        reverse=True
    )
    selected_opportunities = sorted_eligible[:max_holdings]

    # Calculate Attractiveness Scores (A_i)
    A_values = {}
    sum_A = 0.0
    if selected_opportunities:
        A_values = {
            opp: (getattr(opp, 'market_annual_return', 0) - benchmark_return) / benchmark_return
            for opp in selected_opportunities
        }
        sum_A = sum(A_values.values())

    # Compute projected return with initial cash
    projected_return = 0.0
    if sum_A > 0:
        projected_return = sum(
            (A / sum_A) * getattr(opp, 'market_annual_return', 0)
            for opp, A in A_values.items()
        ) * (1 - min_cash_reserve)

    # Dynamic cash adjustment if below target
    delta_cash = 0.0
    if projected_return < target_return:
        shortfall = target_return - projected_return
        delta_cash = sensitivity_factor * (shortfall / target_return)
        delta_cash = min(delta_cash, max_cash_allocation - min_cash_reserve)
    adjusted_cash = min_cash_reserve + delta_cash

    # Compute initial weights with adjusted cash
    initial_weights = {}
    if selected_opportunities and sum_A > 0:
        initial_weights = {
            opp: (A_values[opp] / sum_A) * (1 - adjusted_cash)
            for opp in selected_opportunities
        }

    # Apply single investment cap
    P_values = {}
    total_allocated = 0.0
    for opp in selected_opportunities:
        weight = initial_weights.get(opp, 0.0)
        if weight > single_investment_cap:
            P_values[opp] = single_investment_cap
            total_allocated += single_investment_cap
        else:
            P_values[opp] = weight
            total_allocated += weight

    # Redistribute excess from single cap to cash
    excess_single = (1 - adjusted_cash) - total_allocated
    adjusted_cash += excess_single

    # Apply growth classification caps
    # High Growth
    high_growth_opps = [opp for opp in selected_opportunities if getattr(opp, 'growth_class', '') == 'High Growth']
    sum_high = sum(P_values.get(opp, 0.0) for opp in high_growth_opps)
    if sum_high > high_growth_cap:
        excess_high = sum_high - high_growth_cap
        scale = high_growth_cap / sum_high
        for opp in high_growth_opps:
            P_values[opp] *= scale
        adjusted_cash += excess_high

    # Negative/Low Growth
    low_growth_opps = [opp for opp in selected_opportunities if getattr(opp, 'growth_class', '') in ['Negative',
                                                                                                     'Low Growth']]
    sum_low = sum(P_values.get(opp, 0.0) for opp in low_growth_opps)
    if sum_low > negative_low_growth_cap:
        excess_low = sum_low - negative_low_growth_cap
        scale = negative_low_growth_cap / sum_low
        for opp in low_growth_opps:
            P_values[opp] *= scale
        adjusted_cash += excess_low

    # Ensure adjusted cash doesn’t exceed max
    adjusted_cash = min(adjusted_cash, max_cash_allocation)

    # Assign allocation weights to all opportunities
    for opp in opportunities:
        opp.allocation_weight = P_values.get(opp, 0.0)

    # Calculate adjusted portfolio return (including cash yield)
    investment_return = sum(
        getattr(opp, 'allocation_weight', 0.0) * getattr(opp, 'market_annual_return', 0.0)
        for opp in opportunities
    )
    adjusted_portfolio_return = investment_return + (adjusted_cash * cash_yield)

    # Write results to Portfolio_Mgmt sheet
    portfolio_mgmt_sheet.range(portfolio_mgmt_pos["projected_cash"]).value = adjusted_cash
    portfolio_mgmt_sheet.range(portfolio_mgmt_pos["projected_portfolio_return"]).value = adjusted_portfolio_return


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
    sheet.range(f"B{start_row}:Q{last_row}").clear_contents()

    # Write new data
    column_order = sorted(opportunities_headers.keys(), key=lambda x: opportunities_headers[x])
    data = [{attr: getattr(opp, attr, None) for attr in column_order} for opp in opportunities]
    df = pd.DataFrame(data, columns=column_order)
    sheet.range(f"B{int(start_row)}").options(pd.DataFrame, header=False, index=False).value = df

    # Set ERB and ERC formulas
    if opportunities:
        try:
            last_data_row = start_row + len(opportunities) - 1
            benchmark_ref = (monitor_wb.sheets['Portfolio_Mgmt'].range(portfolio_mgmt_pos["benchmark_return"]).
                             get_address(row_absolute=True, column_absolute=True))
            cash_yield_ref = monitor_wb.sheets['Portfolio_Mgmt'].range(portfolio_mgmt_pos["cash_yield"]).get_address(
                row_absolute=True, column_absolute=True)
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
    try:
        us_riskfree = get_riskfree_rate("us")
        us_prime = get_us_prime_rate()

        with xw.App(visible=False) as app:
            monitor_wb = app.books.open(monitor_path)
            # Update the market yields
            market_yield_sheet = monitor_wb.sheets['Market_Yield']
            market_yield_sheet.range(market_yield_pos["us_riskfree"]).value = us_riskfree
            market_yield_sheet.range(market_yield_pos["us_prime"]).value = us_prime
            # Retrieve the model assumptions
            portfolio_mgmt_sheet = monitor_wb.sheets['Portfolio_Mgmt']
            equity_cost = portfolio_mgmt_sheet.range(portfolio_mgmt_pos["equity_cost"]).value
            target_return = portfolio_mgmt_sheet.range(portfolio_mgmt_pos["target_return"]).value
            holding_period = portfolio_mgmt_sheet.range(portfolio_mgmt_pos["holding_period"]).value
            monitor_wb.save()
            monitor_wb.close()
        print("Market yields updated successfully.")
    except Exception as e:
        print(f"Error updating Market yields: {e}")

    # Retrieve the Forex rates and the market prices
    forex_data = ForexData()
    price_dict = get_price_dict(model_paths)

    # Update each model's market data and model assumptions
    for path in model_paths:
        try:
            with xw.App(visible=False) as app:  # New App context for each model
                model_wb = app.books.open(path)
                thesis_sheet = model_wb.sheets['Thesis']

                # Update market data
                symbol = thesis_sheet.range(thesis_pos['symbol']).value
                if symbol in price_dict:
                    thesis_sheet.range(thesis_pos['price']).value = price_dict[symbol]

                # Update forex rate
                price_currency = thesis_sheet.range(thesis_pos['price_currency']).value
                report_currency = thesis_sheet.range(thesis_pos['report_currency']).value
                if forex_data:
                    fx_rate = forex_data.get_rate(report_currency, price_currency)
                    thesis_sheet.range(thesis_pos['fx_rate']).value = fx_rate

                # Update market yield assumptions
                thesis_sheet.range(thesis_pos["target_return"]).value = target_return
                thesis_sheet.range(thesis_pos["holding_period"]).value = holding_period
                thesis_sheet.range(thesis_pos["base_equity_cost"]).value = equity_cost

                model_wb.save()
                model_wb.close()
                print(f"Updated {path}")
        except Exception as e:
            print(f"Error updating {path}: {e}")
