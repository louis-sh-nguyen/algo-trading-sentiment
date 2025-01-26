import yfinance as yf
from datetime import datetime, timedelta

class SentimentAnalyser:
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.stock = yf.Ticker(symbol)
    
    def analyse(self) -> float:
        """Simple sentiment analysis (0-100)"""
        try:
            news = self.stock.news
            if not news:
                return 50  # Neutral if no news
                
            # Basic sentiment based on number of recent news
            recent_news = [
                n for n in news 
                if datetime.fromtimestamp(n['providerPublishTime']) > 
                datetime.now() - timedelta(days=7)
            ]
            
            return min(100, len(recent_news) * 10)
        except:
            return 50

if __name__ == '__main__':
    # Example usage
    symbol = 'AAPL'
    analyzer = SentimentAnalyser(symbol)
    
    # Get sentiment score
    sentiment_score = analyzer.analyse()
    print(f"Sentiment score for {symbol}: {sentiment_score}")