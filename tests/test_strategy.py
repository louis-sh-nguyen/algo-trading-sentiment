import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from datetime import datetime

# Adjust import based on your project structure
from scripts.strategy import Strategy

@pytest.fixture
def mock_strategy():
    """Fixture to create a Strategy instance with mocked analysis results."""
    symbols = ['AAPL', 'MSFT', 'GOOG']
    strategy = Strategy(symbols)

    # Mock analysis results directly to test sorting logic
    strategy.analysis_results = {
        'AAPL': {
            'symbol': 'AAPL',
            'score': 0.7,
            'technical': 0.8,
            'fundamental': 0.6,
            'sentiment': 0.7
        },
        'MSFT': {
            'symbol': 'MSFT',
            'score': 0.8,
            'technical': 0.7,
            'fundamental': 0.9,
            'sentiment': 0.8
        },
        'GOOG': {
            'symbol': 'GOOG',
            'score': 0.6,
            'technical': 0.9,
            'fundamental': 0.5,
            'sentiment': 0.4
        },
        'FAIL': None # Simulate a failed analysis
    }
    strategy.last_update = datetime.now()
    return strategy

def test_select_top_stocks_total_score(mock_strategy):
    """Test selecting top stocks based on the total score."""
    top_stocks = mock_strategy.select_top_stocks(score_type='total', n=2)
    assert len(top_stocks) == 2
    assert top_stocks[0]['symbol'] == 'MSFT' # Highest total score
    assert top_stocks[1]['symbol'] == 'AAPL'

def test_select_top_stocks_technical_score(mock_strategy):
    """Test selecting top stocks based on the technical score."""
    top_stocks = mock_strategy.select_top_stocks(score_type='technical', n=2)
    assert len(top_stocks) == 2
    assert top_stocks[0]['symbol'] == 'GOOG' # Highest technical score
    assert top_stocks[1]['symbol'] == 'AAPL'

def test_select_top_stocks_fundamental_score(mock_strategy):
    """Test selecting top stocks based on the fundamental score."""
    top_stocks = mock_strategy.select_top_stocks(score_type='fundamental', n=2)
    assert len(top_stocks) == 2
    assert top_stocks[0]['symbol'] == 'MSFT' # Highest fundamental score
    assert top_stocks[1]['symbol'] == 'AAPL'

def test_select_top_stocks_sentiment_score(mock_strategy):
    """Test selecting top stocks based on the sentiment score."""
    top_stocks = mock_strategy.select_top_stocks(score_type='sentiment', n=2)
    assert len(top_stocks) == 2
    assert top_stocks[0]['symbol'] == 'MSFT' # Highest sentiment score
    assert top_stocks[1]['symbol'] == 'AAPL'

def test_select_top_stocks_invalid_score_type(mock_strategy):
    """Test selecting top stocks with an invalid score type."""
    with pytest.raises(ValueError, match="Invalid score type: invalid"):
        mock_strategy.select_top_stocks(score_type='invalid', n=2)

def test_select_top_stocks_more_than_available(mock_strategy):
    """Test selecting more stocks than available valid results."""
    top_stocks = mock_strategy.select_top_stocks(score_type='total', n=5)
    # Should return all valid stocks (3 in this case), sorted
    assert len(top_stocks) == 3
    assert top_stocks[0]['symbol'] == 'MSFT'
    assert top_stocks[1]['symbol'] == 'AAPL'
    assert top_stocks[2]['symbol'] == 'GOOG'

# Create mocks 
@patch('scripts.strategy.fetch_data')   # arg 4
@patch('scripts.strategy.TechnicalAnalyser')    # arg 3
@patch('scripts.strategy.FundamentalAnalyser')  # arg 2
@patch('scripts.strategy.SentimentAnalyser')    # arg 1
def test_analyse_all_stocks_basic(mock_sentiment, mock_fundamental, mock_technical, mock_fetch):    # order matters
    """Basic test for analyse_all_stocks, mocking dependencies."""
    symbols = ['TEST']
    strategy = Strategy(symbols)

    # Mock fetch_data
    mock_fetch.return_value = pd.DataFrame({'Close': [100, 101]})

    # Mock analysers' analyse methods
    mock_tech_instance = MagicMock()
    mock_tech_instance.analyse.return_value = 0.75
    mock_technical.return_value = mock_tech_instance

    mock_fund_instance = MagicMock()
    mock_fund_instance.analyse.return_value = 0.65
    mock_fundamental.return_value = mock_fund_instance

    mock_sent_instance = MagicMock()
    mock_sent_instance.analyse.return_value = 0.55
    mock_sentiment.return_value = mock_sent_instance

    strategy.analyse_all_stocks()

    mock_fetch.assert_called_once_with('TEST')
    mock_technical.assert_called_once_with(mock_fetch.return_value)
    mock_fundamental.assert_called_once_with('TEST')
    mock_sentiment.assert_called_once_with('TEST')

    assert 'TEST' in strategy.analysis_results
    result = strategy.analysis_results['TEST']
    assert result is not None
    assert result['symbol'] == 'TEST'
    assert result['technical'] == 0.75
    assert result['fundamental'] == 0.65
    assert result['sentiment'] == 0.55
    # Check calculated total score: (0.75 * 0.4) + (0.65 * 0.4) + (0.55 * 0.2) = 0.3 + 0.26 + 0.11 = 0.67
    assert pytest.approx(result['score']) == 0.67
