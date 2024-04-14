import json
import oandapyV20.endpoints.positions as positions
import oandapyV20.endpoints.transactions as transactions
from datetime import datetime
import pandas as pd
import oandapyV20
from oandapyV20.endpoints.accounts import AccountDetails
import oandapyV20.endpoints.trades as trades

import numpy as np

access_token = "3f0f1b513d44797ff63c09d9da612561-6480f119d75e63cea1e420564d12b6f1"
account_id = "101-003-28603773-001"


accountID = account_id
access_token = access_token
client = oandapyV20.API(access_token=access_token, environment="practice")


# Fetch transactions
def fetch_transactions(open_date, current_date):
    open_date = open_date.strftime('%Y-%m-%dT%H:%M:%S.000000Z')
    current_date = current_date.strftime('%Y-%m-%dT%H:%M:%S.000000Z')

    params = {
        "from": open_date,
        "to": current_date,
        "type": "ORDER_FILL"
    }
    r = transactions.TransactionList(accountID=account_id, params=params)
    data = client.request(r)
    return data['transactions']


# Process transactions to calculate equity
def process_transactions(transactions,capital):
    df = pd.DataFrame(transactions)
    df = df[df['type'] == 'ORDER_FILL']
    df['time'] = pd.to_datetime(df['time'])
    df['amount'] = pd.to_numeric(df['pl'], errors='coerce').fillna(0)
    df['cumulative'] = capital + df['amount'].cumsum()
    df.set_index('time', inplace=True)
    return df

# Calculate drawdowns
def calculate_drawdowns(df):
    df['peak'] = df['cumulative'].cummax()
    df['drawdown'] = df['peak'] - df['cumulative']
    df['drawdown_pct'] = (df['drawdown'] / df['peak']) * 100
    return df

def get_current_balance():
    request = AccountDetails(accountID=accountID)
    response = client.request(request)

    if response and 'account' in response:
        account_info = response['account']
        balance = float(account_info['balance'])
        return balance
        
    return None

def calculate_annualised_returns(capital, total_trading_days):
    
    current_balance = get_current_balance()
    annualised_returns = ( (current_balance/capital * 100 ) / int(total_trading_days) )* 252

    return annualised_returns


def fetch_balance_changes(open_date, current_date):
    open_date = open_date.strftime('%Y-%m-%dT%H:%M:%S.000000Z')
    current_date = current_date.strftime('%Y-%m-%dT%H:%M:%S.000000Z')

    params = {
        "from": open_date,
        "to": current_date,
        "type": "DAILY"
    }
    r = transactions.TransactionList(accountID=account_id, params=params)
    data = client.request(r)
    df = pd.DataFrame(data['transactions'])
    if not df.empty:
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
        df['time'] = pd.to_datetime(df['time'])
        df.set_index('time', inplace=True)
        df = df.resample('D').sum()  # Sum daily changes
    return df

def calculate_sharpe_ratio(df):
    # The risk-free daily rate assume 1% annual rate
    risk_free_rate = 0.01 / 365
    df['excess_daily_return'] = df['amount'] - risk_free_rate
    
    # Mean of excess returns
    mean_excess_return = df['excess_daily_return'].mean()
    
    # Standard deviation of returns
    std_dev = df['excess_daily_return'].std()
    
    # Sharpe ratio
    sharpe_ratio = mean_excess_return / std_dev * np.sqrt(252)  # sqrt(252) annualizes the standard deviation
    
    return sharpe_ratio

def fetch_closed_trades():
    r = trades.TradesList(accountID=account_id, params={"state": "CLOSED"})
    resp = client.request(r)
    return resp['trades']

def calculate_win_rate_from_trades(trades):
    wins = sum(1 for trade in trades if float(trade['realizedPL']) > 0)
    losses = sum(1 for trade in trades if float(trade['realizedPL']) < 0)
    total_trades = wins + losses
    win_rate = (wins / total_trades) * 100 if total_trades > 0 else 0
    return win_rate

def pnl_all_positions():
    request = positions.OpenPositions(accountID=account_id)
    response = client.request(request)
    open_positions = response.get("positions", [])
    pnl = sum([float(pos['unrealizedPL']) for pos in open_positions])
    return pnl
