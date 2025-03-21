"""This file records the positions in the valuation model.

"""

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
    "fcfe_yield": "C55",
    "dividend_yield": "C56",
    # Calculate Stable Income Value Section
    "base_equity_cost": "C64",
    # Scenario Analysis Section
    "expected_equity_value": "C108"
}

user_data_pos = {
    'Thesis': [
        "C1", "F1",
        "C5:D8",
        "C16:C19",
        "E20",
        "C64", "D65,D66"
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
        "C52:C53", "C61", "C65:C67", "E46:E68",
        "C77", "C82", "C84:C85", "C89", "E71:E96"
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

