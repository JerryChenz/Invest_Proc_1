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
    "benchmark_return": "C12",
    "cash_yield": "C13",
    "max_holdings": "C29",
    "single_investment_cap": "C30",
    "negative_low_growth": "C33",
    "high_growth": "C34",
    "target_return": "C37",
    "holding_period": "E37",
    "equity_cost": "C38",
    "min_cash_reserve": "E63",
    "projected_cash": "C113",
    "projected_portfolio_return": "C114",
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
