from utils import setup_logging, fetch_data
from technical import TechnicalAnalyser
from fundamental import FundamentalAnalyser
from sentiment import SentimentAnalyser
import logging
from typing import Dict, List
import pandas as pd
from datetime import datetime, timedelta

class Strategy:
    def __init__(self, symbols: list):
        self.symbols = symbols
        self.stock_data: Dict[str, pd.DataFrame] = {}
        self.analysis_results: Dict[str, dict] = {}
        self.last_update = None
    
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
    
    def analyze_all_stocks(self):
        """Run analysis for all symbols once"""
        if not self.stock_data:
            self.fetch_all_data()
        
        self.analysis_results.clear()
        
        for symbol in self.symbols:
            try:
                if self.stock_data.get(symbol) is not None:
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
                    
                    self.analysis_results[symbol] = {
                        'symbol': symbol,
                        'score': total_score,
                        'technical': tech_score,
                        'fundamental': fund_score,
                        'sentiment': sent_score
                    }
            except Exception as e:
                logging.error(f"Error analyzing {symbol}: {e}")
                self.analysis_results[symbol] = None
        
        self.last_update = datetime.now()
    
    def get_analysis(self, symbol: str) -> dict:
        """Get analysis results for a symbol"""
        if not self.analysis_results or \
           (datetime.now() - self.last_update) > timedelta(hours=24):
            self.analyze_all_stocks()
        return self.analysis_results.get(symbol)
    
    def select_top_stocks(self, score_type: str = 'total', n: int = 5) -> List[dict]:
        """Select top N stocks based on specified score type"""
        if not self.analysis_results:
            self.analyze_all_stocks()
        
        valid_results = [r for r in self.analysis_results.values() if r]
        
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
            valid_results,                # List of stock analysis results 
            key=score_map[score_type],  # Lambda function for chosen score
            reverse=True           # Highest scores first
        )
        
        # Return top N stocks
        return sorted_results[:n]  # Slice first N results

if __name__ == '__main__':
    setup_logging()
    
    # Test strategy
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META']
    
    # symbols = [
    #     'AAPL',  'MSFT',  'GOOGL', 'AMZN',  'META',  'NVDA', 'TSLA',
    #     'INTC',  'AMD',   'CRM',   'ADBE',  'ORCL',  'CSCO', 'IBM',
    #     'QCOM',  'TXN',   'AVGO',  'ARM',   'PYPL',  'MU',   'UBER',
    #     'ASML', 'SHOP',  'NOW',   'SNOW',  'PLTR',  'NET',  'AMAT',
    # ]
    strategy = Strategy(symbols)
    
    # Get top stocks by different metrics
    print("\nTop Stocks by Total Score:")
    for stock in strategy.select_top_stocks('total', 5):
        print(f"{stock['symbol']}: {stock['score']:.2f}")
    
    print("\nTop Stocks by Technical Score:")
    for stock in strategy.select_top_stocks('technical', 5):
        print(f"{stock['symbol']}: {stock['technical']:.2f}")
        
    print("\nTop Stocks by Fundamental Score:")
    for stock in strategy.select_top_stocks('fundamental', 5):
        print(f"{stock['symbol']}: {stock['fundamental']:.2f}")
        
    print("\nTop Stocks by Sentiment Score:")
    for stock in strategy.select_top_stocks('sentiment', 5):
        print(f"{stock['symbol']}: {stock['sentiment']:.2f}")