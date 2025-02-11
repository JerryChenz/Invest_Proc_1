from yahooquery import Ticker
import time
import pandas as pd
from smart_value.data.yf_data import get_forex


def get_quotes(ticker_list):
    """ Get the updated stock info from yahooquery

    :param ticker_list: list of stock symbols
    :return: a dictionary containing stock data in the last
    """

    stock_dict = {}

    print(f"obtaining the prices for {len(ticker_list)} stocks...")
    tries = 2
    for i in range(tries):
        try:
            all_symbols = " ".join(ticker_list)
            stock_info = Ticker(all_symbols)
            stock_dict = stock_info.price
        except:  # random API error
            if i < tries - 1:  # i is zero indexed
                wait = 60
                print(f"Possible API error, wait {wait} seconds before retry...")
                time.sleep(wait)
                continue
            else:
                return stock_dict
        else:
            return stock_dict


def get_price(ticker, stock_dict):
    """ Get the updated stock info from yahooquery

    :param ticker: string stock symbol
    :param stock_dict: a dictionary containing stock data in the last
    :return: the stock price of this symbol
    """

    return stock_dict[ticker]['regularMarketPrice'], stock_dict[ticker]['currency']


class YqStock:
    """Retrieves the data from yahooquery"""

    def __init__(self, symbol):
        """
        :param symbol: string ticker of the stock
        """

        self.symbol = symbol
        self.name = None
        self.fx_rate = None
        self.price = None
        self.price_currency = None
        self.report_currency = None
        self.shares = None
        self.last_dividend = None
        self.is_df = None
        self.annual_bs = None
        self.quarter_bs = None
        self.cf_df = None
        self.last_fy = None
        self.most_recent_quarter = None
        try:
            self.stock_data = Ticker(self.symbol)
        except KeyError:
            print("Check your stock ticker")
        self.load_attributes()

    def load_attributes(self):

        try:
            self.name = self.stock_data.quote_type[str(self.symbol)]['shortName']
        except TypeError:
            self.name = ""
        self.price = [self.stock_data.financial_data[self.symbol]['currentPrice'],
                      self.stock_data.price[self.symbol]['currency']]
        self.price_currency = self.stock_data.price[self.symbol]['currency']
        self.shares = self.stock_data.key_stats[self.symbol]['sharesOutstanding']
        self.report_currency = self.stock_data.financial_data[self.symbol]['financialCurrency']
        self.annual_bs = self.get_balance_sheet("annual")
        self.quarter_bs = self.get_balance_sheet("quarterly")
        self.is_df = self.get_income_statement()
        self.cf_df = self.get_cash_flow()
        self.fx_rate = get_forex(self.report_currency, self.price_currency)
        try:
            self.last_dividend = -int(self.cf_df.loc['CashDividendsPaid'][0]) / self.shares
        except ZeroDivisionError:
            self.last_dividend = 0
        # left most column contains the most recent data
        self.last_fy = self.annual_bs.columns[0]
        self.most_recent_quarter = self.quarter_bs.columns[0]

    def get_balance_sheet(self, option="annual"):
        """Returns a DataFrame with selected balance sheet data

        :param option: annual or quarterly

        balance sheet keys:
          ['asOfDate', 'periodType', 'currencyCode', 'AccountsPayable',
               'AccountsReceivable', 'AccumulatedDepreciation',
               'AllowanceForDoubtfulAccountsReceivable', 'AvailableForSaleSecurities',
               'BuildingsAndImprovements', 'CapitalLeaseObligations', 'CapitalStock',
               'CashAndCashEquivalents', 'CashCashEquivalentsAndShortTermInvestments',
               'CashFinancial', 'CommonStock', 'CommonStockEquity',
               'ConstructionInProgress', 'CurrentAssets',
               'CurrentCapitalLeaseObligation', 'CurrentDebtAndCapitalLeaseObligation',
               'CurrentLiabilities', 'DividendsPayable',
               'FinancialAssetsDesignatedasFairValueThroughProfitorLossTotal',
               'FinishedGoods', 'Goodwill', 'GoodwillAndOtherIntangibleAssets',
               'GrossAccountsReceivable', 'GrossPPE', 'Inventory', 'InvestedCapital',
               'InvestmentinFinancialAssets', 'InvestmentsinAssociatesatCost',
               'LandAndImprovements', 'LongTermCapitalLeaseObligation',
               'LongTermDebtAndCapitalLeaseObligation', 'LongTermEquityInvestment',
               'MachineryFurnitureEquipment', 'MinorityInterest', 'NetPPE',
               'NetTangibleAssets', 'NonCurrentDeferredRevenue',
               'NonCurrentDeferredTaxesAssets', 'NonCurrentDeferredTaxesLiabilities',
               'NonCurrentPrepaidAssets', 'OrdinarySharesNumber',
               'OtherEquityInterest', 'OtherIntangibleAssets', 'OtherInvestments',
               'OtherPayable', 'OtherProperties', 'OtherReceivables',
               'OtherShortTermInvestments', 'Payables', 'PrepaidAssets', 'Properties',
               'RawMaterials', 'RetainedEarnings', 'ShareIssued', 'StockholdersEquity',
               'TangibleBookValue', 'TaxesReceivable', 'TotalAssets',
               'TotalCapitalization', 'TotalDebt', 'TotalEquityGrossMinorityInterest',
               'TotalLiabilitiesNetMinorityInterest', 'TotalNonCurrentAssets',
               'TotalNonCurrentLiabilitiesNetMinorityInterest', 'TotalTaxPayable',
               'TreasuryStock', 'WorkInProcess', 'WorkingCapital']
        """

        dummy = {
            "Dummy": [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]}

        bs_index = ['TotalAssets', 'CurrentAssets', 'CurrentLiabilities', 'CurrentDebtAndCapitalLeaseObligation',
                    'CurrentCapitalLeaseObligation', 'LongTermDebtAndCapitalLeaseObligation',
                    'LongTermCapitalLeaseObligation', 'TotalEquityGrossMinorityInterest', 'CommonStockEquity',
                    'CashAndCashEquivalents', 'OtherShortTermInvestments', 'InvestmentProperties',
                    'LongTermEquityInvestment', 'InvestmentinFinancialAssets', 'NetPPE']

        if option == "annual":
            # reverses the dataframe with .iloc[:, ::-1]
            balance_sheet = self.stock_data.balance_sheet(trailing=False).set_index('asOfDate').T.iloc[:, ::-1]
        else:
            balance_sheet = self.stock_data.balance_sheet(frequency="q", trailing=False).set_index('asOfDate') \
                                .T.iloc[:, ::-1]
        # Start of Cleaning: make sure the data has all the required indexes
        dummy_df = pd.DataFrame(dummy, index=bs_index)
        clean_bs = dummy_df.join(balance_sheet)
        bs_df = clean_bs.loc[bs_index]
        # Ending of Cleaning: drop the dummy column after join
        bs_df.drop('Dummy', inplace=True, axis=1)

        return bs_df.fillna(0)

    def get_income_statement(self):
        """Returns a DataFrame with selected income statement data

        income statement keys:
        ['asOfDate', 'periodType', 'currencyCode', 'BasicAverageShares',
       'BasicEPS', 'CostOfRevenue', 'DilutedAverageShares', 'DilutedEPS',
       'DilutedNIAvailtoComStockholders', 'EBIT',
       'GeneralAndAdministrativeExpense', 'GrossProfit',
       'ImpairmentOfCapitalAssets', 'InterestExpense',
       'InterestExpenseNonOperating', 'InterestIncome',
       'InterestIncomeNonOperating', 'MinorityInterests', 'NetIncome',
       'NetIncomeCommonStockholders', 'NetIncomeContinuousOperations',
       'NetIncomeFromContinuingAndDiscontinuedOperation',
       'NetIncomeFromContinuingOperationNetMinorityInterest',
       'NetIncomeIncludingNoncontrollingInterests', 'NetInterestIncome',
       'NetNonOperatingInterestIncomeExpense', 'NormalizedEBITDA',
       'NormalizedIncome', 'OperatingExpense', 'OperatingIncome',
       'OperatingRevenue', 'OtherNonOperatingIncomeExpenses',
       'OtherSpecialCharges', 'OtherunderPreferredStockDividend',
       'PretaxIncome', 'ReconciledCostOfRevenue', 'ReconciledDepreciation',
       'SellingAndMarketingExpense', 'SellingGeneralAndAdministration',
       'SpecialIncomeCharges', 'TaxEffectOfUnusualItems', 'TaxProvision',
       'TaxRateForCalcs', 'TotalExpenses', 'TotalRevenue', 'TotalUnusualItems',
       'TotalUnusualItemsExcludingGoodwill', 'WriteOff']
        """

        # reverses the dataframe with .iloc[:, ::-1]
        raw_is = self.stock_data.income_statement(trailing=False).set_index('asOfDate')
        income_statement = raw_is[raw_is['currencyCode'] == self.report_currency].T.iloc[:, ::-1]
        # print(income_statement.to_string())
        # Start of Cleaning: make sure the data has all the required indexes
        dummy = {"Dummy": [None, None, None, None, None]}
        is_index = ['TotalRevenue', 'CostOfRevenue', 'SellingGeneralAndAdministration', 'InterestExpense',
                    'NetIncomeCommonStockholders']
        dummy_df = pd.DataFrame(dummy, index=is_index)
        clean_is = dummy_df.join(income_statement)
        # print(clean_is.to_string())
        is_df = clean_is.loc[is_index]
        # Ending of Cleaning: drop the dummy column after join
        is_df.drop('Dummy', inplace=True, axis=1)
        is_df = is_df.fillna(0)

        return is_df

    def get_cash_flow(self):
        """Returns a DataFrame with selected Cash flow statement data

        cash flow statement keys:
        ['periodType', 'currencyCode', 'AmortizationCashFlow',
       'BeginningCashPosition', 'CapitalExpenditure', 'CashDividendsPaid',
       'ChangeInCashSupplementalAsReported', 'ChangeInInventory',
       'ChangeInOtherCurrentAssets', 'ChangeInPayable', 'ChangeInReceivables',
       'ChangeInWorkingCapital', 'ChangesInCash', 'CommonStockDividendPaid',
       'CommonStockIssuance', 'CommonStockPayments', 'Depreciation',
       'DepreciationAndAmortization', 'EffectOfExchangeRateChanges',
       'EndCashPosition', 'FinancingCashFlow', 'FreeCashFlow',
       'GainLossOnInvestmentSecurities', 'GainLossOnSaleOfPPE',
       'InterestPaidCFF', 'InterestReceivedCFI', 'InvestingCashFlow',
       'IssuanceOfCapitalStock', 'LongTermDebtPayments',
       'NetBusinessPurchaseAndSale', 'NetCommonStockIssuance', 'NetIncome',
       'NetIncomeFromContinuingOperations', 'NetInvestmentPurchaseAndSale',
       'NetIssuancePaymentsOfDebt', 'NetLongTermDebtIssuance',
       'NetOtherFinancingCharges', 'NetOtherInvestingChanges',
       'NetPPEPurchaseAndSale', 'OperatingCashFlow', 'OtherNonCashItems',
       'PurchaseOfBusiness', 'PurchaseOfInvestment', 'PurchaseOfPPE',
       'RepaymentOfDebt', 'RepurchaseOfCapitalStock', 'SaleOfInvestment',
       'SaleOfPPE', 'StockBasedCompensation', 'TaxesRefundPaid']
        """

        # reverses the dataframe with .iloc[:, ::-1]
        cash_flow = self.stock_data.cash_flow(trailing=False).set_index('asOfDate').T.iloc[:, ::-1]
        # Start of Cleaning: make sure the data has all the required indexes
        dummy = {"Dummy": [None, None, None, None, None, None]}
        cf_index = ['OperatingCashFlow', 'InvestingCashFlow', 'FinancingCashFlow',
                    'CashDividendsPaid', 'RepurchaseOfCapitalStock', 'EndCashPosition']
        dummy_df = pd.DataFrame(dummy, index=cf_index)
        clean_cf = dummy_df.join(cash_flow)
        cf_df = clean_cf.loc[cf_index]
        # Ending of Cleaning: drop the dummy column after join
        cf_df.drop('Dummy', inplace=True, axis=1)

        return cf_df.fillna(0)
