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
    "equity_cost": "$C$12",
    "max_holdings": "C30",
    "single_investment_cap": "C31",
    "holding_period": "C36",
    "correct_chance": "C37",
    "incorrect_loss": "C38",
    "target_return": "C46",
    "entry_yield": "C47",
    "min_cash_reserve": "E73"
}

opportunities_headers = {
    "symbol": "B",
    "name": "C",
    "price": "D",
    "price_currency": "E",
    "market_annual_return": "F",
    "allocation_weight": "G",
    "target_price": "H",
    "expected_equity_value": "I",
    "sell_price": "J",
    "entry_price": "K",
    "exit_price": "L",
    "fcfe_yield": "M",
    "dividend_yield": "N",
    "roe": "O",
    "profit_sales": "P",
    "sales_assets": "Q",
    "assets_equity": "R",
    "debt_equity": "S",
    "debt_ebit": "T",
    "realizable_value": "U",
    "comp_group": "V",
    "growth_class": "W",
    "update_after": "X",
    "is_selected": "Y"
}

# start row of the Opportunities.
opportunities_start_row = 3
