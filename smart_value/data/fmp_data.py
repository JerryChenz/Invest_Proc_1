import pandas as pd
from urllib.request import urlopen
import certifi
import json

api_key = 'c99eda5db224d34162adae341298790b'
# Free keys doesn't allow you to retrieve oversea stock data

def get_jsonparsed_data(url):
    response = urlopen(url, cafile=certifi.where())
    data = response.read().decode("utf-8")
    return json.loads(data)


url = (f"https://financialmodelingprep.com/api/v3/income-statement/AAPL?period=annual&apikey={api_key}")
print(get_jsonparsed_data(url))
