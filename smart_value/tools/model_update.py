import pathlib
from pathlib import Path
import xlwings
from openpyxl.reader.excel import load_workbook
from smart_value.data.forex_data import get_forex_dict
from smart_value.data.yq_data import get_quotes
from smart_value.tools import model_dash
from smart_value.tools.find_docs import get_model_paths, new_latest_model
from smart_value.tools.model_dash import thesis_pos

input_dict = {
    "info": "C4:D22",
    "income_statement": "C25:M33",
    "balance_sheet": "C34:M43",
    "dividend": "C44:M44",
    "Others": "C48:E87",
    "Valuation": "E91:F98"
}


def update_models(quick=False):
    """Update the models in the opportunities folder with the latest template

    :param quick: update the price and forex if False
    """

    opportunities_path_list = get_model_paths()

    # get stock prices and forex rates
    forex_dict = {}
    price_dict = {}
    if quick is False:
        forex_dict = get_forex_dict()
        price_dict = get_price_dict(opportunities_path_list)

    for p in opportunities_path_list:
        # Step 1: renames the existing model to mark as old
        print(f"Updating {p.name}")
        marked_path = p.rename(Path(p.parent, p.stem + "_old" + p.suffix))
        # Step 2: creates a new model with the latest template
        updated_path = new_latest_model(p.name)
        # Step 3: copy the inputs from the marked path and paste to the updated model with inputs
        copy_inputs(marked_path, updated_path, quick, forex_dict, price_dict)
        # Step 4: delete the marked model
        pathlib.Path.unlink(marked_path)


def copy_inputs(old_path, new_path, quick, forex_dict, price_dict):
    """reads the inputs of the model at marked_path, returns the inputs in a dictionary

    :param old_path: the file path of the marked model
    :param new_path: the file path of the new model
    :param quick: update the price and forex if False
    :param forex_dict: forex dictionary contains the updated forex rates
    :param price_dict: price dictionary contains the updated stock prices
    """

    with xlwings.App(visible=False) as app:
        xl_old_model = app.books.open(old_path)
        xl_new_model = app.books.open(new_path)
        old_input_sheet = xl_old_model.sheets('Inputs')
        new_input_sheet = xl_new_model.sheets('Inputs')
        for inputs in input_dict:
            old_input_sheet.range(input_dict[inputs]).copy()
            new_input_sheet.range(input_dict[inputs]).paste(paste="formulas")
        xl_old_model.close()
        if quick is False:
            dash_sheet = xl_new_model.sheets('Dashboard')
            model_dash.update_dash_marco(dash_sheet)
            model_dash.update_dash_market(dash_sheet, forex_dict, price_dict)
        xl_new_model.save(new_path)
        xl_new_model.close()


def get_price_dict(opportunities_path_list):

    ticker_list = []

    for p in opportunities_path_list:
        opp_wb = load_workbook(p, read_only=True, data_only=True)
        dash_sheet = opp_wb["Dashboard"]
        ticker_list.append(dash_sheet[thesis_pos["symbol"]].value)
        opp_wb.close()
    return get_quotes(ticker_list)
