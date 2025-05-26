import yfinance as yf
import pandas as pd
import numpy as np
import time
import xlwings as xw

"""
Script to scrape financial data from Yahoo Finance and calculate key metrics for a stock screener spreadsheet.

This script performs the following main functions:
1. Reads stock tickers from a specified sheet in the Excel file
2. Retrieves financial data from Yahoo Finance with error handling
3. Calculates fundamental analysis metrics with currency conversions
4. Generates a combined quality ranking system
5. Updates the specified sheet in the Excel spreadsheet with fresh data

Input Requirements:
- 'financial_models/level2_screener.xlsx' must exist
- The specified sheet (hk_screener, cn_screener, or us_screener) must exist in the workbook
- Tickers list starts in column B (row 2+) in the specified sheet
- Excel file must have write permissions

Output Details:
- Updates columns C-R in the specified sheet with the following metrics:
    C: Company Name
    D: Industry
    E: Market Price (local currency)
    F: Market Currency
    G: Market Capitalization
    H: 52 Week High
    I: 52 Week Low
    J: percent_from_low
    K: Dividend Yield (Dividend/Price)
    L: EBIT (Earnings Before Interest & Taxes)
    M: Invested Capital
    N: Report Currency
    O: FX Rate (Market/Report Currency)
    P: EBIT/EV Ratio
    Q: ROIC (Return on Invested Capital)
    R: Combined Quality Ranking

Key Implementation Details:
- Data Retrieval:
  - Uses yfinance with 3 retries (10s wait) per ticker
  - Processes in batches of 10 with 1s delay between batches
  - Handles missing data: NaN for numbers, 'N/A' for strings

- Financial Calculations:
  - EBIT = Total Revenue - Cost of Revenue - Operating Expenses
  - Enterprise Value = Market Cap + Total Debt - Cash
  - ROIC = EBIT / Invested Capital
  - Dividend Yield = Annual Dividend Rate / Current Price

- Currency Handling:
  - Hard-coded USD rates: CNY=7.2, HKD=0.13, JPY=142.63
  - Converts EBIT to report currency using FX rate
  - Only supports USD/CNY/HKD/JPY conversions
  - Excludes tickers with unsupported currencies from rankings

- Quality Ranking System:
  1. Calculates EBIT/EV and ROIC separately
  2. Ranks both metrics (higher values better)
  3. Sums individual ranks
  4. Creates final ranking from summed ranks
  5. Only includes tickers with valid FX rates and both metrics

Technical Notes:
- Requires xlwings Excel integration
- Runs Excel in background (visible=False)
- Preserves existing spreadsheet formatting
- Saves and closes workbook properly on completion
- Uses pandas for data manipulation
- Implements NaN handling for financial calculations
- User is prompted to choose which sheet to update
"""

# Global parameter for Excel file path
EXCEL_FILE_PATH = 'financial_models/level2_screener.xlsx'

rate_to_usd = {
    'USD': 1.0,
    'CNY': 1 / 7.2,
    'HKD': 0.13,
    'MOP': 0.12,
    'JPY': 1 / 142.63,
    'EUR': 1.1381
}


def get_exchange_rate(market_currency, report_currency):
    """Calculate FX rate between market and report currencies."""
    try:
        return rate_to_usd[report_currency] / rate_to_usd[market_currency]
    except KeyError:
        return np.nan


def get_ticker_data(ticker, retries=3, wait_time=10):
    """Enhanced financial data retrieval with proper statement sorting."""
    for attempt in range(retries):
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            # Base data structure
            data = {
                'Ticker': ticker,
                'Company Name': info.get('shortName', 'N/A'),
                'Industry': info.get('industry', 'N/A'),
                'Market Price': info.get('currentPrice', np.nan),
                'Market Currency': info.get('currency', 'N/A'),
                'Market Capitalization': info.get('marketCap', np.nan),
                '52 week high': info.get('fiftyTwoWeekHigh', np.nan),
                '52 week low': info.get('fiftyTwoWeekLow', np.nan),
                'trailingAnnualDividendRate': info.get('trailingAnnualDividendRate', np.nan),
                'Report Currency': info.get('financialCurrency', 'N/A'),
                'Invested Capital': np.nan,
                'Total Debt': np.nan,
                'Cash': np.nan
            }

            # Get and sort financial statements
            try:
                financials = stock.financials.sort_index(axis=1, ascending=False)
                if not financials.empty:
                    latest = financials.iloc[:, 0]
                    data['EBIT'] = latest.get('EBIT', np.nan)
            except Exception as e:
                print(f"Financials error for {ticker}: {e}")

            # Get and sort balance sheet
            try:
                balance_sheet = stock.balance_sheet.sort_index(axis=1, ascending=False)
                if not balance_sheet.empty:
                    latest_bs = balance_sheet.iloc[:, 0]
                    data['Invested Capital'] = latest_bs.get('Invested Capital', np.nan)
                    data['Total Debt'] = latest_bs.get('Total Debt', np.nan)
                    data['Cash'] = latest_bs.get('Cash And Cash Equivalents', np.nan)
            except Exception as e:
                print(f"Balance sheet error for {ticker}: {e}")

            return data
        except Exception as e:
            print(f"Attempt {attempt + 1} failed for {ticker}: {e}")
            time.sleep(wait_time)
    return {'Ticker': ticker}


def update_level2_screener(sheet_name):
    """Main update function with improved calculations for the specified sheet."""
    print("Connecting...")
    app = xw.App(visible=False)
    wb = app.books.open(EXCEL_FILE_PATH)
    try:
        sheet = wb.sheets[sheet_name]
    except KeyError:
        print(f"Sheet '{sheet_name}' not found.")
        wb.close()
        app.quit()
        return

    # Clear existing data except row 1
    sheet.range('C2:R1048576').clear_contents()

    # Get tickers and process data
    tickers = sheet.range('B2').expand('down').value
    if not tickers:
        print("No tickers found.")
        wb.save()
        wb.close()
        app.quit()
        return
    tickers = [tickers] if isinstance(tickers, str) else tickers

    # Show progress while processing tickers
    total = len(tickers)
    data_list = []
    print(f"Processing {total} tickers:")
    for idx, t in enumerate(tickers, 1):
        print(f"\r  Progress: {idx}/{total} ({t})", end="")
        data = get_ticker_data(t)
        data_list.append(data)
    print("\nProcessing complete.")

    df = pd.DataFrame(data_list)

    # Currency conversions and calculations
    df['FX Rate'] = df.apply(
        lambda x: get_exchange_rate(x['Market Currency'], x['Report Currency']),
        axis=1
    )
    df['Debt USD'] = df['Total Debt'] * df['FX Rate']
    df['Cash USD'] = df['Cash'] * df['FX Rate']
    df['Enterprise Value'] = df['Market Capitalization'] + df['Debt USD'] - df['Cash USD']

    # Financial ratios
    df['Dividend Yield'] = df['trailingAnnualDividendRate'] / df['Market Price']
    df['EBIT/EV'] = (df['EBIT'] * df['FX Rate']) / df['Enterprise Value'].replace(0, np.nan)
    df['ROIC'] = df['EBIT'] / df['Invested Capital'].replace(0, np.nan)

    # Quality ranking system
    valid_mask = df[['EBIT/EV', 'ROIC']].notna().all(axis=1)
    df['Combined Rank'] = np.nan
    if valid_mask.any():
        temp = df[valid_mask].copy()
        temp['EBIT/EV Rank'] = temp['EBIT/EV'].rank(ascending=False, method='min')
        temp['ROIC Rank'] = temp['ROIC'].rank(ascending=False, method='min')
        temp['Total Rank'] = temp[['EBIT/EV Rank', 'ROIC Rank']].sum(axis=1)
        df.loc[valid_mask, 'Combined Rank'] = temp['Total Rank'].rank(method='dense')

    # Add dummy column for percent_from_low to align output columns
    df['percent_from_low'] = np.nan

    # Write to Excel
    output_cols = [
        'Company Name', 'Industry', 'Market Price', 'Market Currency',
        'Market Capitalization', '52 week high', '52 week low', 'percent_from_low',
        'Dividend Yield', 'EBIT', 'Invested Capital', 'Report Currency', 'FX Rate',
        'EBIT/EV', 'ROIC', 'Combined Rank'
    ]
    sheet.range('C2').options(index=False, header=False).value = df[output_cols].values

    # Insert formula in column J (percent_from_low)
    if len(tickers) > 0:
        last_row = 1 + len(tickers)
        j_range = f'J2:J{last_row}'
        sheet.range(j_range).formula = '=E2/I2-1'

    wb.save()
    wb.close()
    app.quit()


if __name__ == "__main__":
    VALID_SHEETS = ['hk_screener', 'cn_screener', 'us_screener']
    sheet_to_update = input("Enter the sheet to update (hk_screener, cn_screener, us_screener): ")
    if sheet_to_update in VALID_SHEETS:
        update_level2_screener(sheet_to_update)
    else:
        print("Invalid sheet name.")
