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
    "max_holdings": "C27",
    "single_investment_cap": "C28",
    "negative_low_growth": "C31",
    "high_growth": "C32",
    "target_return": "C35",
    "holding_period": "E35",
    "equity_cost": "C36",
    "min_cash_reserve": "E61",
    "projected_cash": "C111",
    "projected_portfolio_return": "C112",
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
