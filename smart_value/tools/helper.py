import xlwings
from smart_value.tools.find_docs import get_model_paths


def copy_value():
    """Update the models in the opportunities folder with the latest template."""

    opportunities_path_list = get_model_paths()

    for p in opportunities_path_list:
        print(f"Updating {p.name}")
        with xlwings.App(visible=False) as app:
            xl_model = app.books.open(p)
            input_sheet = xl_model.sheets('Inputs')
            # Case 1
            input_sheet.range("C30:M33").copy()
            input_sheet.range("C31:M34").paste(paste="formulas")
            input_sheet.range("C30:M30").clear_contents()
            # Case 2
            # fin_sheet = xl_model.sheets('Fin_Analysis')
            # input_sheet.range("C41").value = fin_sheet.range("D3").value
            # input_sheet.range("C42").value = fin_sheet.range("D4").value
            # input_sheet.range("C37").value = fin_sheet.range("I49").value
            xl_model.save(p)
            xl_model.close()
