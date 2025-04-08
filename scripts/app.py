import streamlit as st
import pandas as pd

def run_app():
    st.set_page_config(page_title="Stock Screener", layout="wide")
    
    # Title and description
    st.title("Stock Screener")
    st.markdown("Screen stocks based on fundamental metrics, momentum indicators, sentiment analysis, or a combination.")
    
    # Create tabs for different screening categories
    tab1, tab2, tab3, tab4 = st.tabs(["Fundamental", "Momentum", "Sentiment", "Combined"])
    
    with tab1:
        st.header("Fundamental Screening")
        
        st.subheader("Select Fundamental Metrics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            pe_ratio = st.slider("P/E Ratio", min_value=0, max_value=100, value=(0, 30))
            pb_ratio = st.slider("P/B Ratio", min_value=0.0, max_value=10.0, value=(0.0, 3.0), step=0.1)
            dividend_yield = st.slider("Dividend Yield (%)", min_value=0.0, max_value=10.0, value=(0.0, 5.0), step=0.1)
        
        with col2:
            market_cap = st.select_slider(
                "Market Cap", 
                options=["Nano Cap", "Micro Cap", "Small Cap", "Mid Cap", "Large Cap", "Mega Cap"],
                value=("Small Cap", "Large Cap")
            )
            sector = st.multiselect(
                "Sector",
                ["Technology", "Healthcare", "Financials", "Consumer Discretionary", "Energy", "Utilities", "Materials"]
            )
        
        if st.button("Screen Fundamentals"):
            st.info("Fundamental screening is a placeholder. Integration with data source needed.")
            # Placeholder data
            data = {
                'Symbol': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META'],
                'Name': ['Apple Inc.', 'Microsoft Corp', 'Alphabet Inc', 'Amazon.com Inc', 'Meta Platforms Inc'],
                'P/E': [28.5, 32.1, 25.8, 71.2, 29.5],
                'P/B': [35.1, 12.8, 5.9, 10.2, 6.1],
                'Div Yield': [0.57, 0.82, 0.0, 0.0, 0.0]
            }
            st.dataframe(pd.DataFrame(data))
    
    with tab2:
        st.header("Momentum Screening")
        
        st.subheader("Select Momentum Indicators")
        
        col1, col2 = st.columns(2)
        
        with col1:
            rsi_range = st.slider("RSI (14)", min_value=0, max_value=100, value=(30, 70))
            price_change = st.slider("Price Change (%)", min_value=-50, max_value=100, value=(0, 20))
        
        with col2:
            time_period = st.radio("Time Period", ["1 Week", "1 Month", "3 Months", "6 Months", "1 Year"])
            volume_increase = st.checkbox("Above Average Volume")
        
        if st.button("Screen Momentum"):
            st.info("Momentum screening is a placeholder. Integration with data source needed.")
            # Placeholder data
            data = {
                'Symbol': ['NVDA', 'AMD', 'TSLA', 'PLTR', 'COIN'],
                'Name': ['NVIDIA Corp', 'Advanced Micro Devices', 'Tesla Inc', 'Palantir', 'Coinbase'],
                'RSI': [68.2, 52.1, 45.8, 62.7, 71.5],
                'Price Change %': [15.2, 8.9, -2.3, 10.5, 25.7],
                'Volume Ratio': [1.5, 1.2, 0.9, 2.1, 3.2]
            }
            st.dataframe(pd.DataFrame(data))
    
    with tab3:
        st.header("Sentiment Screening")
        
        st.subheader("Select Sentiment Sources")
        
        news_sentiment = st.checkbox("News Sentiment", value=True)
        social_media = st.checkbox("Social Media", value=True)
        analyst_ratings = st.checkbox("Analyst Ratings", value=True)
        
        sentiment_threshold = st.select_slider(
            "Sentiment Threshold",
            options=["Very Negative", "Negative", "Neutral", "Positive", "Very Positive"],
            value="Positive"
        )
        
        time_range = st.radio("Time Range", ["Last 24 Hours", "Last Week", "Last Month"])
        
        if st.button("Screen Sentiment"):
            st.info("Sentiment screening is a placeholder. Integration with sentiment analysis needed.")
            # Placeholder data
            data = {
                'Symbol': ['AAPL', 'MSFT', 'NFLX', 'SBUX', 'DIS'],
                'Name': ['Apple Inc.', 'Microsoft Corp', 'Netflix Inc', 'Starbucks Corp', 'Walt Disney Co'],
                'News Sentiment': ['Positive', 'Very Positive', 'Neutral', 'Negative', 'Positive'],
                'Social Sentiment': ['Neutral', 'Positive', 'Very Positive', 'Neutral', 'Negative'],
                'Analyst Rating': ['Buy', 'Strong Buy', 'Hold', 'Sell', 'Buy']
            }
            st.dataframe(pd.DataFrame(data))
    
    with tab4:
        st.header("Combined Screening")
        
        st.subheader("Select Screening Weights")
        
        fundamental_weight = st.slider("Fundamental Weight", min_value=0, max_value=100, value=33)
        momentum_weight = st.slider("Momentum Weight", min_value=0, max_value=100, value=33)
        sentiment_weight = st.slider("Sentiment Weight", min_value=0, max_value=100, value=34)
        
        # Adjust for 100% total
        total = fundamental_weight + momentum_weight + sentiment_weight
        if total != 100:
            st.warning(f"Weights sum to {total}%. Consider adjusting to total 100%.")
        
        st.subheader("Select Key Metrics from Each Category")
        
        metrics = st.multiselect(
            "Select Metrics",
            [
                "P/E Ratio", "Dividend Yield", "Market Cap", 
                "RSI", "Price Change", "Volume Trend", 
                "News Sentiment", "Social Media Buzz", "Analyst Recommendations"
            ],
            ["P/E Ratio", "RSI", "News Sentiment"]
        )
        
        if st.button("Run Combined Screen"):
            st.info("Combined screening is a placeholder. Integration needed.")
            # Placeholder data
            data = {
                'Symbol': ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'TSLA'],
                'Name': ['Apple Inc.', 'Microsoft Corp', 'Alphabet Inc', 'NVIDIA Corp', 'Tesla Inc'],
                'Combined Score': [87, 92, 78, 85, 72],
                'Fundamental': [90, 85, 82, 75, 65],
                'Momentum': [75, 90, 65, 95, 85],
                'Sentiment': [95, 95, 85, 80, 65]
            }
            st.dataframe(pd.DataFrame(data))

    # Footer
    st.markdown("---")
    st.caption("Stock Screener App | Data for educational purposes only")

if __name__ == "__main__":
    run_app()