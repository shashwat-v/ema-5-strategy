from fyers_apiv3 import fyersModel
from fyers_apiv3.FyersWebsocket import data_ws
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import glob
import time
import math

client_id = "DYDX2P3BXM-100"
secret_key = "V44I3I6EUM"
redirect_uri = "https://www.google.com"
response_type = "code"
grant_type = "authorization_code"

session = fyersModel.SessionModel(
    client_id=client_id,
    secret_key=secret_key,
    redirect_uri=redirect_uri,
    response_type=response_type,
    grant_type=grant_type
)

response = session.generate_authcode()
print(response)

auth_code = str(input("Enter the Authorization Code: "))

session.set_token(auth_code)
response = session.generate_token()

df = pd.DataFrame()
df = response
access_token = df['access_token']

fyers = fyersModel.FyersModel(client_id=client_id, is_async=False, token=access_token, log_path="")
# from here do whatever you want!!!
# -------------------------------------------------------------------------------------------------

# ticker = "NSE:NIFTY50-INDEX"
ticker = "NSE:NIFTYBANK-INDEX"
timeframe = "5"
start_date = "2021-01-01"
end_date = "2024-12-20"
MAX_DAYS = 100

range_from = datetime.strptime(start_date, "%Y-%m-%d")
range_to = datetime.strptime(end_date, "%Y-%m-%d")

current_start = range_from

all_data = []

while current_start < range_to:
    current_end = min(current_start + timedelta(days=MAX_DAYS), range_to)

    start_date_str = current_start.strftime('%Y-%m-%d')
    end_date_str = current_end.strftime('%Y-%m-%d')

    print(f"Fetching data from {start_date_str} to {end_date_str}")

    data = {
        "symbol": ticker,
        "resolution": timeframe,
        "date_format": "1",
        "range_from": start_date_str,
        "range_to": end_date_str,
        "cont_flag": "1"
    }

    try:
        response = fyers.history(data=data)
        candles = response.get("candles", [])
        columns = ["epoch_time", "open", "high", "low", "close", "volume"]
        df = pd.DataFrame(candles, columns=columns)
        df['timestamp'] = pd.to_datetime(df['epoch_time'], unit='s')
        all_data.append(df)

    except Exception as e:
        print(f"Error fetching data for range {start_date_str} to {end_date_str}: {e}")

    current_start = current_end

all_data_df = pd.concat(all_data, ignore_index=True)
all_data_df['timestamp'] = all_data_df['timestamp'] + timedelta(hours=5, minutes=30)
all_data_df['5EMA'] = all_data_df['close'].ewm(span=5, adjust=False).mean()
all_data_df['date'] = all_data_df['timestamp'].dt.date

output_directory = "daily_candles_5min"
os.makedirs(output_directory, exist_ok=True)

existing_files = glob.glob(os.path.join(output_directory, "*.csv"))
for file in existing_files:
    os.remove(file)
    print(f"Deleted: {file}")

for date, group in all_data_df.groupby('date'):
    filename = os.path.join(output_directory, f"{date}.csv")
    
    group.drop(columns=['date', 'epoch_time'], inplace=True)
    group.to_csv(filename, index=False)

print("All daily candlestick data has been processed and saved.")