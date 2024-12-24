import pandas as pd
import os
import numpy as np
import plotly.graph_objects as go

total_profit = 0
total_loss = 0
decimal_returns = []
initial_capital = 100000
equity = initial_capital
equity_curve = []

data_folder = "daily_candles_5min"

for file in os.listdir(data_folder):
    if file.endswith(".csv"):
        data = pd.read_csv(os.path.join(data_folder, file))
        data['5EMA'] = data['close'].ewm(span=5).mean()

        alert_candle_index = None
        i = 1

        while i < len(data):
            if data['low'][i] > data['5EMA'][i]:
                if alert_candle_index is None or data['low'][i] > data['low'][alert_candle_index]:
                    alert_candle_index = i
            elif alert_candle_index is not None:
                if data['low'][i] < data['low'][alert_candle_index]:
                    entry_price = data['low'][alert_candle_index]
                    candle_range = data['high'][alert_candle_index] - data['low'][alert_candle_index]
                    stop_loss = data['high'][alert_candle_index] + (0.06 * candle_range)
                    target = entry_price - (stop_loss - entry_price) * 3

                    trade = {
                        'entry_time': data['timestamp'][alert_candle_index],
                        'entry_price': entry_price,
                        'stop_loss': stop_loss,
                        'target': target,
                        'exit_time': None,
                        'exit_price': None,
                        'result': None,
                        'pnl': None,
                        'return': None
                    }

                    for j in range(i + 1, len(data)):
                        if data['high'][j] > stop_loss:
                            trade['exit_time'] = data['timestamp'][j]
                            trade['exit_price'] = stop_loss
                            trade['result'] = 'loss'
                            trade['pnl'] = entry_price - stop_loss
                            trade['return'] = (stop_loss - entry_price) / entry_price
                            decimal_returns.append(trade['return'])
                            equity += trade['pnl'] * (initial_capital / entry_price)
                            equity_curve.append(equity)
                            total_loss += abs(trade['pnl'])
                            i = j + 1
                            break
                        elif data['low'][j] < target:
                            trade['exit_time'] = data['timestamp'][j]
                            trade['exit_price'] = target
                            trade['result'] = 'profit'
                            trade['pnl'] = entry_price - target
                            trade['return'] = (target - entry_price) / entry_price
                            decimal_returns.append(trade['return'])
                            equity += trade['pnl'] * (initial_capital / entry_price)
                            equity_curve.append(equity)
                            total_profit += abs(trade['pnl'])
                            i = j + 1
                            break

                    alert_candle_index = None
                    continue
                elif data['low'][i] > data['low'][alert_candle_index]:
                    alert_candle_index = i
            i += 1

final_return = (equity - initial_capital) / initial_capital
daily_returns = [equity_curve[i + 1] - equity_curve[i] for i in range(len(equity_curve) - 1)]
avg_daily_return = np.mean(daily_returns) if daily_returns else 0
std_dev_daily_return = np.std(daily_returns) if daily_returns else 1
sharpe_ratio = (avg_daily_return - 0.02 / 252) / std_dev_daily_return if std_dev_daily_return else 0

print(f"\nTotal Profit from Profitable Trades: {total_profit:.2f}")
print(f"Total Loss from Losing Trades: {total_loss:.2f}")
print(f"Final Equity: {equity:.2f}")
print(f"Final Return: {final_return:.2%}")
print(f"Sharpe Ratio: {sharpe_ratio:.2f}")

equity_df = pd.DataFrame({'Equity': equity_curve})
equity_df.to_csv("equity_curve.csv", index=False)

returns_df = pd.DataFrame(decimal_returns, columns=['Decimal Return'])
returns_df.to_csv("decimal_returns.csv", index=False)

equity_df = pd.read_csv("equity_curve.csv")
returns_df = pd.read_csv("decimal_returns.csv")

fig_equity = go.Figure()
fig_equity.add_trace(go.Scatter(
    y=equity_df['Equity'],
    mode='lines',
    name='Equity Curve',
    line=dict(color='green')
))
fig_equity.update_layout(
    title="Equity Curve Analysis",
    xaxis_title="Trade Number",
    yaxis_title="Equity",
    template="plotly_dark"
)
fig_equity.show()

fig_returns = go.Figure()
fig_returns.add_trace(go.Histogram(
    x=returns_df['Decimal Return'],
    nbinsx=50,
    name='Decimal Returns',
    marker=dict(color='blue')
))
fig_returns.update_layout(
    title="Distribution of Returns",
    xaxis_title="Decimal Return",
    yaxis_title="Frequency",
    template="plotly_dark"
)
fig_returns.show()

cumulative_return = equity_df['Equity'].iloc[-1] / equity_df['Equity'].iloc[0] - 1
cumulative_percent = (equity_df['Equity'] / equity_df['Equity'].iloc[0]) * 100

fig_cumulative = go.Figure()
fig_cumulative.add_trace(go.Scatter(
    y=cumulative_percent,
    mode='lines',
    name='Cumulative Return (%)',
    line=dict(color='orange')
))
fig_cumulative.update_layout(
    title=f"Cumulative Return: {cumulative_return:.2%}",
    xaxis_title="Trade Number",
    yaxis_title="Cumulative Return (%)",
    template="plotly_dark"
)
fig_cumulative.show()