import pandas as pd
import numpy as np
from datetime import datetime

from utils import fetch_data  # run script directly
from strategy import Strategy   # run script directly
# from .utils import fetch_data   # relative import for tests
# from .strategy import Strategy   # relative import for tests

class Backtester:
    def __init__(self, strategy, symbols: list, start_date: str, 
                 initial_capital: float = 100000):
        self.strategy = strategy
        self.symbols = symbols
        self.start_date = start_date
        self.initial_capital = initial_capital
        self.positions = {}
        self.cash = initial_capital
        self.trades = []
        self.portfolio_values = []

    def run(self):
        data = {s: fetch_data(s) for s in self.symbols}
        dates = data[self.symbols[0]].index
        
        for date in dates:
            signals = {s: self.strategy.analyze_stock(s) for s in self.symbols}
            self._process_signals(signals, date, data)
            self._update_portfolio(date, data)
        
        return self._calculate_metrics()

    def _process_signals(self, signals, date, data):
        for symbol, signal in signals.items():
            if signal and signal['score'] > 70 and symbol not in self.positions:
                self._execute_trade(symbol, 'BUY', date, data[symbol].loc[date])
            elif signal and signal['score'] < 30 and symbol in self.positions:
                self._execute_trade(symbol, 'SELL', date, data[symbol].loc[date])

    def _execute_trade(self, symbol, action, date, price_data):
        price = price_data['Close']
        if action == 'BUY':
            position_size = self.cash * 0.1
            shares = position_size // price
            cost = shares * price
            if cost <= self.cash:
                self.positions[symbol] = {'shares': shares, 'cost': cost}
                self.cash -= cost
                self.trades.append({
                    'date': date,
                    'symbol': symbol,
                    'action': action,
                    'price': price,
                    'shares': shares
                })
        else:  # SELL
            position = self.positions[symbol]
            self.cash += position['shares'] * price
            self.trades.append({
                'date': date,
                'symbol': symbol,
                'action': action,
                'price': price,
                'shares': position['shares']
            })
            del self.positions[symbol]

    def _update_portfolio(self, date, data):
        portfolio_value = self.cash
        for symbol, position in self.positions.items():
            portfolio_value += position['shares'] * data[symbol].loc[date, 'Close']
        self.portfolio_values.append({
            'date': date,
            'value': portfolio_value
        })

    def _calculate_metrics(self):
        df = pd.DataFrame(self.portfolio_values)
        returns = df['value'].pct_change()
        return {
            'total_return': (df['value'].iloc[-1] / self.initial_capital - 1) * 100,
            'sharpe_ratio': returns.mean() / returns.std() * np.sqrt(252),
            'max_drawdown': (df['value'].max() - df['value'].min()) / df['value'].max() * 100,
            'trades': len(self.trades)
        }

if __name__ == '__main__':
    # Example usage
    symbols = ['AAPL', 'MSFT', 'GOOGL']
    strategy = Strategy(symbols)
    backtester = Backtester(strategy, symbols, '2022-01-01')
    results = backtester.run()
    print(f"Backtest Results:\n{results}")