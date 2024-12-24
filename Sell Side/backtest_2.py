import pandas as pd
import os

total_profit = 0
total_loss = 0

data_folder = "../daily_candles_5min"

for file in os.listdir(data_folder):
    if file.endswith(".csv"):
        print(f"Processing file: {file}")
        data = pd.read_csv(os.path.join(data_folder, file))
        data['5EMA'] = data['close'].ewm(span=5).mean() 

        alert_candle_index = None
        trades = [] 
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
                        'pnl': None
                    }

                    for j in range(i + 1, len(data)):
                        if data['high'][j] > stop_loss: 
                            trade['exit_time'] = data['timestamp'][j]
                            trade['exit_price'] = stop_loss
                            trade['result'] = 'loss'
                            trade['pnl'] = entry_price - stop_loss
                            total_loss += abs(trade['pnl']) 
                            i = j + 1
                            break
                        elif data['low'][j] < target: 
                            trade['exit_time'] = data['timestamp'][j]
                            trade['exit_price'] = target
                            trade['result'] = 'profit'
                            trade['pnl'] = entry_price - target
                            total_profit += abs(trade['pnl'])
                            i = j + 1 
                            break

                    trades.append(trade)
                    alert_candle_index = None 
                    continue 
                elif data['low'][i] > data['low'][alert_candle_index]: 
                    alert_candle_index = i
            i += 1 

print(f"\nTotal Profit from Profitable Trades: {total_profit:.2f}")
print(f"Total Loss from Losing Trades: {total_loss:.2f}")
