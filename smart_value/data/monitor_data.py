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
    "max_holdings": "C25",
    "single_investment_cap": "C26",
    "target_return": "C29",
    "holding_period": "E29",
    "equity_cost": "C30",
    "cash_allocation": "C56"
}

opportunities_headers = {
    "symbol": "B",
    "name": "C",
    "price": "D",
    "price_currency": "E",
    "market_annual_return": "F",
    "ERB": "G",
    "ERC": "H",
    "target_price": "I",
    "expected_equity_value": "J",
    "fcfe_yield": "K",
    "dividend_yield": "L",
    "comp_group": "M",
    "growth_class": "N",
    "update_after": "O",
    "is_selected": "P"
}

# start row of the Opportunities.
opportunities_start_row = 3
