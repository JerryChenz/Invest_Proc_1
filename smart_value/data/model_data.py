"""This file records the positions in the valuation model."""

thesis_pos = {
    "last_revision": "C1", "is_selected": "F1",
    # Company Information Section
    "name": "C5",
    "shares_outstanding": "C6",
    "update_after": "C8",
    # Listing Information Section
    "symbol": "C11",
    "price": "C12",  # Aka. Market Price
    "price_currency": "C13",  # Aka. Market Currency
    "fx_rate": "C14",
    "symbol_secondary": "D11",
    "price_secondary": "D12",
    "price_currency_secondary": "D13",
    "fx_rate_secondary": "D14",
    # Valuation Overview Section
    "growth_class": "C21",
    "report_currency": "C22",
    "comp_group": "C23",
    "target_return": "C24", "entry_yield": 'E24',
    "holding_period": "E25",
    "market_annual_return": "C26",  # Aka. Market Implied Annual Return
    # Calculate FCFE Section
    "fcfe_yield": "C63",
    "dividend_yield": "C64",
    # Calculate Stable Income Value Section
    "base_equity_cost": "C72",
    # Adjusting for Financial Structure Section
    "liabilities_equity": "C93",
    "debt_equity": "C94",
    "debt_ebit": "C95",
    "realizable_value": "C109",
    # Scenario Analysis Section
    "expected_equity_value": "C122",
    # Investment Decision Section
    "target_price": 'C139',
    "entry_price": 'C147',
    "sell_price": "C155",
    "target_price_secondary": 'C139',
    "entry_price_secondary": 'C147',
    "sell_price_secondary": "C155"
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
        "C1", "F1",
        "C5:D7",
        "C11:D13",
        "C16:D16",
        "C22:C24",
        "E24:E25",
        "C72", "D73:D74",
        "D73:D74"
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
