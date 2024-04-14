import numpy as np
from oandapyV20 import API
import oandapyV20
import oandapyV20.endpoints.positions as positions
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.trades as trades
import oandapyV20.endpoints.pricing as pricing
from oandapyV20.endpoints.instruments import InstrumentsCandles
from datetime import date, timedelta
import pandas_ta
from pandas_ta.volatility import thermo, true_range, pdist, bbands, rvi
import pandas as pd


access_token = "3f0f1b513d44797ff63c09d9da612561-6480f119d75e63cea1e420564d12b6f1"
account_id = "101-003-28603773-001"

accountID = account_id
access_token = access_token

client = oandapyV20.API(access_token=access_token, environment="practice")

def get_current_price(instrument):
    params = {
        "instruments": instrument
    }
    request = pricing.PricingInfo(accountID=account_id, params=params)
    response = client.request(request)

    if 'prices' in response and response['prices']:
        return float(response['prices'][0]['bids'][0]['price'])

    return None

def get_top10_features(open, high, low, close,model_features):
    # top 10 features 'DPO_20', 'THERMO_20_2_0.5', 'CFO_9', 'TRUERANGE_1', 'PDIST', 'BBB_5_2.0', 'RVI_14', 'SLOPE_1', 'BULLP_13', 'BOP'
    dpo_df = pandas_ta.trend.dpo(close)
    thermo_df = thermo(high, low)
    cfo_df = pandas_ta.momentum.cfo(close)
    truerange_df = true_range(high, low, close)
    pdist_df = pdist(open, high, low, close)
    bbands_df = bbands(close)
    #cci_df = pandas_ta.momentum.cci(high, low, close)
    rvi_df = rvi(close, high, low)
    slope_df = pandas_ta.momentum.slope(close)
    eri_df = pandas_ta.momentum.eri(high, low, close)
    bop_df = pandas_ta.momentum.bop(open, high, low, close)

    combined = pd.concat([dpo_df, thermo_df, slope_df, cfo_df, truerange_df, bbands_df, rvi_df, pdist_df, eri_df, bop_df], axis=1)
    return combined[model_features].copy()


def fetch_candlestick_data(instrument_name, lookback_count):
    # Initialize the Oanda API client
    api = API(access_token=access_token, environment="practice")
    #UTC time zone
    # Define the parameters for the candlestick data request
    params = {
        'count': lookback_count,
        'granularity': 'M15',
        'price': 'MBA',  #mid, bid, ask
    }

    # Request the candlestick data from Oanda API
    candles_request = InstrumentsCandles(instrument=instrument_name, params=params)
    response = api.request(candles_request)

    price_data = []
    for entry in response['candles']:
        price_entry = {
            'time': entry['time'],
            'volume': entry['volume'],
            'bid_close': float(entry['bid']['c']),
            'ask_close': float(entry['ask']['c']),
            'm_open': float(entry['mid']['o']),
            'm_high': float(entry['mid']['h']),
            'm_low': float(entry['mid']['l']),
            'm_close': float(entry['mid']['c'])
        }
        price_data.append(price_entry)
    price_df = pd.DataFrame(price_data)
    
    # Extract the close prices from the response
    # close_prices = [float(candle['mid']['c']) for candle in response['candles']]
    # bid_prices = [float(candle['bid']['c']) for candle in response['candles']]
    # ask_prices = [float(candle['ask']['c']) for candle in response['candles']]
    # #volume = [float(candle['volume']['c']) for candle in response['candles']]

    return price_df
