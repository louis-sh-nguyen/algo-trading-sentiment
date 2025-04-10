import logging
from pathlib import Path
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, List
import time
from functools import wraps
import requests
import bs4 as bs

def setup_logging():
    """Configure logging settings"""
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        filename=log_dir / f'trading_{datetime.now().strftime("%Y%m%d")}.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def retry(func, retries=3, delay=2):
    """Retry decorator with exponential backoff"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        for attempt in range(retries):
            try:
                return func(*args, **kwargs)
            except yf.YFRateLimitError as e:
                logging.error(f"Attempt {attempt + 1} failed: {e}")
                if attempt == retries - 1:
                    raise  # Re-raise exception on last attempt
                time.sleep(delay * (attempt + 1))  # Exponential backoff
            except Exception as e:
                logging.error(f"Attempt {attempt + 1} failed with non-rate-limit error: {e}")
                raise # Re-raise immediately for non-rate-limit errors
    return wrapper

@retry
def fetch_data(
    symbol: str, 
    start_date: Optional[str] = None, 
    end_date: Optional[str] = None,
    period: int = 200
) -> pd.DataFrame:
    """
    Fetch stock data using yfinance.
    
    Args:
        symbol: Stock ticker symbol
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        period: Number of days if start/end not specified
    
    Returns:
        DataFrame with OHLCV data
    """
    try:
        if start_date and end_date:
            df = yf.download(symbol, start=start_date, end=end_date, progress=False)
        else:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period)
            df = yf.download(symbol, start=start_date, end=end_date, progress=False)
            
        if df.empty:
            raise ValueError(f"No data found for {symbol}")
        
        # Convert multi-index columns to single level by dropping 2nd level (e.g. ('Close', 'AAPL') → 'Close')
        df.columns = df.columns.droplevel(1)
        
        return df
        
    except Exception as e:
        logging.error(f"Error fetching data for {symbol}: {e}")
        raise

def validate_ticker(symbol: str) -> bool:
    """Validate if ticker symbol exists"""
    try:
        ticker = yf.Ticker(symbol)
        if ticker.info:
            return True
        return False
    except:
        return False

def calculate_returns(prices: pd.Series) -> pd.Series:
    """Calculate percentage returns from price series"""
    return prices.pct_change()

def get_sp500_tickers() -> List[str]:
    """
    Scrape Wikipedia to get the current list of S&P 500 companies.
    
    Returns:
        List of S&P 500 ticker symbols
    """
    try:
        logging.info("Fetching S&P 500 tickers from Wikipedia")
        resp = requests.get('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
        soup = bs.BeautifulSoup(resp.text, 'html.parser')
        table = soup.find('table', {'class': 'wikitable sortable'})
        
        tickers = []
        for row in table.findAll('tr')[1:]:
            ticker = row.findAll('td')[0].text.strip()
            ticker = ticker.replace('.', '-')  # Replace dots with hyphens for Yahoo Finance compatibility
            tickers.append(ticker)
        
        logging.info(f"Successfully fetched {len(tickers)} S&P 500 tickers")
        return tickers
    except Exception as e:
        logging.error(f"Error fetching S&P 500 tickers: {e}")
        # Return a list of major tickers as a fallback
        fallback_tickers = ["AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "META", "GOOG", "TSLA", 
                           "BRK-B", "UNH", "JPM", "XOM", "LLY", "AVGO", "V", "PG", "MA", "HD", "COST", "MRK"]
        logging.info(f"Using fallback list of {len(fallback_tickers)} major tickers")
        return fallback_tickers

if __name__ == '__main__':
    # Test utilities
    setup_logging()
    
    # Test data fetching
    symbol = 'AAPL'
    try:
        if validate_ticker(symbol):
            data = fetch_data(symbol)
            print(f"\nFetched {len(data)} days of data for {symbol}")
            print("\nLast 5 days:")
            print(data.tail())
            
            returns = calculate_returns(data['Close'])
            print(returns)
            print(f"\nMean daily return: {returns.mean().item():.4f}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test S&P 500 ticker retrieval
    try:
        sp500 = get_sp500_tickers()
        print(f"\nRetrieved {len(sp500)} S&P 500 tickers")
        print(f"First 10 tickers: {', '.join(sp500[:10])}")
    except Exception as e:
        print(f"Error fetching S&P 500 tickers: {e}")