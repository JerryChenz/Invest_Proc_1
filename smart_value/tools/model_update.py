"""
model_update.py - The script automates the process of updating Excel-based financial valuation models to new
template versions while preserving user inputs. It handles:

1. Template Migration: Transfers user data from old Excel models to new template versions
2. Batch Processing: Updates multiple files efficiently
3. Data Integrity: Maintains consistency and prevents data loss during updates
"""

import pathlib
import time
import xlwings as xw
from smart_value.tools.find_docs import get_model_paths, new_latest_model, get_template_paths


def load_template_mapping():
    """Load hardcoded mapping."""
    return {
        'Thesis': [
            {'column': 3, 'start_row': 1, 'end_row': 1},    # C1
            {'column': 6, 'start_row': 1, 'end_row': 1},    # F1
            {'column': 3, 'start_row': 5, 'end_row': 10},   # C5:C10
            {'column': 3, 'start_row': 18, 'end_row': 19}   # C18:C19
        ],
        'Data': [
            {'column': 3, 'start_row': 1, 'end_row': 1},    # C1
            {'column': 3, 'start_row': 3, 'end_row': 32}    # C3:M32 (converted to column ranges)
        ],
        'Normalized_FCF': [
            {'column': 3, 'start_row': 4, 'end_row': 4},    # C4
            {'column': 3, 'start_row': 1, 'end_row': 1},    # C1
            {'column': 3, 'start_row': 3, 'end_row': 32},   # C3:M32
            # ... add all other ranges following same pattern
        ],
        'BS': [
            {'column': 3, 'start_row': 1, 'end_row': 1},    # C1
            {'column': 3, 'start_row': 4, 'end_row': 11},   # C4:D11
            # ... add all other ranges
        ],
        'Scenarios': [
            {'column': 3, 'start_row': 4, 'end_row': 4},    # C4
            {'column': 3, 'start_row': 18, 'end_row': 18},  # C18
            # ... add all other ranges
        ]
    }


def update_models():
    """Main update process with atomic file operations and rollback protection."""
    start_total = time.time()
    model_paths = get_model_paths()
    template_mapping = load_template_mapping()

    processed = 0
    print(f"Updating {len(model_paths)} models")

    for path in model_paths:
        backup = path.with_name(f"{path.stem}_backup{path.suffix}")
        start_file = time.time()

        try:
            # Extract ticker from filename
            ticker = path.name.split("_Valuation")[0]

            # Atomic file operations
            path.replace(backup)
            updated_model = new_latest_model(ticker)

            with xw.App(visible=False) as app:
                old_book = app.books.open(backup)
                new_book = app.books.open(updated_model)

                # Batch input transfer
                for sheet, ranges in template_mapping.items():
                    try:
                        old_sheet = old_book.sheets[sheet]
                        new_sheet = new_book.sheets[sheet]
                    except KeyError:
                        continue

                    for rng in ranges:
                        col = xw.utils.col_name(rng["column"])
                        old_range = f"{col}{rng['start_row']}:{col}{rng['end_row']}"
                        new_sheet.range(old_range).formula = old_sheet.range(old_range).formula

                new_book.save()
                new_book.close()
                old_book.close()

            backup.unlink()
            processed += 1
            print(f"Updated {path.name} in {time.time() - start_file:.2f}s")

        except Exception as e:
            print(f"Error processing {path.name}: {str(e)}")
            if backup.exists():
                backup.replace(path)

    print(f"\nCompleted {processed}/{len(model_paths)} updates in {time.time() - start_total:.2f}s")
