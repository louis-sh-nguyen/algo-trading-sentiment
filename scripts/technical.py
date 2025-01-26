import talib
import pandas as pd

class TechnicalAnalyser:
    def __init__(self, data: pd.DataFrame):
        self.data = data
        
    def calculate_indicators(self) -> pd.DataFrame:
        """Calculate technical indicators"""
        self.data['RSI'] = talib.RSI(self.data['Close'])
        self.data['MACD'], self.data['MACD_Signal'], _ = talib.MACD(self.data['Close'])
        self.data['SMA_20'] = talib.SMA(self.data['Close'], timeperiod=20)
        self.data['SMA_50'] = talib.SMA(self.data['Close'], timeperiod=50)
        return self.data
    
    def get_signals(self) -> dict:
        """Generate technical signals"""
        latest = self.data.iloc[-1]
        return {
            'RSI_Oversold': latest['RSI'] < 30,
            'MACD_Crossover': self.data['MACD'].iloc[-1] > self.data['MACD_Signal'].iloc[-1],
            'Above_SMA20': latest['Close'] > latest['SMA_20'],
            'Price_Above_SMA50': latest['Close'] > latest['SMA_50']
        }

if __name__ == '__main__':
    # Example usage
    from utils import fetch_data
    
    # Fetch sample data
    symbol = 'AAPL'
    data = fetch_data(symbol)
    
    # Create analyzer and calculate signals
    analyser = TechnicalAnalyser(data)
    data_with_indicators = analyser.calculate_indicators()
    signals = analyser.get_signals()
    
    print(f"Technical signals for {symbol}:")
    for signal_name, value in signals.items():
        print(f"{signal_name}: {value}")