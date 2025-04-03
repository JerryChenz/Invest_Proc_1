# Invest_Proc_v4 - Portfolio Management & Valuation Automation Suite

**Brief Description:** This Python project automates key aspects of the investment workflow, integrating individual stock valuation models with a rule-based portfolio management plan, primarily interacting with Excel spreadsheets.

---

## Situation

The investment process relies on a detailed **Portfolio Management Plan** and individual **Excel-based Valuation Models** for each potential stock investment. The core workflow involves:

1.  Maintaining numerous individual Valuation Model spreadsheets, each containing detailed financial analysis, assumptions, and calculated outputs like `Market Annual Return`.
2.  Manually extracting key data points from these individual models.
3.  Consolidating this data into a central monitoring spreadsheet.
4.  Applying a complex set of rules defined in the Portfolio Management Plan (including benchmark comparisons, diversification limits, risk appetite scores, and allocation logic) to determine portfolio weights.
5.  Periodically updating market data (stock prices, FX rates, interest rates) across all models.
6.  Occasionally updating the structure/template of the Valuation Model spreadsheets themselves across all existing files.

## Complication

This heavily Excel-based manual process presented several significant challenges:

1.  **Time-Consuming & Tedious:** Manually opening, extracting data from, and updating dozens or hundreds of individual Excel files was extremely time-intensive.
2.  **Error-Prone:** Manual data transfer (copy-pasting) and complex formula implementation in Excel for the allocation logic were highly susceptible to human error, potentially leading to incorrect portfolio decisions.
3.  **Inconsistent Data:** Ensuring timely updates of market data and consistent application of shared assumptions (like Base Cost of Equity) across all models was difficult to manage manually.
4.  **Difficult Maintenance:** Updating the underlying Excel template for all existing valuation models was a laborious and risky task, often deferred due to complexity.
5.  **Scalability Issues:** The manual approach limited the number of investments that could be effectively tracked and analyzed within the available time.
6.  **Operational Risk:** The reliance on manual steps introduced significant operational risk.

## Resolution: The Python Automation Suite

This Python project was developed to automate and streamline the investment workflow, addressing the complications of the manual process. It acts as an intelligent layer interacting with the existing Excel files.

**Key Features:**

*   **Automated Data Extraction & Aggregation (`stock_monitor.py`):**
    *   Automatically scans for and reads relevant data (Market Annual Return, Growth Classification, Selected Flag, etc.) directly from designated cells within each individual Valuation Model Excel file.
    *   Consolidates this information efficiently into the central 'Opportunities' sheet of the monitoring workbook.

*   **Rule-Based Portfolio Allocation Engine (`stock_monitor.py`):**
    *   Programmatically implements the multi-step allocation logic defined in the Portfolio Management Plan:
        *   Filters investments based on eligibility criteria (Selected Flag, ERB > 0).
        *   Enforces diversification rules (Max Holdings, Growth Classification Caps).
        *   Calculates Excess Returns (ERB, ERC).
        *   Applies the `Δweight_i` adjustment based on Target Annual Return.
        *   Calculates final `allocation_weight_i` respecting the Single Investment Cap.
        *   Distributes investable capital sequentially based on ranked ERB, handling partial allocations.
    *   Calculates and outputs the final `Projected Cash %` and `Projected Portfolio Return` to the 'Portfolio_Mgmt' sheet.

*   **Automated Market Data Integration (`stock_monitor.py`):**
    *   Optionally fetches current market data (stock prices, forex rates, benchmark interest rates) from external sources (`yfinance`, FRED, internal data handlers).
    *   Updates this data both in the central monitoring file and directly within the individual Valuation Model files.
    *   Propagates shared assumptions (Cost of Equity, Target Return, Holding Period) from the central plan to individual models, ensuring consistency.

*   **Automated Model Template Migration (`model_update.py`):**
    *   Provides a robust mechanism to update all existing Valuation Model Excel files to a new template version.
    *   Carefully preserves user-entered data and specific formulas from predefined locations (`user_data_pos`) during the migration, minimizing data loss and manual rework.

*   **User-Friendly Interface (`control_ui.py`):**
    *   Offers a simple Graphical User Interface (GUI) built with Tkinter.
    *   Allows users to easily trigger key automation tasks (Monitor Updates, Model Template Updates) with button clicks.
    *   Includes functionality to create new blank Valuation Model files based on the template.

**Overall Benefits:** This automation significantly increases **efficiency**, reduces **manual errors**, ensures **data consistency**, improves **scalability**, and lowers **operational risk** in the portfolio management process.

---

## Usage

1.  Ensure all dependencies are installed (e.g., `xlwings`, `pandas`, etc.).
2.  Configure necessary file paths (e.g., `stock_monitor_file_path`, model locations).
3.  Run the main user interface:
    ```bash
    python control_ui.py
    ```
4.  Use the GUI buttons to:
    *   **Update Model:** Run the template migration script (`model_update.py`).
    *   **Full Monitor Update:** Run the monitor script (`stock_monitor.py`) including market data updates.
    *   **Simple Monitor Update:** Run the monitor script (`stock_monitor.py`) skipping market data updates (faster).
    *   **Create Model:** Generate a new valuation model file for a specified stock symbol.

---