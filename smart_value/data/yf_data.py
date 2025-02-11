from yfinance import Ticker, download
import datetime as dt
import time

'''
Available yfinance features:
attrs = [
    'info', 'financials', 'quarterly_financials', 'major_holders',
    'institutional_holders', 'balance_sheet', 'quarterly_balance_sheet',
    'cashflow', 'quarterly_cashflow', 'earnings', 'quarterly_earnings',
    'sustainability', 'recommendations', 'calendar'
]
'''


def get_quote(symbol, option):
    """ Get the updated quote from yfinance fast_info

    :param symbol: string stock symbol
    :param option: fast_info argument
    Below available
    'currency', 'dayHigh', 'dayLow', 'exchange', 'fiftyDayAverage', 'lastPrice', 'lastVolume',
    'marketCap', 'open', 'previousClose', 'quoteType', 'regularMarketPreviousClose', 'shares', 'tenDayAverageVolume',
    'threeMonthAverageVolume', 'timezone', 'twoHundredDayAverage', 'yearChange', 'yearHigh', 'yearLow'
    :return: quote given option
    """

    result = None

    tries = 2
    for i in range(tries):
        try:
            company = Ticker(symbol).fast_info
            result = company[option]
        except:  # random API error
            if i < tries - 1:  # i is zero indexed
                wait = 60
                print(f"Possible API error, wait {wait} seconds before retry...")
                time.sleep(wait)
                continue
            else:
                return result
        else:
            return result


def get_forex(report_symbol, price_symbol):
    """ Return the forex quote
    Known bug: If there is no quote available, the fxRate will be 0.

    :param report_symbol: String forex report symbol
    :param price_symbol: String forex price symbol
    :return: Float average of last 3 day's forex quote
    """

    start_date = dt.datetime.today() - dt.timedelta(days=7)
    end_date = dt.datetime.today()
    # print(report_symbol + " " + price_symbol)
    if report_symbol == price_symbol:
        return 1
    elif report_symbol == "MOP" and price_symbol == "HKD":
        # Known missing quote on yahoo finance
        return 0.98
    else:
        forex_code = f"{report_symbol}{price_symbol}=X"
        # print(forex_code)
        # return the average of the last 3 forex quote
        return float(download(forex_code, start_date, end_date).tail(3)['Adj Close'].mean().item())
