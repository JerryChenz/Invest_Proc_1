import os
from datetime import date
import xlwings

from smart_value.tools import model_dash
from smart_value.tools.find_docs import get_template_paths, new_latest_model
from smart_value.tools.model_dash import thesis_pos
from smart_value.data import yq_data as yq


def new_stock_model(ticker, comp_group):
    """Creates a new model if it doesn't already exist, then update.

    :param ticker: the string ticker of the stock
    :param comp_group: the string identifier of the stock comparable group ID
    """

    template_path_list = get_template_paths()

    # New model path
    model_name = ticker + "_" + os.path.basename(template_path_list[0])
    model_path = new_latest_model(model_name)
    # update the model
    update_new_model(ticker, comp_group, model_name, model_path)


def update_new_model(ticker, comp_group, model_name, model_path):
    """Update the model.

    :param ticker: the string ticker of the stock
    :param comp_group: the string identifier of the stock comparable group ID
    :param model_name: the model file name
    :param model_path: the model file path
    """
    # update the new model
    print(f'Updating {model_name}...')
    company = yq.YqStock(ticker)

    with xlwings.App(visible=False) as app:
        model_xl = app.books.open(model_path)
        new_inputs(model_xl.sheets('Inputs'), company, comp_group)
        new_dash(model_xl.sheets('Dashboard'), company)
        model_xl.save(model_path)
        model_xl.close()
    print(f'{model_name} update completed')


def new_inputs(input_sheet, company, comp_group):
    """Get the new inputs

    :param input_sheet: the Excel file of the model
    :param company: the YqStock object of the stock
    :param comp_group: the string identifier of the stock comparable group ID
    """

    data_digits = len(str(int(company.is_df.iloc[0, 0])))
    # print(str(int(stock.is_df.iloc[0, 0])))
    # print(data_digits)
    if 13 > data_digits >= 7:
        report_unit = 1000
    elif data_digits >= 13:
        report_unit = 1000000
    else:
        report_unit = 1

    input_sheet.range('C4').value = company.symbol
    input_sheet.range('C5').value = company.name
    input_sheet.range('C6').value = date.today()
    input_sheet.range('C9').value = comp_group
    input_sheet.range('C10').value = company.shares  # Yahoo data on shares often is wrong
    input_sheet.range('C11').value = company.report_currency
    input_sheet.range('C12').value = company.last_fy
    input_sheet.range('C13').value = report_unit
    input_sheet.range('C44').value = company.last_dividend

    # print(company.is_df)
    for i in range(len(company.is_df.columns)):
        # income statement
        input_sheet.range((25, i + 3)).value = int(company.is_df.iloc[0, i] / report_unit)  # Sales
        input_sheet.range((26, i + 3)).value = int(company.is_df.iloc[1, i] / report_unit)  # COGS
        input_sheet.range((27, i + 3)).value = int(company.is_df.iloc[2, i] / report_unit)  # Operating Expenses

    for j in range(len(company.annual_bs.columns)):
        # Total Liabilities = Total Asset - TotalEquityAndMinorityInterest
        input_sheet.range((37, j + 3)).value = (int(company.annual_bs.iloc[0, j] / report_unit)  # TotalAssets
                                                - int(company.annual_bs.iloc[7, j] / report_unit))  # TotalEquity
        # TotalEquityAndMinorityInterest
        input_sheet.range((41, j + 3)).value = int(company.annual_bs.iloc[7, j] / report_unit)
        # Non-common Interest = TotalEquityAndMinorityInterest - CommonStockEquity
        input_sheet.range((42, j + 3)).value = (int(company.annual_bs.iloc[7, j] / report_unit)
                                                - int(company.annual_bs.iloc[8, j] / report_unit))  # CommonStockEquity


def new_dash(dash_sheet, company):
    """Update the Data sheet.

    :param dash_sheet: the xlwings object of Data
    :param company: the Stock object
    """

    dash_sheet.range('G3').value = company.price[0]
    dash_sheet.range('H3').value = company.price_currency
    dash_sheet.range('G7').value = company.fx_rate
    model_dash.update_dash_marco(dash_sheet)
