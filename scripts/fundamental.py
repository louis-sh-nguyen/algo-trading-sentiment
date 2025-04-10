import yfinance as yf
import pandas as pd
import numpy as np
import logging

class FundamentalAnalyser:
    def __init__(self, symbol):
        self.symbol = symbol
        self.ticker = yf.Ticker(symbol)
        self.info = self.ticker.info
        
        # Default weights and benchmarks
        self.metric_weights = {
            'PE_Ratio': {'weight': -0.15, 'benchmark': 20.0},  # Lower is better
            'PB_Ratio': {'weight': -0.10, 'benchmark': 3.0},   # Lower is better
            'ROE': {'weight': 0.20, 'benchmark': 0.15},        # Higher is better
            'Profit_Margin': {'weight': 0.20, 'benchmark': 0.10}, # Higher is better
            'Current_Ratio': {'weight': 0.15, 'benchmark': 2.0},  # Higher is better
            'Debt_to_Equity': {'weight': -0.20, 'benchmark': 1.0}  # Lower is better
        }
        
        # Store the metrics
        self.metrics = {}
    
    def get_metrics(self):
        """Fetch fundamental metrics for the stock"""
        try:
            # Get P/E Ratio (try forwardPE first, then trailingPE)
            self.metrics['PE_Ratio'] = self.info.get('forwardPE', self.info.get('trailingPE', 0))
            
            # Get P/B Ratio
            self.metrics['PB_Ratio'] = self.info.get('priceToBook', 0)
            
            # Get Return on Equity
            self.metrics['ROE'] = self.info.get('returnOnEquity', 0)
            
            # Get Profit Margin
            self.metrics['Profit_Margin'] = self.info.get('profitMargins', 0)
            
            # Get Current Ratio
            self.metrics['Current_Ratio'] = self.info.get('currentRatio', 0)
            
            # Get Debt to Equity
            self.metrics['Debt_to_Equity'] = self.info.get('debtToEquity', 0) / 100 if self.info.get('debtToEquity') else 0
            
            return self.metrics
        
        except Exception as e:
            print(f"Error fetching metrics for {self.symbol}: {e}")
            return {}
    
    def score_metric(self, metric_name, value):
        """Score a single metric relative to its benchmark"""
        if value == 0 or value is None:
            return 50  # Neutral score for missing data
        
        weight = self.metric_weights[metric_name]['weight']
        benchmark = self.metric_weights[metric_name]['benchmark']
        
        if weight > 0:  # Higher is better
            if value >= benchmark * 2:
                return 100  # Double the benchmark or better gets full score
            elif value <= 0:
                return 0   # Negative values get zero
            else:
                return min(100, (value / benchmark) * 50 + 50)  # Scale from 50-100
        else:  # Lower is better (negative weight)
            if value <= benchmark / 2:
                return 100  # Half the benchmark or better gets full score
            elif value >= benchmark * 2:
                return 0   # Double the benchmark or worse gets zero
            else:
                return max(0, 100 - ((value / benchmark) * 50))  # Scale from 50-0
    
    def analyse(self):
        """Calculate an overall fundamental score for the stock"""
        if not self.metrics:
            self.get_metrics()
        
        total_score = 0
        total_weight = 0
        
        for metric, value in self.metrics.items():
            if metric in self.metric_weights:
                weight = abs(self.metric_weights[metric]['weight'])
                if weight > 0:  # Skip metrics with zero weight
                    metric_score = self.score_metric(metric, value)
                    total_score += metric_score * weight
                    total_weight += weight
        
        # Normalize the score
        if total_weight > 0:
            return round(total_score / total_weight, 1)
        else:
            return 50  # Default neutral score if no weights

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