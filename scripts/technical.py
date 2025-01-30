import talib
import pandas as pd
import logging

class TechnicalAnalyser:
    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.signal_weights = {
            'RSI_Oversold': 25,       # Strong buy signal
            'RSI_Overbought': -25,    # Strong sell signal
            'MACD_Crossover': 15,     # Trend confirmation
            'Above_SMA20': 10,        # Short-term trend
            'Price_Above_SMA50': 15   # Medium-term trend
        }
    
    def calculate_indicators(self) -> pd.DataFrame:
        """Calculate technical indicators"""
        self.data['RSI'] = talib.RSI(self.data['Close'])
        self.data['MACD'], self.data['MACD_Signal'], _ = talib.MACD(self.data['Close'])
        self.data['SMA_20'] = talib.SMA(self.data['Close'], timeperiod=20)
        self.data['SMA_50'] = talib.SMA(self.data['Close'], timeperiod=50)
        return self.data
    
    def get_signals(self) -> dict:
        """Generate technical signals"""
        data_with_indicators = self.calculate_indicators()
        latest_data = self.data.iloc[-1]
        return {
            'RSI_Oversold': latest_data['RSI'] < 30,
            'RSI_Overbought': latest_data['RSI'] > 70,
            'MACD_Crossover': self.data['MACD'].iloc[-1] > self.data['MACD_Signal'].iloc[-1],
            'Above_SMA20': latest_data['Close'] > latest_data['SMA_20'],
            'Price_Above_SMA50': latest_data['Close'] > latest_data['SMA_50']
        }

    def analyse(self) -> float:
        """Convert technical signals to normalized score (0-100)"""
        try:
            signals = self.get_signals()
            
            # Calculate raw score
            score = sum(
                self.signal_weights[signal] 
                for signal, is_active in signals.items()
                if is_active and signal in self.signal_weights
            )
            
            # Normalize to 0-100 range
            normalized_score = 50 + score
            return max(0, min(100, normalized_score))
            
        except Exception as e:
            logging.error(f"Error calculating technical score: {e}")
            return 50

if __name__ == '__main__':
    # Example usage
    from utils import fetch_data
    
    # Fetch sample data
    symbol = 'AAPL'
    data = fetch_data(symbol)
    
    # Create analyzer and calculate signals
    analyser = TechnicalAnalyser(data)
    score = analyser.analyse()
    
    print(f"Technical score for {symbol}: {score:.2f}")