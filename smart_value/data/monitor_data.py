"""This file records the positions/headers in the stock monitor."""

market_yield_pos = {
    "us_riskfree": "C8",
    "us_prime": "D8",
    "cn_riskfree": "C9",
    "cn_prime": "D9",
    "hk_riskfree": "C10",
    "hk_prime": "D10"
}

portfolio_mgmt_pos = {
    "benchmark_return": "C10",
    "cash_yield": "C11",
    "max_holdings": "C26",
    "single_investment_cap": "C27",
    "negative_low_growth": "C30",
    "high_growth": "C31",
    "target_return": "C34",
    "holding_period": "E34",
    "equity_cost": "C35",
    "initial_cash_allocation": "E60",
    "sensitivity_factor": "C87",
    "max_cash_allocation": "C88",
    "adjusted_cash_allocation": "C100",
    "adjusted_portfolio_return": "C101",
}

opportunities_headers = {
    "symbol": "B",
    "name": "C",
    "price": "D",
    "price_currency": "E",
    "market_annual_return": "F",
    "ERB": "G",
    "ERC": "H",
    "allocation_weight": "I",
    "target_price": "J",
    "expected_equity_value": "K",
    "fcfe_yield": "L",
    "dividend_yield": "M",
    "comp_group": "N",
    "growth_class": "O",
    "update_after": "P",
    "is_selected": "Q"
}

# start row of the Opportunities.
opportunities_start_row = 3
