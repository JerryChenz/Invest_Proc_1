import xlwings as xw
import yfinance as yf
from smart_value.tools.find_docs import bank_monitor_file_path

# ============================================
# CONFIGURATION - Update these values
# ============================================
EXCEL_FILE_PATH = bank_monitor_file_path
SHEET_NAME = "Sheet1"  # Change to your sheet name
SYMBOL_COL = "AR"  # Column for stock symbols
PRICE_COL = "AS"  # Column for stock prices
START_ROW = 6  # Starting row


# ============================================

def get_stock_price(symbol):
    """
    Fetch current stock price using yfinance.
    Returns price as float or None if failed.
    """
    try:
        # Clean symbol
        ticker_symbol = str(symbol).strip().upper()

        # Handle common suffix variations if needed
        # Example: Add .HK for Hong Kong stocks without suffix
        # if ticker_symbol.isdigit() and len(ticker_symbol) == 4:
        #     ticker_symbol += ".HK"

        # Fetch ticker data
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info

        # Try multiple fields to get current price
        price = (
                info.get('currentPrice') or  # Primary: current price
                info.get('regularMarketPrice') or  # Alternative: market price
                info.get('previousClose') or  # Fallback: previous close
                info.get('bid') or  # Last resort: bid price
                info.get('navPrice')  # For ETFs/Mutual funds
        )

        return float(price) if price else None

    except Exception as e:
        print(f"  Error fetching {symbol}: {e}")
        return None


def main():
    """
    Main function: Connects to Excel and updates stock prices using while loop.
    """
    print("=" * 60)
    print("STOCK PRICE UPDATER")
    print("=" * 60)

    # Connect to Excel workbook
    print(f"\nConnecting to: {EXCEL_FILE_PATH}")
    try:
        # Try to connect to already open workbook
        wb = xw.Book(EXCEL_FILE_PATH)
        print("Connected to open workbook")
    except Exception:
        # Open new connection
        wb = xw.Book(EXCEL_FILE_PATH)
        print("Opened workbook")

    # Select worksheet
    sheet = wb.sheets[SHEET_NAME]
    print(f"Active sheet: {SHEET_NAME}")

    # Initialize counters
    current_row = START_ROW
    updated = 0
    failed = 0

    print(f"\nStarting updates from row {START_ROW}...")
    print("-" * 60)

    # WHILE LOOP: Continue until empty cell in symbol column
    while True:
        # Read stock symbol from Column AR
        symbol_cell = sheet.range(f"{SYMBOL_COL}{current_row}")
        symbol = symbol_cell.value

        # Exit condition: Empty cell means end of list
        if symbol is None or str(symbol).strip() == "":
            print(f"\nEnd of list reached at row {current_row}")
            break

        symbol = str(symbol).strip().upper()
        print(f"Row {current_row:3d}: {symbol:10s} -> ", end="", flush=True)

        # Get price from Yahoo Finance
        price = get_stock_price(symbol)

        # Write to Column AS
        price_cell = sheet.range(f"{PRICE_COL}{current_row}")

        if price is not None:
            price_cell.value = price
            price_cell.number_format = '$#,##0.00'
            print(f"${price:,.2f}")
            updated += 1
        else:
            price_cell.value = "ERROR"
            price_cell.font.color = (255, 0, 0)  # Red text for errors
            print("FAILED")
            failed += 1

        # Move to next row
        current_row += 1

    # Save and close
    print("-" * 60)
    print("Saving workbook...")
    wb.save()

    # Summary
    print("\n" + "=" * 60)
    print("UPDATE COMPLETE")
    print("=" * 60)
    print(f"Total rows processed: {updated + failed}")
    print(f"Successfully updated: {updated}")
    print(f"Failed: {failed}")
    print(f"Last row checked: {current_row - 1}")
    print("=" * 60)


if __name__ == "__main__":
    main()
