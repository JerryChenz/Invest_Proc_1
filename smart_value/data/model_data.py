"""This file records the positions in the valuation model.

"""

thesis_pos = {
    "last_revision": "C1",
    "is_hold": "F1",
    # Executive Summary
    "name": "C5",
    "symbol": "D5",
    "price": "C6",
    "price_currency": "D6",
    "shares_outstanding": "C7",
    "report_currency": "C8",
    "fx_rate": "C9",
    "update_after": "C11",
    "investment_type": "C17",
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
            {'column': 3, 'start_row': 1, 'end_row': 1},   # C1
            {'column': 6, 'start_row': 1, 'end_row': 1},   # F1
            {'column': 3, 'start_row': 5, 'end_row': 10},  # C5:D6
            {'column': 3, 'start_row': 7, 'end_row': 10},  # C7:C10
            {'column': 3, 'start_row': 18, 'end_row': 19}  # C18:C19
        ],
        'Data': [
            {'column': 3, 'start_row': 1, 'end_row': 1},    # C1
            {'column': 3, 'start_row': 3, 'end_row': 32}    # C3:M32
        ],
        'Normalized_FCF': [
            {'column': 3, 'start_row': 4, 'end_row': 4},    # C4
            {'column': 3, 'start_row': 28, 'end_row': 29},  # C28:C29
            {'column': 3, 'start_row': 33, 'end_row': 34},  # C33:C34
            {'column': 3, 'start_row': 43, 'end_row': 43},  # C43
            {'column': 3, 'start_row': 52, 'end_row': 53},  # C52:C53
            {'column': 3, 'start_row': 61, 'end_row': 61},  # C61
            {'column': 3, 'start_row': 65, 'end_row': 67},  # C65:C67
            {'column': 3, 'start_row': 77, 'end_row': 77},  # C77
            {'column': 3, 'start_row': 82, 'end_row': 82},  # C82
            {'column': 3, 'start_row': 84, 'end_row': 85},  # C84:C85
            {'column': 3, 'start_row': 89, 'end_row': 89},  # C89
        ],
        'BS': [
            {'column': 3, 'start_row': 1, 'end_row': 1},   # C1
            {'column': 3, 'start_row': 4, 'end_row': 11},  # C4:D11
            # G4:H11
            # C15:D23
            # C33
            # C36:C39
            # C42
            # G28
        ],
        'Scenarios': [
            {'column': 3, 'start_row': 4, 'end_row': 4},    # C4
            {'column': 3, 'start_row': 18, 'end_row': 18},  # C18
            # E25
            # C26
            # C28
            # E31
            # C32
            # C34
            # E37
            # C38
            # C46
            # E49
            # C50
            # C52
            # E55
            # C56
            # C58
            # F60
            # C65
        ]
    }

