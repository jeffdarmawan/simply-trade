import streamlit as st
import pandas as pd
import oandapyV20
import oandapyV20.endpoints.trades as trades
import oandapyV20.endpoints.pricing as pricing
import oandapyV20.endpoints.accounts as accounts
import oandapyV20.endpoints.positions as positions

access_token = "f176a52ece6296e57df035992ee409d3-d299d6aaafa65622d5418531ebe83a00"
account_id = "101-003-28603640-001"

class OandaAPI:
    def __init__(self, access_token):
        self.client = oandapyV20.API(access_token=access_token, environment="practice")
        self.prices = {}
        self.summary_info = {}

    def get_prices(self):
        forex_pairs = ["EUR_USD", "USD_JPY", "GBP_USD", "AUD_USD"]
        params = {
            "instruments" : "EUR_USD,USD_JPY,GBP_USD,AUD_USD"
        }
        r = pricing.PricingInfo(accountID=account_id, params=params)
        self.client.request(r)
        for i in r.response['prices']:
            self.prices[i['instrument']] = i['bids'][0]['price']
        return self.prices
    
    
    def get_account_summary(self):
        r = accounts.AccountSummary(accountID=account_id)
        self.client.request(r)
        response = r.response
        self.summary_info = {   'balance': response['account']['balance'],
                                'currency': response['account']['currency'],
                                'positionValue': response['account']['positionValue'],
                                'pl': response['account']['pl'],
                                'unrealizedPL': response['account']['unrealizedPL'],
                            }
        return self.summary_info
    

    def get_order_history(self):
        open_time = []
        instrument = []
        price = []
        initial_units = []
        current_units = []
        unrealized_pnl = []
        realized_pnl = []

        forex_pairs = ["EUR_USD", "USD_JPY", "GBP_USD", "AUD_USD"]
        for forex_pair in forex_pairs:
            params = {
                "instrument" : str(forex_pair)
            }
            r = trades.TradesList(accountID=account_id, params=params)
            self.client.request(r)

            for item in r.response['trades']:
                open_time.append(item['openTime'])
                instrument.append(item['instrument'])
                price.append(item['price'])
                initial_units.append(item['initialUnits'])
                current_units.append(item['currentUnits'])
                unrealized_pnl.append(item['unrealizedPL'])
                realized_pnl.append(item['realizedPL'])
        
        order_history = pd.DataFrame({
            "Open Time": open_time,
            "Instrument": instrument,
            "Price": price,
            "Initial Units": initial_units,
            "Current Units": current_units,
            "Unrealized P&L": unrealized_pnl,
            "Realized P&L": realized_pnl
        })

        return order_history

    
class Delta_Data:
    def __init__(self):
        self.price_last_period = { 'EUR_USD': 0,
                                   'USD_JPY': 0,
                                   'GBP_USD': 0,
                                   'AUD_USD': 0
                                 }
        self.summary_info_last_period = { 'balance': 0,
                                          'positionValue': 0,
                                          'pl': 0,
                                          'unrealizedPL': 0,
                                          'annualized_return': 0,
                                          'max_drawdown': 0,
                                          'sharpe_ratio': 0,
                                          'win_rate': 0
                                        }
        
    def get_price_delta(self, current_prices):
        delta = {}
        for key in current_prices.keys():
            delta[key] = float(current_prices[key]) - float(self.price_last_period[key])
            self.price_last_period[key] = current_prices[key]
        return delta
        
    
    def get_summary_info_delta(self, current_summary_info):
        delta = {}
        for key in current_summary_info.keys():
            delta[key] = float(current_summary_info[key]) - float(self.summary_info_last_period[key])
            self.summary_info_last_period[key] = current_summary_info[key]
        return delta
    
    
