"""This file records the positions in the valuation model."""

thesis_pos = {
    # Model Information Section
    "last_revision": "F3",
    "portfolio_code": "F4",
    "is_selected": "F5",
    # Company Information Section
    "name": "C4",
    "symbol": "C5",
    "comp_group": "C6",
    "price_currency": "C7",  # Aka. Market Currency
    "price": "C8",  # Aka. Market Price
    "market_annual_return": "E9",  # Aka. Market Implied Annual Return
    "shares_outstanding": "C9",
    # DCF Conclusion Section
    "expected_equity_value": "C19",
    "growth_class": "C19",
    "fx_rate": "E16",
    "report_currency": "E17",
    "update_after": "E19",
    # Price Target Section
    "target_price": 'C22',
    "entry_price": 'C23',
    "exit_price": "C24",
    "sell_price": "C25",
    "holding_period": "E21",
    "target_return": "E22",
    "entry_yield": 'E23',
    "benchmark_return": "E24",
    "base_equity_cost": "E25",
    # Calculate FCFE Section
    "fcfe_yield": "C62",
    "dividend_yield": "C63",
    "roe": "C66",
    "profit_sales": "C67",
    "sales_assets": "C68",
    "assets_equity": "C69",
    # Adjusting for Financial Structure Section
    "debt_equity": "C80",
    "debt_ebit": "C81",
    "realizable_value": "C111"
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
        "F3:F5",
        "C4:D9",
        "C15:C17",
        "E16:E18",
        "E21:E25"
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
        "C29:C31", "C35", "C41", "E22:E41",
        "C51:C52", "C60", "C64:C66", "E44:E67",
        "C79", "C82:C83", "C88", "C91", "E70:E96"
    ],
    'Scenarios': [
        "C4",
        "C18",
        "C22:C24", "F23:F24",
        "C29:C30", "F29:F30",
        "C40:C41",
        "C46"
    ]
}
