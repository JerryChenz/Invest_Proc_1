# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.


def notion_price():
    import yfinance as yf
    from notion.client import NotionClient
    from datetime import datetime

    client = NotionClient(token_v2="514b02c7f5ac3c25e23915fb3e5e7a468ae3d881c2eeaa03bd1d87e788b062cfb5fb2ad0933a10e144095a551c2e1001eae35a90e1e01e8c8db4606f7b7a92c96e6a4b1b8572bf4b6a0bd60dbc4d")

    cv = client.get_collection_view("https://www.notion.so/Valuation-Project-8075400fc5614af0a5ed7a94fa8e984e")

    print("The title is:", page.title)

    tickers = ['AAPL', 'MSFT', 'VWRL.AS', 'CHF=X', 'AMZN', 'INTC']
    for ticker in tickers:
        price = yf.Ticker(ticker)
        row = cv.collection.add_row()

        hist = price.history(period="1d")
        row.Stock = ticker
        row.Date = datetime.today().strftime('%Y-%m-%d')
        row.Close = float(round((hist.Close[0]), 1))
        row.Open = float(round((hist.Open[0]), 1))
        row.Open = float(round((hist.Open[0]), 1))
        row.Volume = float(round((hist.Volume[0]), 1))
        row.High = float(round((hist.High[0]), 1))
        row.DayReturn = float(round(((hist.Close[0]) - (hist.Open[0])) / (hist.Open[0]) * 100, 2))

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    notion_price()


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
