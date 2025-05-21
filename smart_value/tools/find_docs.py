"""
find_docs.py - File Path Management for Valuation Models

Purpose:
Manages model and template file paths with strict naming convention enforcement:
- Models: <ticker>_Valuation.xlsx (ticker ≤ 10 chars, no underscores)
- Templates: Valuation_vX.Y.xlsx (semantic versioning)
Ensures clean separation of working files from backups and temp files.

Key Features:
1. Model Validation: Regex checks for version patterns
2. Atomic Operations: Safe file creation with existence checks
3. Version Sorting: Semantic version comparison for templates
4. Temp File Filtering: Automatic exclusion of backup/autosave files
"""

import pathlib
import re
import shutil

# Configure base paths
project_root = pathlib.Path.cwd().resolve()
# the cwd() above is the output assumed from running the invest_proc main.
models_folder = project_root / 'financial_models' / 'opportunities'
templates_folder = project_root / 'financial_models' / 'templates'
macro_monitor_file_path = project_root / 'financial_models' / 'Macro_Monitor.xlsx'

# Validation patterns
MODEL_PATTERN = re.compile(
    r'^[^_]{1,10}_Valuation\.xlsx?$',  # Ticker (1-10 chars, no underscores) + _Valuation
    re.IGNORECASE
)
TEMP_PATTERN = re.compile(r'(_old|~|\.tmp)$', re.IGNORECASE)  # Exclude backups/autosaves
VERSION_PATTERN = re.compile(
    r'^Valuation_v(\d+\.\d+(?:\.\d+)*)\.xlsx?$',  # Semantic version extraction
    re.IGNORECASE
)


def get_model_paths():
    """Get validated model paths matching naming convention."""
    if not models_folder.exists():
        raise FileNotFoundError(f"Models directory not found: {models_folder}")

    return [
        f for f in models_folder.iterdir()
        if f.is_file()
           and MODEL_PATTERN.match(f.name)
           and not TEMP_PATTERN.search(f.name)
    ]


def get_template_paths():
    """Get templates sorted by semantic version (newest first)."""
    if not templates_folder.exists():
        raise FileNotFoundError(f"Templates directory not found: {templates_folder}")

    templates = []
    for f in templates_folder.iterdir():
        if match := VERSION_PATTERN.match(f.name):
            version = tuple(map(int, match.group(1).split('.')))
            templates.append((version, f))

    return [t[1] for t in sorted(templates, reverse=True)]


def get_monitor_path(portfolio_code):
    """Return the monitor file path based on the portfolio code."""
    return project_root / 'financial_models' / f'Stock_Monitor_{portfolio_code}.xlsx'


def new_latest_model(ticker):
    """Create new model from template with validation."""

    # Generate filename
    model_name = f"{ticker}_Valuation.xlsx"
    model_path = models_folder / model_name

    if model_path.exists():
        raise FileExistsError(f"Model already exists: {model_name}")

    # Copy latest template
    templates = get_template_paths()
    if not templates:
        raise FileNotFoundError("No valid templates available")

    shutil.copy(templates[0], model_path)
    return model_path


def col_to_num(col):
    """Convert Excel column letter to its corresponding number (e.g., 'A' -> 1, 'AA' -> 27)."""
    num = 0
    for c in col:
        num = num * 26 + (ord(c.upper()) - ord('A') + 1)
    return num
