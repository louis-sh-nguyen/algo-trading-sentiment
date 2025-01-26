import yfinance as yf
from typing import Dict

class FundamentalAnalyser:
    def __init__(self, symbol: str):
        self.stock = yf.Ticker(symbol)
        
    def get_metrics(self) -> Dict:
        """Get key fundamental metrics"""
        info = self.stock.info
        return {
            'PE_Ratio': info.get('trailingPE', 0),
            'PB_Ratio': info.get('priceToBook', 0),
            'Profit_Margin': info.get('profitMargins', 0),
            'ROE': info.get('returnOnEquity', 0),
            'Current_Ratio': info.get('currentRatio', 0),
            'Debt_to_Equity': info.get('debtToEquity', 0)
        }
    
    def analyse(self) -> float:
        """Score fundamental strength (0-100)"""
        metrics = self.get_metrics()
        score = 0
        weights = {'PE_Ratio': -0.2, 'Profit_Margin': 0.3, 'ROE': 0.3}
        
        for metric, weight in weights.items():
            if metrics.get(metric):
                score += metrics[metric] * weight
        
        return max(0, min(100, score * 10))

if __name__ == '__main__':
    # Example usage
    symbol = 'AAPL'
    analyser = FundamentalAnalyser(symbol)
    
    # Get and display metrics
    metrics = analyser.get_metrics()
    print(f"\nFundamental metrics for {symbol}:")
    for metric, value in metrics.items():
        print(f"{metric}: {value:.2f}")
    
    # Calculate and display fundamental score
    score = analyser.analyse()
    print(f"\nFundamental score: {score:.2f}")