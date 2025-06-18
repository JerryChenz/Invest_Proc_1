import os
import pandas as pd
from smart_value.data.monitor_data import opportunities_headers
from smart_value.tools.find_docs import get_monitor_path


def generate_monitor_md():
    """Generate a Markdown file from the Opportunities sheets of Stock_Monitor_INT.xlsx and Stock_Monitor_CN.xlsx."""

    # Define paths for the Excel files
    int_excel_path = get_monitor_path("INT")
    cn_excel_path = get_monitor_path("CN")

    # Get the directory containing the Excel files
    directory = os.path.dirname(int_excel_path)
    print(f"Output directory: {directory}")

    # Read data from both Excel files
    df_int = read_opportunities_sheet(int_excel_path)
    print("International DataFrame:")
    print(df_int.to_string())
    df_cn = read_opportunities_sheet(cn_excel_path)
    print("China DataFrame:")
    print(df_cn.to_string())

    # Generate Markdown content
    md_content = "# Stock Opportunities\n\n"

    # Add International section if data exists
    if not df_int.empty:
        md_content += "## International\n\n"
        md_content += df_int.to_markdown(index=False) + "\n\n"

    # Add China section if data exists
    if not df_cn.empty:
        md_content += "## China\n\n"
        md_content += df_cn.to_markdown(index=False) + "\n\n"

    # Define the output path and save the Markdown file
    output_path = os.path.join(directory, "Opportunities.md")
    with open(output_path, 'w', encoding='utf-8') as md_file:
        md_file.write(md_content)

    print(f"Markdown file saved to: {output_path}")
    return output_path


def read_opportunities_sheet(file_path):
    """Reads the Opportunities sheet from the given Excel file and returns a processed DataFrame."""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return pd.DataFrame()
    try:
        # Number of columns to read (26, from B to AA)
        num_cols = len(opportunities_headers)
        # Read columns 1 to 26 (B to AA in Excel, since A is 0)
        df = pd.read_excel(
            file_path,
            sheet_name='Opportunities',
            usecols=range(1, num_cols + 1),  # Indices 1 to 26
            skiprows=2,
            header=None,
            engine='openpyxl'
        )
        # Assign the 26 column names
        df.columns = list(opportunities_headers.keys())
        # Remove rows where all elements are NaN
        df.dropna(how='all', inplace=True)
        return df
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return pd.DataFrame()
