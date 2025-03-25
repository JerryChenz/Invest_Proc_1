"""This file records the positions in the valuation model."""

thesis_pos = {
    "last_revision": "C1", "is_hold": "F1",
    # Stock Information Section
    "name": "C5", "symbol": "D5",
    "price": "C6", "price_currency": "D6",
    "shares_outstanding": "C7",
    "update_after": "C9",
    # Valuation Overview Section
    "investment_type": "C15",
    "report_currency": "C16", "fx_rate": "C17",
    "comp_group": "C18",
    "target_return": "C19",
    "target_price": 'C20',
    "holding_period": "E20",
    "market_annual_return": "C21",
    # Calculate FCFE Section
    "fcfe_yield": "C58",
    "dividend_yield": "C59",
    # Calculate Stable Income Value Section
    "base_equity_cost": "C67",
    # Scenario Analysis Section
    "expected_equity_value": "C112"
}

data_pos = {
    # Income Statement
    "date_of_last_annual_report": "C1", "figure_in": "C3",
    "sales": "C4:M4", "cogs": "C5:M5",
    "opex": "C6:M6", "selling_expenses": "C7:M7",
    "research_development": "C8:M8", "jv_result": "C9:M9",
    "securities_income": "C10:M10", "property_income": "C11:M11",
    "interest_expense": "C12:M12", "interest_income": "C13:M13",
    "income_tax": "C14:M14", "net_income": "C15:M15", "nc_income": "C16:M16",
    # Cash Flow Statement
    "da": "C19:M19", "capex": "C20:M20", "wcinv": "C21:M21",
    "dividend_per_share": "C22:M22",
    # Balance Sheet
    "Account_receivable": "C25:M25", "inventory": "C26:M26",
    "total_liabilities": "C27:M27", "total_equity": "C28:M28", "nc_interest": "C29:M29"
}

user_data_pos = {
    'Thesis': [
        "C1", "F1",
        "C5:D8",
        "C16:C19",
        "E20",
        "C67", "D68:D69"
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
