"""This file records the positions/headers in the stock monitor."""

market_yield_pos = {
    "us_riskfree": "C4",
    "us_prime": "D4",
    "cn_riskfree": "C5",
    "cn_prime": "D5",
    "hk_riskfree": "C6",
    "hk_prime": "D6"
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
    "entry_yield": "E36",
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
    "sell_price": "L",
    "entry_price": "M",
    "exit_price": "N",
    "fcfe_yield": "O",
    "dividend_yield": "P",
    "liabilities_equity": "Q",
    "debt_equity": "R",
    "debt_ebit": "S",
    "realizable_value": "T",
    "comp_group": "U",
    "growth_class": "V",
    "update_after": "W",
    "is_selected": "X"
}

# start row of the Opportunities.
opportunities_start_row = 3
