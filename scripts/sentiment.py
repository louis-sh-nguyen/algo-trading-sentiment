import yfinance as yf
from gnews import GNews
from datetime import datetime, timedelta
import logging
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import numpy as np
from abc import ABC, abstractmethod
from typing import List, Dict

class NewsSource(ABC):
    @abstractmethod
    def get_news(self, symbol: str, days: int = 7) -> List[Dict]:
        """Return list of news items with title and timestamp"""
        pass

class YFinanceNews(NewsSource):
    def get_news(self, symbol: str, days: int = 7) -> List[Dict]:
        def datetime_from_pubDate(content: str) -> datetime:
            date_str = content.split('T')[0]
            time_str = content.split('T')[1].split('Z')[0]
            date_time_str = f"{date_str} {time_str}"
            date_time = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')
            return date_time
        
        try:
            stock = yf.Ticker(symbol)
            news = stock.news
            if not news:
                return []
            
            cutoff = datetime.now() - timedelta(days=days)
            
            results = [{
                'title': n['content']['title'],
                'timestamp': datetime_from_pubDate(n['content']['pubDate']),
                'source': 'yfinance'
            } for n in news 
            if datetime_from_pubDate(n['content']['pubDate']) > cutoff]
            
            return results
        except Exception as e:
            logging.error(f"YFinance error for {symbol}: {e}")
            return []

class GNewsSource(NewsSource):
    def __init__(self):
        self.gnews = GNews(language='en', country='US', period='7d')
    
    def get_news(self, symbol: str, days: int = 7) -> List[Dict]:
        try:
            news = self.gnews.get_news(f"{symbol} stock")
            return [{
                'title': n['title'],
                'timestamp': datetime.now(),  # GNews doesn't provide timestamps
                'source': 'gnews'
            } for n in news[:10]]  # Limit to top 10 news items
        except Exception as e:
            logging.error(f"GNews error for {symbol}: {e}")
            return []

class SentimentAnalyser:
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.news_sources = {
            'yfinance': {'source': YFinanceNews(), 'weight': 0.6},
            'gnews': {'source': GNewsSource(), 'weight': 0.4}
        }
        self.tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
        self.model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
    
    def get_sentiment_score(self, text: str) -> float:
        try:
            inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True)
            outputs = self.model(**inputs)
            probabilities = torch.nn.functional.softmax(outputs.logits, dim=1)
            return (probabilities[0][0] * 0 + 
                   probabilities[0][1] * 50 + 
                   probabilities[0][2] * 100).item()
        except Exception as e:
            logging.error(f"Sentiment analysis error: {e}")
            return 50
    
    def analyse(self) -> float:
        source_scores = {}
        
        for source_name, config in self.news_sources.items():
            news_items = config['source'].get_news(self.symbol)
            if news_items:
                scores = [self.get_sentiment_score(item['title']) for item in news_items]
                source_scores[source_name] = {
                    'score': np.mean(scores),
                    'weight': config['weight']
                }
        
        if not source_scores:
            return 50
        
        weighted_score = sum(
            source['score'] * source['weight']
            for source in source_scores.values()
        ) / sum(source['weight'] for source in source_scores.values())
        
        return weighted_score

if __name__ == '__main__':
    # logging.basicConfig(level=logging.INFO)
    symbol = 'AAPL'
    analyser = SentimentAnalyser(symbol)
    score = analyser.analyse()
    print(f"Combined sentiment score for {symbol}: {score:.2f}")