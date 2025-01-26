from utils import setup_logging, fetch_data
from technical import TechnicalAnalyser
from fundamental import FundamentalAnalyser
from sentiment import SentimentAnalyser
import logging

class Strategy:
    def __init__(self, symbols: list):
        self.symbols = symbols
    
    def analyse_stock(self, symbol: str) -> dict:
        try:
            data = fetch_data(symbol)
            
            tech = TechnicalAnalyser(data)
            tech.calculate_indicators()
            tech_signals = tech.get_signals()
            
            fund = FundamentalAnalyser(symbol)
            fund_score = fund.analyse()
            
            # sent = SentimentAnalyser(symbol)
            # sent_score = sent.analyse()
            sent_score = 50  # Placeholder
            
            total_score = (
                sum(tech_signals.values()) * 25 +
                fund_score * 0.4 +
                sent_score * 0.2
            )
            
            return {
                'symbol': symbol,
                'score': total_score,
                'technical': tech_signals,
                'fundamental': fund_score,
                'sentiment': sent_score
            }
        except Exception as e:
            logging.error(f"Error analyzing {symbol}: {e}")
            return None
        
if __name__ == '__main__':
    # setup_logging()
    strategy = Strategy(['AAPL', 'MSFT', 'GOOGL'])
    for symbol in strategy.symbols:
        result = strategy.analyse_stock(symbol)
        print(f'Analysis for {symbol}: {result}')
        # if result:
        #     logging.info(f"Analysis for {symbol}: {result}")