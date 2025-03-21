from fredapi import Fred

fred_api_key = '25dcdb108d7d62628268b97f9df6b593'


def get_riskfree_rate(country):
    """Return the 10-year government bond yield
    :param country: us or cn
    :return: 10-year government bond yield"""

    fred = Fred(api_key=fred_api_key)

    try:
        # output rate not in percentage
        if country == 'cn':
            return fred.get_series('INTDSRCNM193N').iloc[-1] / 100  # China Discount Rate
        else:
            return fred.get_series('DGS10').iloc[-1] / 100  # US 10 Year Treasury Yield
    except Exception as e:
        print(f"Error fetching {country} risk-free rate: {e}")
        return None


def get_us_prime_rate():
    """Return the US Bank Prime Loan Rate"""

    fred = Fred(api_key=fred_api_key)

    try:
        # DPRIME: Bank Prime Loan Rate
        return fred.get_series('DPRIME').iloc[-1] / 100
    except Exception as e:
        print(f"Error fetching US prime rate: {e}")
        return None
