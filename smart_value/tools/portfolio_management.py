"""portfolio_management.py - Portfolio Allocation and Management Logic

Purpose:
Handles portfolio allocation and management for the stock monitor system.

"""

import pandas as pd
from smart_value.tools.find_docs import col_to_num
from smart_value.data.monitor_data import (portfolio_mgmt_pos, opportunities_headers, opportunities_start_row)
import smart_value.tools.create_markdown


def update_monitor_data(monitor_wb, opportunities):
    """Update the Opportunities sheet with the latest opportunity data.

    Args:
        monitor_wb (xlwings.Book): The monitor workbook object.
        opportunities (list): List of MonitorStock objects containing opportunity data.

    Updates:
        Calculates allocation weights using the Half Kelly Allocation formula for eligible
        opportunities (Selected Flag = 'Y' and ERB > 0) and writes data to the Opportunities sheet.
    """
    sheet = monitor_wb.sheets['Opportunities']
    portfolio_mgmt_sheet = monitor_wb.sheets['Portfolio_Mgmt']

    # Read parameters from Portfolio_Mgmt sheet
    benchmark_return = portfolio_mgmt_sheet.range(portfolio_mgmt_pos['benchmark_return']).value
    p = portfolio_mgmt_sheet.range(portfolio_mgmt_pos['correct_chance']).value  # Valuation confidence
    l = portfolio_mgmt_sheet.range(portfolio_mgmt_pos['target_loss']).value     # Target loss if incorrect

    # Calculate allocation weights for each opportunity
    for opp in opportunities:
        market_annual_return = getattr(opp, 'market_ .annual_return', None)
        is_selected = getattr(opp, 'is_selected', None)

        # Ensure required values are available
        if (market_annual_return is not None and
            benchmark_return is not None and
            p is not None and
            l is not None):
            erb = market_annual_return - benchmark_return
            # Check eligibility: Selected Flag = 'Y' and ERB > 0
            if is_selected == 'Y' and erb > 0:
                w = market_annual_return  # Expected return if correct
                # Avoid division by zero
                if w != 0:
                    hk_allocation = (p * w + (1 - p) * l) / (2 * w)
                    # Ensure allocation is non-negative
                    opp.allocation_weight = max(hk_allocation, 0)
                else:
                    opp.allocation_weight = 0
            else:
                opp.allocation_weight = 0
        else:
            opp.allocation_weight = 0

    # Prepare data for writing to the sheet
    start_row = opportunities_start_row
    opportunities.sort(key=lambda opp: getattr(opp, 'market_annual_return', float('-inf')), reverse=True)
    buffer = 100
    last_row = start_row + buffer - 1
    sheet.range(f"B{start_row}:AA{last_row}").clear_contents()

    # Sort columns by numerical column position
    column_order = sorted(opportunities_headers.keys(), key=lambda x: col_to_num(opportunities_headers[x]))
    data = [{attr: getattr(opp, attr, None) for attr in column_order} for opp in opportunities]
    df = pd.DataFrame(data, columns=column_order)
    sheet.range(f"B{int(start_row)}").options(pd.DataFrame, header=False, index=False).value = df

    # Set formulas for ERB and ERC columns
    if opportunities:
        try:
            last_data_row = start_row + len(opportunities) - 1
            benchmark_ref = f"Portfolio_Mgmt!{portfolio_mgmt_pos['benchmark_return']}"
            cash_yield_ref = f"Portfolio_Mgmt!{portfolio_mgmt_pos['cash_yield']}"
            sheet.range(f"G{int(start_row)}:G{int(last_data_row)}").formula = f"=F{int(start_row)} - {benchmark_ref}"
            sheet.range(f"H{int(start_row)}:H{int(last_data_row)}").formula = f"=F{int(start_row)} - {cash_yield_ref}"
        except Exception as e:
            print(f"Error setting formulas: {e}")

    smart_value.tools.create_markdown.generate_monitor_md()
    print(f"Successfully updated {len(opportunities)} opportunities.")
