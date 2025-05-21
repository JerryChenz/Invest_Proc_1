"""This file records the positions in the valuation model."""

thesis_pos = {
    "last_revision": "C1",
    "portfolio_code": "D1",
    "is_selected": "F1",
    # Company Information Section
    "name": "C5",
    "shares_outstanding": "C6",
    "update_after": "C8",
    # Listing Information Section
    "symbol": "C11",
    "price": "C12",  # Aka. Market Price
    "price_currency": "C13",  # Aka. Market Currency
    "fx_rate": "C16",
    "symbol_secondary": "D11",
    "price_secondary": "D12",
    "price_currency_secondary": "D13",
    "fx_rate_secondary": "D16",
    # Valuation Overview Section
    "growth_class": "C21",
    "valuation_method": "E21",
    "comp_group": "C22",
    "report_currency": "C25",
    "expected_equity_value": "C26",
    "market_annual_return": "E26",  # Aka. Market Implied Annual Return
    # Valuation Outputs Section
    "holding_period": "F28",
    "target_price": 'C29', "target_price_secondary": 'D29',
    "entry_price": 'C30', "entry_price_secondary": 'D30',
    "sell_price": "C31", "sell_price_secondary": "D31",
    "exit_price": "C32", "exit_price_secondary": "D32",
    "target_return": "F29",
    "entry_yield": 'F30',
    "base_equity_cost": "F31",
    "benchmark_return": "F32",
    # Calculate FCFE Section
    "fcfe_yield": "C69",
    "dividend_yield": "C70",
    "roe": "C73",
    "profit_sales": "C74",
    "sales_assets": "C75",
    "assets_equity": "C76",
    # Adjusting for Financial Structure Section
    "debt_equity": "C104",
    "debt_ebit": "C105",
    "realizable_value": "C119"
}

data_pos = {
    # Income Statement
    "date_of_last_annual_report": "C1", "scaling_factor": "C3",
    "sales": "C4:M4", "cogs": "C5:M5",
    "opex": "C6:M6", "selling_expenses": "C7:M7",
    "research_development": "C8:M8", "jv_result": "C9:M9",
    "securities_income": "C10:M10", "property_income": "C11:M11",
    "interest_expense": "C12:M12", "interest_income": "C13:M13",
    "income_tax": "C14:M14", "net_income": "C15:M15", "nc_income": "C16:M16",
    # Cash Flow Statement
    "da": "C19:M19", "capex": "C20:M20", "wcinv": "C21:M21",
    "cfo": "C22:M22", "cfi": "C23:M23", "cff": "C24:M24",
    "dividend_per_share": "C25:M25",
    # Balance Sheet
    "Account_receivable": "D28:M28", "inventory": "D29:M29",
    "total_liabilities": "D30:M30", "total_equity": "D31:M31", "nc_interest": "D32:M32"
}

user_data_pos = {
    'Thesis': [
        "C1", "D1", "F1",
        "C5:D7",
        "C11:D13",
        "C16:D16",
        "C22:C25", "E21:E22",
        "F28:F32"
    ],
    'Data': [
        "C1",
        "C3:M32"
    ],
    'BS': [
        "C1",
        "C4:C11", "G4:H11",
        "C15:D23", "G15:H23",
        "C27:C30", "C33",
        "C36:C39", "C42",
        "G28",
        "D76"
    ],
    'Normalized_FCF': [
        "C4", "E3:E19",
        "C28:C29", "C33:C34", "C43", "E22:E43",
        "C53:C54", "C62", "C66:C68", "E46:E69",
        "C78", "C83", "C85", "C90", "E71:E97"
    ],
    'Scenarios': [
        "C4",
        "C18",
        "C26", "C28", "E25",
        "C32", "C34", "E31",
        "C38", "E37",
        "C46",
        "C50", "C52", "E49",
        "C56", "C58", "E55",
        "C65"
    ]
}
