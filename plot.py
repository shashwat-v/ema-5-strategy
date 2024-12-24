import pandas as pd
import plotly.graph_objects as go
import os
from datetime import datetime

directory = "./daily_candles_5min"

start_date = datetime(2023, 1, 1)
end_date = datetime(2024, 12, 20)

all_data = []

for filename in sorted(os.listdir(directory)):
    if filename.endswith(".csv"):
        file_date = datetime.strptime(filename.split(".")[0], "%Y-%m-%d")
        if start_date <= file_date <= end_date:
            filepath = os.path.join(directory, filename)
            df = pd.read_csv(filepath)
            df['timestamp'] = pd.to_datetime(df['timestamp']).dt.date
            all_data.append(df)

combined_df = pd.concat(all_data, ignore_index=True)

combined_df.sort_values(by="timestamp", inplace=True)

fig = go.Figure(data=[go.Candlestick(
    x=combined_df['timestamp'],
    open=combined_df['open'],
    high=combined_df['high'],
    low=combined_df['low'],
    close=combined_df['close'],
    name="Candles"
)])

fig.add_trace(go.Scatter(
    x=combined_df['timestamp'],
    y=combined_df['5EMA'],
    mode='lines',
    line=dict(color='blue', width=2),
    name='5 EMA'
))

fig.update_layout(
    title="Candlestick Chart with 5 EMA",
    xaxis_title="Time",
    yaxis_title="Price",
    template="plotly_dark"
)

fig.show()
