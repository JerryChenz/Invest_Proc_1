import xlwings as xw
import yfinance as yf
from smart_value.tools.find_docs import bank_monitor_file_path
import os
import time

# ============================================
# CONFIGURATION
# ============================================
EXCEL_FILE_PATH = str(bank_monitor_file_path)
SHEET_NAME = "Model"

PRIMARY_SYMBOL_COL   = "AH"
PRIMARY_PRICE_COL    = "AI"
SECONDARY_SYMBOL_COL = "AR"
SECONDARY_PRICE_COL  = "AS"

START_ROW = 6

# ============================================

def get_stock_price(symbol):
    if not symbol or not str(symbol).strip():
        return None
    try:
        ticker = yf.Ticker(str(symbol).strip().upper())
        info = ticker.info
        price = (
            info.get('currentPrice') or
            info.get('regularMarketPrice') or
            info.get('previousClose') or
            info.get('regularMarketPreviousClose')
        )
        return float(price) if price is not None else None
    except:
        return None


def open_workbook(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Always open in background (never visible)
    try:
        app = xw.App(visible=False, add_book=False)
        wb = app.books.open(file_path)
        return app, wb
    except Exception as e:
        raise RuntimeError(f"Failed to open workbook in background: {e}")


def update_price_cell(sheet, row, symbol_col, price_col):
    symbol = sheet.range(f"{symbol_col}{row}").value
    if not symbol or str(symbol).strip() == "":
        return False

    symbol = str(symbol).strip().upper()
    price = get_stock_price(symbol)
    price_cell = sheet.range(f"{price_col}{row}")

    if price is not None:
        price_cell.value = price
        price_cell.number_format = '$#,##0.00'
        return True
    else:
        price_cell.value = "ERROR"
        try:
            price_cell.font.color = (255, 0, 0)
        except:
            pass
        return False


def main():

    print("Starting...")
    if not os.path.exists(EXCEL_FILE_PATH):
        print("Error: File not found")
        print(f"  → {EXCEL_FILE_PATH}")
        return

    app = None
    wb = None

    try:
        app, wb = open_workbook(EXCEL_FILE_PATH)
        sheet = wb.sheets[SHEET_NAME]

        current_row = START_ROW
        primary_ok = 0
        primary_err = 0
        secondary_ok = 0
        secondary_err = 0
        rows_with_data = 0

        while True:
            if not sheet.range(f"{PRIMARY_SYMBOL_COL}{current_row}").value:
                break

            rows_with_data += 1

            # Primary
            if update_price_cell(sheet, current_row, PRIMARY_SYMBOL_COL, PRIMARY_PRICE_COL):
                primary_ok += 1
            else:
                primary_err += 1

            # Secondary (only if present)
            sec_symbol = sheet.range(f"{SECONDARY_SYMBOL_COL}{current_row}").value
            if sec_symbol and str(sec_symbol).strip():
                if update_price_cell(sheet, current_row, SECONDARY_SYMBOL_COL, SECONDARY_PRICE_COL):
                    secondary_ok += 1
                else:
                    secondary_err += 1

            current_row += 1

        # ── Minimal output when successful ─────────────────────────────
        total_ok = primary_ok + secondary_ok
        total_err = primary_err + secondary_err

        print(f"Processed {rows_with_data} rows")
        if total_err == 0:
            print(f"Successfully updated {total_ok} prices")
        else:
            print(f"Updated {total_ok} prices  |  Failed {total_err}")

        wb.save()

    except Exception as e:
        print(f"Error: {e}")
        if wb is not None:
            try:
                wb.save()
            except:
                pass

    finally:
        if wb is not None:
            try:
                wb.close()
            except:
                pass
        if app is not None:
            try:
                app.quit()
            except:
                try:
                    app.kill()
                except:
                    pass
        time.sleep(0.6)


if __name__ == "__main__":
    main()
