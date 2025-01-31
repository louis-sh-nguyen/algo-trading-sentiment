from utils import setup_logging, fetch_data
from technical import TechnicalAnalyser
from fundamental import FundamentalAnalyser
from sentiment import SentimentAnalyser
import logging
from typing import Dict
import pandas as pd

class Strategy:
    def __init__(self, symbols: list):
        self.symbols = symbols
        self.stock_data: Dict[str, pd.DataFrame] = {}
    
    def fetch_all_data(self):
        """Fetch data for all symbols once"""
        for symbol in self.symbols:
            try:
                self.stock_data[symbol] = fetch_data(symbol)
            except Exception as e:
                logging.error(f"Error fetching data for {symbol}: {e}")
                self.stock_data[symbol] = None
    
    def refresh_data(self):
        """Clear and refresh all stock data"""
        self.stock_data.clear()
        self.fetch_all_data()
    
    def analyse_stock(self, symbol: str) -> dict:
        """Analyze single stock using stored data"""
        try:
            # Check if data exists, fetch if not
            if not self.stock_data:
                self.fetch_all_data()
            
            if self.stock_data.get(symbol) is None:
                return None
            
            tech = TechnicalAnalyser(self.stock_data[symbol])
            tech_score = tech.analyse()
            
            fund = FundamentalAnalyser(symbol)
            fund_score = fund.analyse()
            
            sent = SentimentAnalyser(symbol)
            sent_score = sent.analyse()
            
            total_score = (
                tech_score * 0.4 +
                fund_score * 0.4 +
                sent_score * 0.2
            )
            
            return {
                'symbol': symbol,
                'score': total_score,
                'technical': tech_score,
                'fundamental': fund_score,
                'sentiment': sent_score
            }
        except Exception as e:
            logging.error(f"Error analyzing {symbol}: {e}")
            return None

    def select_top_stocks(self, score_type: str = 'total', n: int = 5) -> list:
        """
        Select top N stocks based on specified score type
        
        Args:
            score_type: 'total', 'technical', 'fundamental', or 'sentiment'
            n: number of stocks to return (default 5)
        """
        results = []
        
        # Analyze all stocks
        for symbol in self.symbols:
            result = self.analyse_stock(symbol)
            if result:
                results.append(result)
        
        # Define score extraction functions
        score_map = {
            'total': lambda x: x['score'],           # Get total weighted score
            'technical': lambda x: x['technical'],   # Get technical score
            'fundamental': lambda x: x['fundamental'],# Get fundamental score
            'sentiment': lambda x: x['sentiment']    # Get sentiment score
        }

        # Validate score type
        if score_type not in score_map:
            raise ValueError(f"Invalid score type: {score_type}")

        # Sort results using selected score function
        sorted_results = sorted(
            results,                # List of stock analysis results 
            key=score_map[score_type],  # Lambda function for chosen score
            reverse=True           # Highest scores first
        )
        
        return sorted_results[:n]

if __name__ == '__main__':
    # Example usage
    symbols = [
        'AAPL',  'MSFT',  'GOOGL', 'AMZN',  'META',  'NVDA', 'TSLA',
        'INTC',  'AMD',   'CRM',   'ADBE',  'ORCL',  'CSCO', 'IBM',
        'QCOM',  'TXN',   'AVGO',  'ARM',   'PYPL',  'MU',   'UBER',
        'ASML', 'SHOP',  'NOW',   'SNOW',  'PLTR',  'NET',  'AMAT',
    ]
    strategy = Strategy(symbols)
    strategy.refresh_data()
    
    # Get top stocks by different metrics
    print("\nTop Stocks by Total Score:")
    top_total = strategy.select_top_stocks('total', n=10)
    for stock in top_total:
        print(f"{stock['symbol']}: {stock['score']:.2f}")
        
    print("\nTop Stocks by Fundamental Score:")
    top_tech = strategy.select_top_stocks('fundamental', n=10)
    for stock in top_tech:
        print(f"{stock['symbol']}: {stock['technical']:.2f}")        
        
    print("\nTop Stocks by Technical Score:")
    top_tech = strategy.select_top_stocks('technical', n=10)
    for stock in top_tech:
        print(f"{stock['symbol']}: {stock['technical']:.2f}")        
        
    print("\nTop Stocks by Sentiment Score:")
    top_tech = strategy.select_top_stocks('Sentiment', n=10)
    for stock in top_tech:
        print(f"{stock['symbol']}: {stock['sentiment']:.2f}")        
