"""portfolio_management.py - Portfolio Allocation and Management Logic

Purpose:
Handles portfolio allocation and management for the stock monitor system.

"""

import pandas as pd
from smart_value.tools.find_docs import col_to_num
from smart_value.data.monitor_data import (portfolio_mgmt_pos, opportunities_headers, opportunities_start_row)
import smart_value.tools.create_markdown


def calculate_allocation_weight(market_annual_return, is_selected, years, benchmark_return, p, incorrect_loss):
    """
    Calculate the allocation weight for an opportunity using the Half Kelly Criterion.

    Args:
        market_annual_return: The opportunity's return at market price.
        is_selected: Flag for selected opportunities.
        years: Expected Holding Period.
        benchmark_return (float): The benchmark return rate (e.g., 11.74%).
        p (float): Valuation confidence (probability of intrinsic value accuracy).
        incorrect_loss (float): Expected loss at est. intrinsic value when incorrect.

    Returns:
        float: The allocation weight, or 0 if ineligible or calculation fails.
    """

    # Check if all required attributes are present and investment is eligible
    if market_annual_return is not None:
        erb = market_annual_return - benchmark_return
        if erb > 0:  # Eligibility: ERB > 0
            w = market_annual_return  # Expected return at current market price
            if w != 0:  # Avoid division by zero
                # --- STEP 1: N-year compounded gain if right --------------------------
                total_gain = (1 + market_annual_return) ** years - 1

                # --- STEP 2: gain / loss ratio (Kelly's b) -----------------------------
                b = total_gain / abs(incorrect_loss)

                # --- STEP 3: raw Kelly -------------------------------------------------
                q = 1 - p
                kelly = (b * p - q) / b

                # --- STEP 4: half Kelly ------------------------------------------------
                half_kelly = kelly / 2
                if is_selected == "N":
                    half_kelly = half_kelly / 2

                # --- STEP 5: return ----------------------------------------------------
                allocation_weight = max(0.0, half_kelly)  # never negative
                return allocation_weight
    return 0


def update_monitor_data(monitor_wb, opportunities):
    """
    Update the Opportunities sheet with opportunity data and allocation weights.

    Args:
        monitor_wb (xlwings.Book): The monitor workbook object.
        opportunities (list): List of MonitorStock objects with opportunity data.

    Process:
        1. Retrieves portfolio parameters from Portfolio_Mgmt sheet.
        2. Calculates allocation weights for each opportunity.
        3. Writes sorted opportunity data to the Opportunities sheet.
        4. Sets ERB and ERC formulas.
    """
    # Access required sheets
    sheet = monitor_wb.sheets['Opportunities']
    portfolio_mgmt_sheet = monitor_wb.sheets['Portfolio_Mgmt']

    # Retrieve parameters from Portfolio_Mgmt sheet
    benchmark_return = portfolio_mgmt_sheet.range(portfolio_mgmt_pos['benchmark_return']).value
    p = portfolio_mgmt_sheet.range(portfolio_mgmt_pos['correct_chance']).value  # e.g., 60%
    incorrect_loss = portfolio_mgmt_sheet.range(portfolio_mgmt_pos['incorrect_loss']).value  # e.g., -15%

    # Calculate allocation weights
    for opp in opportunities:
        market_annual_return = getattr(opp, 'market_annual_return', None)
        is_selected = getattr(opp, 'is_selected', None)
        price = getattr(opp, 'price', None)
        entry_price = getattr(opp, 'entry_price', None)
        years = getattr(opp, 'holding_period', None)
        opp.allocation_weight = calculate_allocation_weight(market_annual_return, is_selected, years,
                                                            benchmark_return, p, incorrect_loss)

    # Sort opportunities by market_annual_return (equivalent to ERB descending)
    opportunities.sort(key=lambda opp: getattr(opp, 'market_annual_return', float('-inf')), reverse=True)

    # Prepare and write data to the sheet
    start_row = opportunities_start_row
    buffer = 100
    last_row = start_row + buffer - 1
    sheet.range(f"B{start_row}:AA{last_row}").clear_contents()

    column_order = sorted(opportunities_headers.keys(), key=lambda x: col_to_num(opportunities_headers[x]))
    data = [{attr: getattr(opp, attr, None) for attr in column_order} for opp in opportunities]
    df = pd.DataFrame(data, columns=column_order)
    sheet.range(f"B{int(start_row)}").options(pd.DataFrame, header=False, index=False).value = df

    # Set ERB and ERC formulas if there are opportunities
    if opportunities:
        try:
            last_data_row = start_row + len(opportunities) - 1
            benchmark_ref = f"Portfolio_Mgmt!{portfolio_mgmt_pos['benchmark_return']}"
            cash_yield_ref = f"Portfolio_Mgmt!{portfolio_mgmt_pos['cash_yield']}"
            sheet.range(f"G{int(start_row)}:G{int(last_data_row)}").formula = f"=F{int(start_row)} - {benchmark_ref}"
            sheet.range(f"H{int(start_row)}:H{int(last_data_row)}").formula = f"=F{int(start_row)} - {cash_yield_ref}"
        except Exception as e:
            print(f"Error setting formulas: {e}")

    # Generate markdown and log completion
    smart_value.tools.create_markdown.generate_monitor_md()
    print(f"Successfully updated {len(opportunities)} opportunities.")


if __name__ == '__main__':
    half_kelly = calculate_allocation_weight(0.23,
                                             "Y", 3, 0.11, 0.6, -0.75)
    assert round(half_kelly * 100, 1) == 12.6, "Incorrect Half Kelly"
