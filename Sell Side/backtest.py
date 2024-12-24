import pandas as pd
import plotly.graph_objects as go

df = pd.read_csv("../daily_candles_5min/2024-12-19.csv")
df['timestamp'] = pd.to_datetime(df['timestamp'])

marked_rows = []

for i in range(0, len(df)-1):
    current_candle = df.iloc[i]
    next_candle = df.iloc[i + 1]
    
    if current_candle['low']>current_candle['5EMA']:
        if next_candle['low']> next_candle['5EMA']:
            if current_candle['low'] > next_candle['low']:
                marked_rows.append((current_candle['timestamp'], current_candle['low'], "Earlier Candle"))
            else:
                marked_rows.append((next_candle['timestamp'], next_candle['low'], "Later Candle"))
        else:
            marked_rows.append((current_candle['timestamp'], current_candle['low'], "Earlier Candle"))
        
marked_df = pd.DataFrame(marked_rows, columns=['timestamp', 'low', 'mark_type'])
marked_df = (
    marked_df.groupby('timestamp', as_index=False)
    .agg({'low': 'first', 'mark_type': lambda x: 'Combined' if len(x) > 1 else x.iloc[0]})
)

fig = go.Figure(data=[go.Candlestick(
    x=df['timestamp'],
    open=df['open'],
    high=df['high'],
    low=df['low'],
    close=df['close'],
    name="Candles"
)])

fig.add_trace(go.Scatter(
    x=df['timestamp'],
    y=df['5EMA'],
    mode='lines',
    line=dict(color='blue', width=2),
    name='5 EMA'
))

fig.add_trace(go.Scatter(
    x=marked_df['timestamp'],
    y=marked_df['low'],
    mode='markers',
    marker=dict(color='green', size=10, symbol='triangle-up'),
    name='True Condition'
))

fig.update_layout(
    title="Candlestick Chart with 5 EMA and True Conditions",
    xaxis_title="Time",
    yaxis_title="Price",
    template="plotly_dark"
)

fig.show()

