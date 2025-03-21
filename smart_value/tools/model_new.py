import os
import shutil
from yahooquery import Ticker
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
    """Updates the model with data fetched using yahooquery."""
    print(f'Updating {model_name}...')
    tkr = Ticker(ticker)

    # Fetch data from yahooquery
    price_info = tkr.price.get(ticker, {})
    summary_profile = tkr.summary_profile.get(ticker, {})
    key_stats = tkr.key_stats.get(ticker, {})
    financial_data = tkr.financial_data.get(ticker, {})
    income_statement = tkr.income_statement(frequency='a').set_index('asOfDate').sort_index(ascending=False)

    # Extract necessary fields
    name = summary_profile.get('name', ticker)
    symbol = ticker
    price_value = price_info.get('regularMarketPrice')
    price_currency = price_info.get('currency', 'USD')
    shares_outstanding = key_stats.get('sharesOutstanding')
    report_currency = financial_data.get('financialCurrency', price_currency)

    # Calculate FX rate
    if price_currency == report_currency:
        fx_rate = 1.0
    else:
        fx_ticker = f"{price_currency}{report_currency}=X"
        fx_data = Ticker(fx_ticker).price.get(fx_ticker, {})
        fx_rate = fx_data.get('regularMarketPrice', 1.0)

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
        # Determine figure_in scaling factor
        figure_in_value = 1000  # Default to thousands
        if not income_statement.empty and 'TotalRevenue' in income_statement.columns:
            latest_revenue = income_statement['TotalRevenue'].iloc[0]
            if abs(latest_revenue) >= 1_000_000:
                figure_in_value = 1_000_000
        data_sheet.range(data_pos["figure_in"]).value = figure_in_value

        # Fetch financial data
        cash_flow = tkr.cash_flow(frequency='a').set_index('asOfDate').sort_index(ascending=False)
        balance_sheet = tkr.balance_sheet(frequency='a').set_index('asOfDate').sort_index(ascending=False)

        # Mapping from data_pos keys to financial data columns
        financial_mapping = {
            "sales": ('income_statement', 'TotalRevenue'),
            "cogs": ('income_statement', 'CostOfRevenue'),
            "opex": ('income_statement', 'OperatingExpenses'),
            "selling_expenses": ('income_statement', 'SellingGeneralAndAdministrative'),
            "research_development": ('income_statement', 'ResearchAndDevelopment'),
            "jv_result": ('income_statement', 'NetIncomeFromContinuingOperations'),
            "securities_income": ('income_statement', 'OtherNonOperatingIncomeExpenses'),
            "property_income": ('income_statement', 'OperatingIncome'),
            "interest_expense": ('income_statement', 'InterestExpense'),
            "interest_income": ('income_statement', 'InterestIncome'),
            "income_tax": ('income_statement', 'IncomeTaxExpense'),
            "net_income": ('income_statement', 'NetIncome'),
            "nc_income": ('income_statement', 'NetIncomeFromContinuingOperations'),
            "da": ('cash_flow', 'DepreciationAmortization'),
            "capex": ('cash_flow', 'CapitalExpenditure'),
            "wcinv": ('cash_flow', 'ChangeInWorkingCapital'),
            "dividend_per_share": ('cash_flow', 'DividendsPaid'),
            "Account_receivable": ('balance_sheet', 'AccountsReceivable'),
            "inventory": ('balance_sheet', 'Inventory'),
            "total_liabilities": ('balance_sheet', 'TotalLiabilities'),
            "total_equity": ('balance_sheet', 'TotalEquity'),
            "nc_interest": ('balance_sheet', 'NoncontrollingInterest'),
        }

        # Update each data field
        for key, range_ref in data_pos.items():
            if key in ['date_of_last_annual_report', 'figure_in']:
                continue

            if key not in financial_mapping:
                continue

            source, column = financial_mapping[key]
            df = income_statement if source == 'income_statement' else cash_flow if source == 'cash_flow' else balance_sheet

            if df.empty:
                continue

            try:
                data = df[column].tolist()
            except KeyError:
                continue

            # Special handling for dividend_per_share
            if key == 'dividend_per_share':
                if shares_outstanding and data:
                    data = [abs(d) / shares_outstanding for d in data]  # No figure_in scaling
                else:
                    data = []
            else:
                # Apply figure_in scaling to totals
                data = [d / figure_in_value for d in data]

            # Write to Excel
            start_cell = range_ref.split(':')[0]
            if data:
                data_to_write = data[:10]  # Max 10 years
                data_sheet.range(start_cell).value = data_to_write

        model_xl.save()
        model_xl.close()

    print(f'{model_name} update completed')
