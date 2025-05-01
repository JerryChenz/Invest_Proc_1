import os
import shutil
import yfinance as yf
import xlwings as xw
from smart_value.tools.find_docs import get_template_paths, models_folder
from smart_value.data.model_data import thesis_pos, data_pos

def new_stock_model(ticker, comp_group=None):
    """Creates a new model if it doesn't already exist, then updates it."""
    template_path_list = get_template_paths()
    template_basename = os.path.basename(template_path_list[0])
    model_basename = template_basename.replace("_Template", "")
    model_name = f"{ticker}_{model_basename}"

    # Ensure models folder exists
    os.makedirs(models_folder, exist_ok=True)
    model_path = os.path.join(models_folder, model_name)

    if not os.path.exists(model_path):
        shutil.copy(template_path_list[0], model_path)
        print(f"Created new model: {model_name}")
    else:
        print(f"Using existing model: {model_name}")

    update_new_model(ticker, model_name, model_path, comp_group)

def update_new_model(ticker, model_name, model_path, comp_group=None):
    """Updates the model with data fetched using yfinance."""
    print(f'Updating {model_name}...')
    tkr = yf.Ticker(ticker)

    # Fetch data from yfinance
    info = tkr.info
    financials = tkr.financials
    cashflow = tkr.cashflow
    balance_sheet = tkr.balance_sheet

    # Extract necessary fields
    name = info.get('longName', ticker)
    symbol = ticker
    price_value = info.get('regularMarketPrice')
    price_currency = info.get('currency', 'USD')
    shares_outstanding = info.get('sharesOutstanding')
    report_currency = info.get('currency', 'USD')  # Assuming same as price currency

    # Calculate FX rate
    if price_currency == report_currency:
        fx_rate = 1.0
    else:
        fx_ticker = f"{report_currency}{price_currency}=X"
        fx_tkr = yf.Ticker(fx_ticker)
        fx_rate = fx_tkr.info.get('regularMarketPrice', 1.0)

    with xw.App(visible=False) as app:
        model_xl = app.books.open(model_path)
        thesis_sheet = model_xl.sheets('Thesis')
        data_sheet = model_xl.sheets('Data')

        # Update Thesis Sheet
        if comp_group:
            thesis_sheet.range(thesis_pos["comp_group"]).value = comp_group
        thesis_sheet.range(thesis_pos["name"]).value = name
        thesis_sheet.range(thesis_pos["symbol"]).value = symbol
        thesis_sheet.range(thesis_pos["price"]).value = price_value
        thesis_sheet.range(thesis_pos["price_currency"]).value = price_currency
        thesis_sheet.range(thesis_pos["shares_outstanding"]).value = shares_outstanding
        thesis_sheet.range(thesis_pos["report_currency"]).value = report_currency
        thesis_sheet.range(thesis_pos["fx_rate"]).value = fx_rate

        # Update Data Sheet
        # Determine scaling factor
        scaling_factor_value = 1000  # Default to thousands
        if not financials.empty and 'Total Revenue' in financials.index:
            latest_revenue = financials.loc['Total Revenue'].iloc[0]
            if abs(latest_revenue) >= 1_000_000:
                scaling_factor_value = 1_000_000
        data_sheet.range(data_pos["scaling_factor"]).value = scaling_factor_value

        # Mapping from data_pos keys to financial data columns
        financial_mapping = {
            "sales": ('financials', 'Total Revenue'),
            "cogs": ('financials', 'Cost Of Revenue'),
            "opex": ('financials', 'Total Operating Expenses'),
            "selling_expenses": ('financials', 'Selling General Administrative'),
            "research_development": ('financials', 'Research Development'),
            "jv_result": ('financials', 'Net Income From Continuing Ops'),
            "securities_income": ('financials', 'Other Income'),
            "property_income": ('financials', 'Operating Income'),
            "interest_expense": ('financials', 'Interest Expense'),
            "interest_income": ('financials', 'Interest Income'),
            "income_tax": ('financials', 'Income Tax Expense'),
            "net_income": ('financials', 'Net Income'),
            "nc_income": ('financials', 'Net Income From Continuing Ops'),
            "da": ('cashflow', 'Depreciation'),
            "capex": ('cashflow', 'Capital Expenditures'),
            "wcinv": ('cashflow', 'Change In Working Capital'),
            "dividend_per_share": ('cashflow', 'Dividends Paid'),
            "Account_receivable": ('balance_sheet', 'Net Receivables'),
            "inventory": ('balance_sheet', 'Inventory'),
            "total_liabilities": ('balance_sheet', 'Total Liab'),
            "total_equity": ('balance_sheet', 'Total Stockholder Equity'),
            "nc_interest": ('balance_sheet', 'Minority Interest'),
        }

        # Update each data field
        for key, range_ref in data_pos.items():
            if key in ['date_of_last_annual_report', 'scaling_factor']:
                continue

            if key not in financial_mapping:
                continue

            source, column = financial_mapping[key]
            if source == 'financials':
                df = financials
            elif source == 'cashflow':
                df = cashflow
            elif source == 'balance_sheet':
                df = balance_sheet
            else:
                continue

            if df.empty or column not in df.index:
                continue

            data = df.loc[column].values.tolist()

            # Special handling for dividend_per_share
            if key == 'dividend_per_share':
                if shares_outstanding and data:
                    data = [abs(d) / shares_outstanding for d in data]  # No scaling factor
                else:
                    data = []
            else:
                # Apply scaling factor to totals
                data = [d / scaling_factor_value for d in data]

            # Write to Excel
            start_cell = range_ref.split(':')[0]
            if data:
                data_to_write = data[:10]  # Max 10 years
                data_sheet.range(start_cell).value = data_to_write

        model_xl.save()
        model_xl.close()

    print(f'{model_name} update completed')
