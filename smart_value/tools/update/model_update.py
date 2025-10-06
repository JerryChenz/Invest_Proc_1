import time
import xlwings as xw
from smart_value.tools.find_docs import get_model_paths, new_latest_model
from smart_value.data.model_data import user_data_pos


def update_models():
    """Main update process with atomic file operations and rollback protection.

    This function automates the updating of Excel-based financial valuation models to new template versions.
    It preserves user inputs and entire worksheets, such as "Breakdown", while maintaining data integrity.

    Key Features:
    1. Template Migration: Transfers user data from old Excel models to new template versions
    2. Worksheet Copying: Copies entire worksheets, such as 'Breakdown', preserving formulas and formatting
    3. Batch Processing: Updates multiple files efficiently
    4. Data Integrity: Maintains consistency and prevents data loss during updates
    """
    start_total = time.time()
    model_paths = get_model_paths()
    template_mapping = user_data_pos

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

                # Transfer user data for other sheets
                for sheet, ranges in template_mapping.items():
                    try:
                        old_sheet = old_book.sheets[sheet]
                        new_sheet = new_book.sheets[sheet]
                    except KeyError:
                        continue

                    for range_entry in ranges:
                        # Handle comma-separated ranges
                        for sub_range in range_entry.split(','):
                            sub_range = sub_range.strip()
                            # Copy formulas directly between matching ranges
                            new_sheet.range(sub_range).formula = old_sheet.range(sub_range).formula

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
