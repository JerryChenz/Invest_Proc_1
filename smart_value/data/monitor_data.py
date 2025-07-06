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
    "benchmark_return": "$C$10",
    "cash_yield": "$C$11",
    "max_holdings": "C27",
    "single_investment_cap": "C28",
    "correct_chance": "C32", "incorrect_loss": "E32",
    "target_return": "C33",
    "entry_yield": "C35",
    "holding_period": "C37", "equity_cost": "E37",
    "min_cash_reserve": "E66"
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
    "roe": "Q",
    "profit_sales": "R",
    "sales_assets": "S",
    "assets_equity": "T",
    "debt_equity": "U",
    "debt_ebit": "V",
    "realizable_value": "W",
    "comp_group": "X",
    "growth_class": "Y",
    "update_after": "Z",
    "is_selected": "AA"
}

# start row of the Opportunities.
opportunities_start_row = 3
