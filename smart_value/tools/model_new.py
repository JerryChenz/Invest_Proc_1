import os
import shutil
from yahooquery import Ticker
import xlwings as xw
from smart_value.tools.find_docs import get_template_paths
from smart_value.data.model_data import thesis_pos, data_pos


def new_stock_model(ticker, comp_group):
    """Creates a new model if it doesn't already exist, then updates it."""
    template_path_list = get_template_paths()
    template_basename = os.path.basename(template_path_list[0])
    model_basename = template_basename.replace("_Template", "")
    model_name = f"{ticker}_{model_basename}"
    models_dir = os.path.dirname(template_path_list[0])
    model_path = os.path.join(models_dir, model_name)

    if not os.path.exists(model_path):
        shutil.copy(template_path_list[0], model_path)
        print(f"Created new model: {model_name}")
    else:
        print(f"Using existing model: {model_name}")

    update_new_model(ticker, comp_group, model_name, model_path)


def update_new_model(ticker, comp_group, model_name, model_path):
    """Updates the model with data fetched using yahooquery."""
    print(f'Updating {model_name}...')
    tkr = Ticker(ticker)

    # Fetch data from yahooquery
    price_info = tkr.price.get(ticker, {})
    summary_profile = tkr.summary_profile.get(ticker, {})
    key_stats = tkr.key_stats.get(ticker, {})
    financial_data = tkr.financial_data.get(ticker, {})

    # Extract necessary fields for Thesis sheet
    name = summary_profile.get('name', ticker)
    symbol = ticker
    price_value = price_info.get('regularMarketPrice')
    price_currency = price_info.get('currency', 'USD')
    shares_outstanding = key_stats.get('sharesOutstanding')
    report_currency = financial_data.get('financialCurrency', price_currency)

    # Calculate FX rate between price currency and report currency
    if price_currency == report_currency:
        fx_rate = 1.0
    else:
        fx_ticker = f"{price_currency}{report_currency}=X"
        fx_data = Ticker(fx_ticker).price.get(fx_ticker, {})
        fx_rate = fx_data.get('regularMarketPrice', 1.0)

    # Update the Excel model
    with xw.App(visible=False) as app:
        model_xl = app.books.open(model_path)
        thesis_sheet = model_xl.sheets('Thesis')
        data_sheet = model_xl.sheets('Data')

        # Update Thesis Sheet
        thesis_sheet.range(thesis_pos["comp_group"]).value = comp_group
        thesis_sheet.range(thesis_pos["name"]).value = name
        thesis_sheet.range(thesis_pos["symbol"]).value = symbol
        thesis_sheet.range(thesis_pos["price"]).value = price_value
        thesis_sheet.range(thesis_pos["price_currency"]).value = price_currency
        thesis_sheet.range(thesis_pos["shares_outstanding"]).value = shares_outstanding
        thesis_sheet.range(thesis_pos["report_currency"]).value = report_currency
        thesis_sheet.range(thesis_pos["fx_rate"]).value = fx_rate

        # Update Data Sheet
        # Fetch annual financial data sorted by latest year first
        income_statement = tkr.income_statement(frequency='a').set_index('asOfDate').sort_index(ascending=False)
        cash_flow = tkr.cash_flow(frequency='a').set_index('asOfDate').sort_index(ascending=False)
        balance_sheet = tkr.balance_sheet(frequency='a').set_index('asOfDate').sort_index(ascending=False)

        # Set date of last annual report and figure_in (currency)
        date_last_annual = income_statement.index[0].strftime('%Y-%m-%d') if not income_statement.empty else "N/A"
        data_sheet.range(data_pos["date_of_last_annual_report"]).value = date_last_annual
        data_sheet.range(data_pos["figure_in"]).value = report_currency

        # Mapping from data_pos keys to financial data columns
        financial_mapping = {
            # Income Statement
            "sales": ('income_statement', 'Total Revenue'),
            "cogs": ('income_statement', 'Cost of Revenue'),
            "opex": ('income_statement', 'Operating Expenses'),
            "selling_expenses": ('income_statement', 'Selling General and Administrative'),
            "research_development": ('income_statement', 'Research and Development'),
            "jv_result": ('income_statement', 'Net Income From Continuing Operations'),
            "securities_income": ('income_statement', 'Other Non Operating Income Expenses'),
            "property_income": ('income_statement', 'Operating Income'),
            "interest_expense": ('income_statement', 'Interest Expense'),
            "interest_income": ('income_statement', 'Interest Income'),
            "income_tax": ('income_statement', 'Income Tax Expense'),
            "net_income": ('income_statement', 'Net Income'),
            "nc_income": ('income_statement', 'Net Income From Continuing Operations'),
            # Cash Flow Statement
            "da": ('cash_flow', 'Depreciation Amortization'),
            "capex": ('cash_flow', 'Capital Expenditure'),
            "wcinv": ('cash_flow', 'Change In Working Capital'),
            "dividend_per_share": ('cash_flow', 'Dividends Paid'),  # Adjusted per share below
            # Balance Sheet
            "Account_receivable": ('balance_sheet', 'Accounts Receivable'),
            "inventory": ('balance_sheet', 'Inventory'),
            "total_liabilities": ('balance_sheet', 'Total Liabilities'),
            "total_equity": ('balance_sheet', 'Total Equity'),
            "nc_interest": ('balance_sheet', 'Noncontrolling Interest'),
        }

        # Update each data field in the Data sheet
        for key, range_ref in data_pos.items():
            if key in ['date_of_last_annual_report', 'figure_in']:
                continue  # Already handled

            if key not in financial_mapping:
                print(f"Warning: {key} not mapped to financial data.")
                continue

            source, column = financial_mapping[key]
            df = None
            if source == 'income_statement':
                df = income_statement
            elif source == 'cash_flow':
                df = cash_flow
            elif source == 'balance_sheet':
                df = balance_sheet

            if df is None or df.empty:
                print(f"No data found for {key}.")
                continue

            try:
                data = df[column].tolist()
            except KeyError:
                print(f"Column '{column}' not found in {source} for {key}.")
                continue

            # Handle dividend_per_share (convert to per-share value)
            if key == 'dividend_per_share':
                if shares_outstanding and data:
                    data = [abs(d) / shares_outstanding for d in data]  # Dividends Paid is negative
                else:
                    data = []

            # Get the start cell (e.g., "C4" from "C4:M4")
            start_cell = range_ref.split(':')[0]

            # Write data to Excel (limited to available years)
            if data:
                data_to_write = data[:10]  # Max 10 columns (C-M)
                data_sheet.range(start_cell).value = data_to_write

        model_xl.save()
        model_xl.close()

    print(f'{model_name} update completed')
