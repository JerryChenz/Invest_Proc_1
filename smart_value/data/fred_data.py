from fredapi import Fred


fred_api_key = '25dcdb108d7d62628268b97f9df6b593'


def get_riskfree_rate(country):
    """Return the 10-year government bond yield
    :param country: us or cn
    :return: 10-year government bond yield"""

    fred = Fred(api_key=fred_api_key)

    # output rate not in percentage
    if country == 'cn':
        return fred.get_series('INTDSRCNM193N').iloc[-1]/100  # China Discount Rate
    else:
        return fred.get_series('DGS10').iloc[-1]/100  # US 10 Year Treasury Yield


def get_us_bbb_yield():
    """Return the ICE BofA BBB US Corporate Index Effective Yield"""

    fred = Fred(api_key=fred_api_key)

    # output rate not in percentage
    return fred.get_series('BAMLC0A4CBBBEY').iloc[-1]/100


def inflation(country):
    """Return the 10-Year Breakeven Inflation Rate"""

    fred = Fred(api_key=fred_api_key)

    # output rate not in percentage
    if country == 'us':
        return fred.get_series('T10YIE').iloc[-1]/100
    else:
        pass  # Manual input is better for other countries
