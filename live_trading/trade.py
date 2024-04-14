from signal_generator import get_current_price, get_top10_features, fetch_candlestick_data
from risk_manager import get_current_price, get_instrument_precision, get_current_balance, get_quantity,get_pnl_price,get_open_positions, check_instrument_positions,place_market_order, close_position, calculate_total_unrealised_pnl, close_all_trades

import time
import oandapyV20
import oandapyV20.endpoints.pricing as pricing
import pandas as pd
import numpy as np
import joblib
from status import Status

# ====== OANDA account details ======
access_token = "3f0f1b513d44797ff63c09d9da612561-6480f119d75e63cea1e420564d12b6f1"
account_id = "101-003-28603773-001"

accountID = account_id
access_token = access_token
client = oandapyV20.API(access_token=access_token, environment="practice")

# ====== Constants ======

pairs_mapping = {
    'EUR_USD': 'EURUSD=X',
    'USD_JPY': 'JPY=X',   
    'GBP_USD': 'GBPUSD=X',
    'AUD_USD': 'AUDUSD=X',
    'NZD_USD': 'NZDUSD=X',
    'USD_HKD': 'HKD=X',
    'USD_SGD': 'SGD=X',
    'USD_MXN': 'MXN=X',
    'USD_THB': 'THB=X',
    'USD_ZAR': 'ZAR=X',
}

# Library import:
models_15 = joblib.load("models_15mins.joblib")
model_15mins_features = ['DPO_20', 'THERMO_20_2_0.5', 'CFO_9', 'TRUERANGE_1', 'PDIST', 'BBB_5_2.0', 'RVI_14', 'SLOPE_1', 'BULLP_13', 'BOP']

# ===== Variables =====
# Variable to be changed 
# Risk reward (1:3) % based on prices
default_take_profit = 0.015
default_stop_loss = 0.005

# Setup
default_usd_pairs = ["EUR_USD","USD_JPY", "GBP_USD","AUD_USD"]

# trade_cycle
default_trade_cycle = 1

# order type
default_order_type = "MARKET"

# Lookback Count
# look back set as 20 to get the latest price action
default_lookback_count = 20

# ====== Trading Strategy ======

def trade_attempt(
        status: Status = Status.Inactive,
        usd_pairs: list = default_usd_pairs,
        take_profit: float = default_take_profit,
        stop_loss: float = default_stop_loss,
        trade_cycle: int = default_trade_cycle,
        order_type: str = default_order_type,
        lookback_count: int = default_lookback_count):
    print("Trading attempt...")
    if status == Status.Active:       
        try:
            print("Running strategy...")

            positions_dict = get_open_positions()

            for instrument in usd_pairs:
                print(instrument)
                price = get_current_price(instrument)
                price_df = fetch_candlestick_data(instrument, lookback_count)
                
                top10_df3 = get_top10_features(price_df["m_open"], price_df["m_high"], price_df["m_low"], price_df["m_close"],model_15mins_features)
                price_df = pd.concat([price_df, top10_df3], axis=1)
                model_data = price_df[model_15mins_features]

                # make prediction for the next period price direction
                # get the currency pair's mode
                model = models_15[pairs_mapping[instrument]]

                # save the predicted y direction
                #   1 is positive => buy t+1, 0 is not positive => sell t+1
                y_pred = model.predict(model_data)
                price_df["prediction_on_next_close"] = [1 if x > 0 else -1 for x in y_pred]
                #find the last signal
                signal = price_df["prediction_on_next_close"].iloc[-1]

                position_type = check_instrument_positions(positions_dict,instrument)
                #
                if position_type == "None": 
                    if signal == 1: 
                        quantity = get_quantity(instrument,signal)
                        pnl_price = get_pnl_price(instrument, signal,take_profit,stop_loss)
                        take_profit_price = pnl_price[0]
                        stop_loss_price = pnl_price[1]
                        place_market_order(instrument, order_type, quantity, take_profit_price, stop_loss_price)

                    elif signal == -1: 
                        quantity = get_quantity(instrument,signal)
                        pnl_price = get_pnl_price(instrument, signal,take_profit,stop_loss)
                        take_profit_price = pnl_price[0]
                        stop_loss_price = pnl_price[1]
                        place_market_order(instrument, order_type, quantity, take_profit_price, stop_loss_price)

                elif position_type == "Long":
                    if signal == 1: 
                        print ("Hold the trade")
                        
                    elif signal == -1: 
                        close_position = close_position(instrument, long_units='ALL', short_units='ALL')
                        quantity = get_quantity(instrument,signal)
                        pnl_price = get_pnl_price(instrument, signal,take_profit,stop_loss)
                        take_profit_price = pnl_price[0]
                        stop_loss_price = pnl_price[1]
                        place_market_order(instrument, order_type, quantity, take_profit_price, stop_loss_price)

                elif position_type == "Short":
                    if signal == 1: 
                        close_position = close_position(instrument, long_units='ALL', short_units='ALL')
                        quantity = get_quantity(instrument,signal)
                        pnl_price = get_pnl_price(instrument, signal,take_profit,stop_loss)
                        take_profit_price = pnl_price[0]
                        stop_loss_price = pnl_price[1]
                        place_market_order(instrument, order_type, quantity, take_profit_price, stop_loss_price)

                    elif signal == -1: 
                        print ("Hold the trade")
                else:
                    pass  

            time.sleep(trade_cycle)  # Wait for a minute before the next cycle

        except Exception as e:
            print(f"An error occurred: {e}")
            #status = 'Inactive'

    elif status == Status.Inactive:
        
        try: 
            print("Trade is still open")
            positions_dict = get_open_positions()
            # print(positions_dict)
            # print("Current balance: {:.2f}".format(get_current_balance()))

        except Exception as e:
            print(f"An error occurred: {e}")
            status = 'Stop'

    else: 
        print("Closing all Trades")
        close_all_trades(client, accountID)
        print("Current balance: {:.2f}".format(get_current_balance()))
