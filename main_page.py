import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from Relative_Functions import OandaAPI, Delta_Data

access_token = "f176a52ece6296e57df035992ee409d3-d299d6aaafa65622d5418531ebe83a00"
api_client = OandaAPI(access_token=access_token)
api_delta = Delta_Data()

st.set_page_config(layout="wide")

current_pair = "BTC_USD"
# ********************************************* sidebar begin *********************************************
st.sidebar.title("Operation Panel")

if st.sidebar.button("EUR-USD 🇪🇺🇺🇸", on_click=None, type="secondary", use_container_width=True):
    st.sidebar.write("You have selected EUR-USD 🇪🇺🇺🇸")
    current_pair = "EUR_USD"
if st.sidebar.button("USD/JPY 🇺🇸🇯🇵", on_click=None, type="secondary", use_container_width=True):
    st.sidebar.write("You have selected USD/JPY 🇺🇸🇯🇵")
    current_pair = "USD_JPY"
if st.sidebar.button("GBP/USD 🇬🇧🇺🇸", on_click=None, type="secondary", use_container_width=True):
    st.sidebar.write("You have selected GBP/USD 🇬🇧🇺🇸")
    current_pair = "GBP_USD"
if st.sidebar.button("AUD/USD 🇦🇺🇺🇸", on_click=None, type="secondary", use_container_width=True):
    st.sidebar.write("You have selected AUD/USD 🇦🇺🇺🇸")
    current_pair = "AUD_USD"

st.sidebar.markdown("---")

summary_info_sidebar = api_client.get_account_summary()
st.sidebar.dataframe(data=summary_info_sidebar,use_container_width=True)


# ************************************** Trading Strategy Buttons ****************************************
from live_trading.status import Status
import requests

# http request to activate the trading strategy
def send_request(status: Status):
    path = "deactivate"
    if status == Status.Active:
        path = "activate"
    elif status == Status.Stop:
        path = "stop"

    url = "http://127.0.0.1:5003/" + path
    
    try:
        # Send the POST request with error handling
        response = requests.post(url, json={"status": 1})
        response.raise_for_status()  # Raise an exception for non-200 status codes

        print("success")

    except requests.exceptions.RequestException as e:
        # Handle errors during request execution (e.g., connection issues)
        print(f"Error: An error occurred during the request - {e}")


# input
# - model:
#    - 1 min
#    - 15 min
#    - 5 min
# - take profit
#    - 
# - stop loss
# - granularity
# - trade_cycle

status = Status.Inactive

if st.sidebar.button("Start", key="start_button", help="Click to start", use_container_width=True):
    status = Status.Active
    send_request(status)

if st.sidebar.button("Pause", key="pause_button", help="Click to pause", use_container_width=True):
    status = Status.Inactive
    send_request(status)

if st.sidebar.button("Stop", key="stop_button", help="Click to stop", use_container_width=True):
    status = Status.Stop
    send_request(status)

if status == Status.Active:
    st.sidebar.success("Trading Strategy is Running")
elif status == Status.Inactive:
    st.sidebar.success("Trading Strategy is Paused")
else:
    st.sidebar.error("Trading Strategy has been Stopped")


# ********************************************* sidebar end *********************************************




# ********************************************* main page begin *****************************************

# 1. Real Time Prices

@st.experimental_fragment(run_every=5)
def show_price():
    prices = api_client.get_prices()
    price_delta = api_delta.get_price_delta(prices)
    tp1, tp2, tp3, tp4 = st.columns(4)
    with tp1:
        st.metric(label="EUR/USD", value=round(float(prices['EUR_USD']),4), delta=price_delta['EUR_USD'])
    with tp2:
        st.metric(label="USD/JPY", value=round(float(prices['USD_JPY']),4), delta=price_delta['USD_JPY'])
    with tp3:
        st.metric(label="GBP/USD", value=round(float(prices['GBP_USD']),4), delta=price_delta['GBP_USD'])
    with tp4:
        st.metric(label="AUD/USD", value=round(float(prices['AUD_USD']),4), delta=price_delta['AUD_USD'])

show_price()


# ================================== CandlePlot ==================================
st.header("CandlePlot")
import plotly.graph_objects as go

from app import update_figure

@st.experimental_fragment(run_every=10)
def update_candle_plot():
    st.plotly_chart(update_figure(tickerChoice=current_pair), use_container_width=True)
update_candle_plot()


# 2. Strategy Explanation
@st.cache_data
def read_strategy_explaination():
    with open('./materials/Strategy_Explaination.txt', 'r') as f:
        return f.read()
    
with st.expander("Strategy Description"):
    strategy_explaination = read_strategy_explaination()
    st.write(strategy_explaination)
    # st.image("https://static.streamlit.io/examples/dice.jpg")


# 3. Performance Metrics
st.header("Performance Metrics")

@st.experimental_fragment(run_every=30)
def account_summary():

    summary_info_api = api_client.get_account_summary()

    #TODO update the hard-coded data source
    metrics_data = {"balance": round(float(summary_info_api['balance']),2),
                    "positionValue": round(float(summary_info_api['positionValue']),2),
                    "pl":   round(float(summary_info_api['pl']),2),
                    "unrealizedPL": round(float(summary_info_api['unrealizedPL']),2),
                    "annualized_return": 12.59,
                    "max_drawdown": 3.78,
                    "sharpe_ratio": 1.14,
                    "win_rate": 64 
                }
    
    metrics_data_delta = api_delta.get_summary_info_delta(metrics_data)
    

    # data get from API
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Total Capital", value=metrics_data["balance"], delta=metrics_data_delta["balance"])
    with col2:
        st.metric(label="Position Value", value=metrics_data["positionValue"], delta=metrics_data_delta["positionValue"])
    with col3:
        st.metric(label="Realized P&L", value=metrics_data["pl"], delta=metrics_data_delta["pl"])
    with col4:
        st.metric(label="Unrealized P&L", value=metrics_data["unrealizedPL"], delta=metrics_data_delta["unrealizedPL"])

    # data get from calculation
    col5, col6, col7, col8 = st.columns(4)
    with col5:
        st.metric(label="Annualized Return", value=metrics_data["annualized_return"], delta=metrics_data_delta["annualized_return"], delta_color="inverse")
    with col6:
        st.metric(label="Maximum Drawdown", value=metrics_data["max_drawdown"], delta=metrics_data_delta["max_drawdown"], delta_color="inverse")
    with col7:
        st.metric(label="Sharpe Ratio", value=metrics_data["sharpe_ratio"], delta=metrics_data_delta["sharpe_ratio"], delta_color="inverse")
    with col8:
        st.metric(label="Win Rate(%)", value=metrics_data["win_rate"], delta=metrics_data_delta["win_rate"], delta_color="inverse")

account_summary()


# 4. P&L Curve vs Benchmark
st.header("Profit and Loss")

# the input P&L data shall be a dataframe like this:
# | timestamps | P&L | Benchmark |
# |------------|-----|-----------|
# | 2022-01-01 | 100 | 200       |
# | 2022-01-02 | 200 | 300       |
# | ...        | ... | ...       |
pnl_data = pd.DataFrame(np.random.randn(20, 3), columns=["timestamps", "P&L", "Benchmark"])
st.line_chart(pnl_data, x="timestamps", y=["P&L", "Benchmark"])


# 5. Order History
st.header("Historical Orders")
# re-check the order history every 15 seconds
@st.experimental_fragment(run_every=30)
def get_order_history_():
    order_history = api_client.get_order_history()
    # return order_history
    # order_history = get_order_history_() # details in Relative_Functions.py

    st.dataframe(data=order_history,
                use_container_width=True,
                hide_index=None,
                column_order=None,
                column_config=None
                )
get_order_history_()


# # 6. Other Visualizations
# st.header("Performance Metrics")


# ********************************************* main page end *******************************************