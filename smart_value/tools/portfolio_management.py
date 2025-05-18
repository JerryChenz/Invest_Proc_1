"""portfolio_management.py - Portfolio Allocation and Management Logic

Purpose:
Handles portfolio allocation and management for the stock monitor system.
Calculates allocation weights, filters eligible opportunities, and computes
projected portfolio returns base on financial parameters.

Key Features:
1. Filters opportunities based on selection criteria and growth classifications.
2. Calculates allocation weights respecting constraints like max holdings.
3. Adjusts allocations to meet investable capital limits.
4. Computes projected cash reserves and portfolio returns.
5. Supports two portfolios (INT and CN) with separate parameters.

Dependencies:
- xlwings: For accessing Excel workbook data.
- smart_value.data.monitor_data: For portfolio management positions.
"""

from smart_value.data.monitor_data import portfolio_mgmt_pos


def calculate_allocation_weights(monitor_wb, opportunities):
    """Calculate allocation weights for the portfolio.

    Args:
        monitor_wb (xlwings.Book): The monitor workbook.
        opportunities (list): List of MonitorStock objects.

    Steps:
    1. Retrieve portfolio parameters from Portfolio_Mgmt sheet.
    2. Filter eligible opportunities (Selected Flag = 'Y', ERB > 0).
    3. Enforce max holdings and growth classification limits.
    4. Calculate provisional weights, adjust for delta, and enforce capital limits.
    5. Compute projected cash reserve and portfolio return.
    6. Write results to Portfolio_Mgmt sheet.
    """
    portfolio_mgmt_sheet = monitor_wb.sheets['Portfolio_Mgmt']

    # Retrieve parameters
    try:
        benchmark_return = float(portfolio_mgmt_sheet.range(portfolio_mgmt_pos["benchmark_return"]).value)
        cash_yield = float(portfolio_mgmt_sheet.range(portfolio_mgmt_pos["cash_yield"]).value)
        max_holdings = int(portfolio_mgmt_sheet.range(portfolio_mgmt_pos["max_holdings"]).value)
        single_investment_cap = float(portfolio_mgmt_sheet.range(portfolio_mgmt_pos["single_investment_cap"]).value)
        negative_low_growth_cap = int(portfolio_mgmt_sheet.range(portfolio_mgmt_pos["negative_low_growth"]).value)
        high_growth_cap = int(portfolio_mgmt_sheet.range(portfolio_mgmt_pos["high_growth"]).value)
        target_return = float(portfolio_mgmt_sheet.range(portfolio_mgmt_pos["target_return"]).value)
        min_cash_reserve = float(portfolio_mgmt_sheet.range(portfolio_mgmt_pos["min_cash_reserve"]).value)
    except Exception as e:
        print(f"Error reading portfolio parameters: {e}")
        return

    # Filter eligible opportunities
    eligible_opportunities = [
        opp for opp in opportunities
        if getattr(opp, 'is_selected', '') == 'Y' and (getattr(opp, 'market_annual_return', 0) - benchmark_return) > 0
    ]

    # Enforce max holdings and growth limits
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
        if growth_class == 'High Growth' and hg_count >= high_growth_cap:
            continue
        elif growth_class in ['Negative', 'Low Growth'] and nlg_count >= negative_low_growth_cap:
            continue
        if len(selected_opportunities) >= max_holdings:
            break
        if growth_class == 'High Growth':
            hg_count += 1
        elif growth_class in ['Negative', 'Low Growth']:
            nlg_count += 1
        selected_opportunities.append(opp)

    # Calculate weights
    if not selected_opportunities:
        projected_cash = 1.0
        projected_portfolio_return = cash_yield
    else:
        for opp in selected_opportunities:
            r_i = getattr(opp, 'market_annual_return', 0)
            delta = max(0, (target_return - r_i) / target_return)
            provisional_weight = single_investment_cap
            opp.allocation_weight = provisional_weight * (1 - delta)

        allocated_weight = sum(getattr(opp, 'allocation_weight', 0) for opp in selected_opportunities)
        investable_capital = 1 - min_cash_reserve

        if allocated_weight > investable_capital:
            sorted_by_erb = sorted(
                selected_opportunities,
                key=lambda opp: (getattr(opp, 'market_annual_return', 0) - benchmark_return),
                reverse=True
            )
            cumulative = 0.0
            for i, opp in enumerate(sorted_by_erb):
                current_weight = getattr(opp, 'allocation_weight', 0)
                if cumulative + current_weight <= investable_capital:
                    cumulative += current_weight
                else:
                    opp.allocation_weight = investable_capital - cumulative
                    cumulative = investable_capital
                    for remaining_opp in sorted_by_erb[i + 1:]:
                        remaining_opp.allocation_weight = 0.0
                    break
            allocated_weight = cumulative

        projected_cash = 1 - allocated_weight
        investment_return = sum(
            getattr(opp, 'allocation_weight', 0.0) * getattr(opp, 'market_annual_return', 0.0)
            for opp in selected_opportunities
        )
        projected_portfolio_return = investment_return + (projected_cash * cash_yield)

    for opp in opportunities:
        if opp not in selected_opportunities:
            opp.allocation_weight = 0.0

    # Write results
    try:
        portfolio_mgmt_sheet.range(portfolio_mgmt_pos["projected_cash"]).value = projected_cash
        portfolio_mgmt_sheet.range(portfolio_mgmt_pos["projected_portfolio_return"]).value = projected_portfolio_return
    except Exception as e:
        print(f"Error writing portfolio results: {e}")
