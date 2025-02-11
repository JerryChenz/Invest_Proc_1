import pathlib
import re
import shutil

# Location of the folders and documents
models_folder_path = pathlib.Path.cwd().resolve() / 'financial_models' / 'opportunities'
stock_monitor_file_path = pathlib.Path.cwd().resolve() / 'financial_models' / 'Stock_Monitor.xlsx'
macro_monitor_file_path = pathlib.Path.cwd().resolve() / 'financial_models' / 'Macro_Monitor.xlsx'
template_folder_path = pathlib.Path.cwd().resolve() / 'financial_models' / 'templates'


def get_model_paths():
    """Load the data of the models from the opportunities folder.

    return a list of paths pointing to the models
    """

    # Define the pattern used to name the models.
    stock_regex = re.compile(".*Valuation.*(?!_old)")
    negative_regex = re.compile(".*~.*")

    try:
        if pathlib.Path(models_folder_path).exists():
            path_list = [val_file_path for val_file_path in models_folder_path.iterdir()
                         if models_folder_path.is_dir() and val_file_path.is_file()]
            opportunities_path_list = list(item for item in path_list if stock_regex.match(str(item)) and
                                           not negative_regex.match(str(item)))
            if len(opportunities_path_list) == 0:
                raise FileNotFoundError("No opportunity file", "opp_file")
        else:
            raise FileNotFoundError("The opportunities folder doesn't exist", "opp_folder")
    except FileNotFoundError as err:
        if err.args[1] == "opp_folder":
            print("The opportunities folder doesn't exist")
        if err.args[1] == "opp_file":
            print("No opportunity file", "opp_file")
    else:
        return opportunities_path_list


def get_template_paths():
    """Load the data of the models from the opportunities folder.

    return a list of paths pointing to the models
    """

    # Define the pattern used to name the models.
    template_regex = re.compile(".*Valuation.*")
    negative_regex = re.compile(".*~.*")

    try:
        if pathlib.Path(template_folder_path).exists():
            path_list = [val_file_path for val_file_path in template_folder_path.iterdir()
                         if template_folder_path.is_dir() and val_file_path.is_file()]
            template_path_list = list(item for item in path_list if template_regex.match(str(item)) and
                                      not negative_regex.match(str(item)))
            if len(template_path_list) > 1 or len(template_path_list) == 0:
                raise FileNotFoundError("The template file error", "temp_file")
        else:
            raise FileNotFoundError("The stock_template folder doesn't exist", "temp_folder")
    except FileNotFoundError as err:
        if err.args[1] == "temp_folder":
            print("The stock_template folder doesn't exist")
        if err.args[1] == "temp_file":
            print("The template file error")
    else:
        return template_path_list


def new_latest_model(file_name):
    """creates a new model with the latest template at the opportunities folder, returns the new path

    :param file_name: the file name of the model
    """

    template_path_list = get_template_paths()
    # New model path
    model_path = models_folder_path / file_name
    if not pathlib.Path(model_path).exists():
        # Creates a new model file if not already exists
        print(f'Creating {file_name}...')
        shutil.copy(template_path_list[0], model_path)
    else:
        print(f'{file_name} already exists')
    return model_path
