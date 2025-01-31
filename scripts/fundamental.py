import yfinance as yf
from typing import Dict
import logging

class FundamentalAnalyser:
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.stock = yf.Ticker(symbol)
        self.metric_weights = {
            # Valuation (lower is better)
            'PE_Ratio': {'weight': -0.15, 'benchmark': 20},
            'PB_Ratio': {'weight': -0.10, 'benchmark': 3},
            
            # Profitability (higher is better)
            'ROE': {'weight': 0.20, 'benchmark': 0.15},
            'Profit_Margin': {'weight': 0.20, 'benchmark': 0.10},
            
            # Financial Health (higher is better)
            'Current_Ratio': {'weight': 0.15, 'benchmark': 1.5},
            'Debt_to_Equity': {'weight': -0.20, 'benchmark': 1.5}
        }
    
    def get_metrics(self) -> Dict:
        """Get key fundamental metrics"""
        info = self.stock.info
        return {
            'PE_Ratio': info.get('trailingPE', 0),
            'PB_Ratio': info.get('priceToBook', 0),
            'ROE': info.get('returnOnEquity', 0),
            'Profit_Margin': info.get('profitMargins', 0),
            'Current_Ratio': info.get('currentRatio', 0),
            'Debt_to_Equity': info.get('debtToEquity', 0)
        }
    
    def calculate_metric_score(self, metric: str, value: float) -> float:
        """Calculate score for individual metric"""
        if value <= 0:
            return 50  # Neutral score for invalid values
            
        config = self.metric_weights[metric]
        benchmark = config['benchmark']
        
        # Calculate relative score
        if config['weight'] > 0:  # Higher is better
            score = (value / benchmark) * 100
        else:  # Lower is better
            score = (benchmark / value) * 100
            
        return max(0, min(100, score))
    
    def analyse(self) -> float:
        """Calculate fundamental score (0-100)"""
        try:
            metrics = self.get_metrics()
            scores = {}
            total_weight = 0
            
            for metric, value in metrics.items():
                if metric in self.metric_weights and value > 0:
                    score = self.calculate_metric_score(metric, value)
                    weight = abs(self.metric_weights[metric]['weight'])
                    scores[metric] = score * weight
                    total_weight += weight
            
            if total_weight == 0:
                return 50
                
            final_score = sum(scores.values()) / total_weight
            return max(0, min(100, final_score))
            
        except Exception as e:
            logging.error(f"Error in fundamental analysis: {e}")
            return 50

if __name__ == '__main__':
    symbol = 'AAPL'
    analyser = FundamentalAnalyser(symbol)
    metrics = analyser.get_metrics()
    score = analyser.analyse()
    
    print(f"\nFundamental Analysis for {symbol}")
    print("\nMetrics:")
    for metric, value in metrics.items():
        print(f"{metric}: {value:.2f}")
    print(f"\nFinal Score: {score:.2f}")