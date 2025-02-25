import talib
import pandas as pd
import logging

class TechnicalAnalyser:
    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.signal_weights = {
            'RSI_Oversold': 35,       # Strong oversold signal
            'RSI_Overbought': -10,    # Weak overbought signal
            'MACD_Crossover': 5,       # Slight trend confirmation
            'Above_SMA20': 0,          # Neutral trend signal
            'Price_Above_SMA50': 0,    # Neutral trend signal
            'BB_Upper_Break': -15,     # Weak overbought signal
            'BB_Lower_Break': 25,      # Oversold signal
            'Stoch_Oversold': 30,      # Strong oversold signal
            'Stoch_Overbought': -10     # Weak overbought signal
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
        self.calculate_indicators()
        latest_data = self.data.iloc[-1]
        # Add Bollinger Bands
        upper, middle, lower = talib.BBANDS(self.data['Close'])
        
        # Add Stochastic Oscillator
        slowk, slowd = talib.STOCH(self.data['High'], self.data['Low'], self.data['Close'])
        
        return {
            'RSI_Oversold': latest_data['RSI'] < 30,
            'RSI_Overbought': latest_data['RSI'] > 70,
            'MACD_Crossover': self.data['MACD'].iloc[-1] > self.data['MACD_Signal'].iloc[-1],
            'Above_SMA20': latest_data['Close'] > latest_data['SMA_20'],
            'Price_Above_SMA50': latest_data['Close'] > latest_data['SMA_50'],
            'BB_Upper_Break': latest_data['Close'] > upper.iloc[-1],
            'BB_Lower_Break': latest_data['Close'] < lower.iloc[-1],
            'Stoch_Oversold': slowk.iloc[-1] < 20,
            'Stoch_Overbought': slowk.iloc[-1] > 80
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
            
            # Scale by volatility (example: using ATR)
            atr = talib.ATR(self.data['High'], self.data['Low'], self.data['Close']).iloc[-1]
            volatility_factor = min(1, atr / self.data['Close'].iloc[-1])  # Normalize
            
            # Apply non-linear scaling
            scaled_score = score * (1 + volatility_factor)
            
            # Normalize to 0-100 range
            normalized_score = 50 + scaled_score
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