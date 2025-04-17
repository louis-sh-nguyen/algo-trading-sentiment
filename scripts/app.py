import streamlit as st
import pandas as pd
import yfinance as yf

from fundamental import FundamentalAnalyser

def run_app():
    st.set_page_config(page_title="Stock Screener", layout="wide")
    
    # Title and description
    st.title("Stock Screener 101")
    st.markdown("Screen stocks based on fundamental metrics, momentum indicators, sentiment analysis, or a combination.")
    
    # Create tabs for different screening categories
    tab1, tab2, tab3, tab4 = st.tabs(["Fundamental", "Momentum", "Sentiment", "Combined"])
    
    with tab1:
        st.header("Fundamental Screening")
        
        # Input for stock symbols with S&P 500 option
        st.subheader("Enter Stock Symbols")
        
        # Initialize session state for symbols if it doesn't exist
        if 'symbol_list' not in st.session_state:
            st.session_state.symbol_list = "AAPL, MSFT, GOOGL, AMZN, META"
        
        # Add Load S&P 500 button right after the subheader
        sp500_clicked = st.button("Load S&P 500", help="Load top S&P 500 stocks")
        
        # If SP500 button clicked, fetch SP500 tickers
        if sp500_clicked:
            try:
                from utils import get_sp500_tickers
                sp500_tickers = get_sp500_tickers()
                # Take first 30 tickers for performance
                sp500_sample = sp500_tickers[:30]
                st.session_state.symbol_list = ", ".join(sp500_sample)
            except Exception as e:
                st.error(f"Error loading S&P 500 tickers: {str(e)}")
        
        # Symbol input area - now using full width since button is above
        symbols_input = st.text_area(
            "Enter stock symbols (comma or space separated)",
            value=st.session_state.symbol_list,
            height=100,
            key="symbols_text_area"
        )
        
        # Update session state when user changes the input
        st.session_state.symbol_list = symbols_input
        
        # Parse symbols and remove duplicates
        raw_symbols = [s.strip().upper() for s in st.session_state.symbol_list.replace(',', ' ').split() if s.strip()]
        symbols = list(dict.fromkeys(raw_symbols))  # Remove duplicates while preserving order
        
        # Show a message if duplicates were found and removed
        if len(raw_symbols) != len(symbols):
            st.info(f"Removed {len(raw_symbols) - len(symbols)} duplicate ticker(s).")
        
        # Add methodology explanation in expandable section
        with st.expander("Screening Methodology"):
            st.markdown("""
            ### How It Works
            
            Stocks are scored on a 0-100 scale based on their fundamental metrics:
            
            **Valuation** (lower is better)
            - P/E Ratio: Price relative to earnings
            - P/B Ratio: Price relative to book value
            
            **Profitability** (higher is better)
            - ROE: How efficiently equity generates profit
            - Profit Margin: Percentage of revenue converted to profit
            
            **Financial Health**
            - Current Ratio: Short-term solvency (higher is better)
            - Debt/Equity: Leverage level (lower is better)
            
            Each metric is scored against its benchmark and weighted according to your settings. Value investors typically emphasize P/E and P/B ratios, while growth investors focus more on profitability metrics.
            """)
            
        # Add metric weights customization section
        st.subheader("Customize Metric Weights and Benchmarks")
        st.markdown("Adjust the importance and benchmark values for each fundamental metric.")
        
        # Store weights in a dictionary
        metric_weights = {}
        # Store benchmarks in a dictionary
        metric_benchmarks = {}
        
        # Valuation Metrics Section
        st.markdown("### Valuation Metrics (lower is better)")
        
        # P/E Ratio (negative weight)
        st.markdown("#### P/E Ratio")
        pe_cols = st.columns([1, 4])
        with pe_cols[0]:
            metric_benchmarks['PE_Ratio'] = st.number_input("Benchmark", min_value=1.0, 
                                                max_value=100.0, value=20.0, 
                                                step=1.0, format="%.1f")
        with pe_cols[1]:
            metric_weights['PE_Ratio'] = abs(st.slider("Weight", min_value=0.0, max_value=1.0, 
                                            value=0.15, step=0.05, format="%.2f")) * -1
        
        # P/B Ratio (negative weight)
        st.markdown("#### P/B Ratio")
        pb_cols = st.columns([1, 4])
        with pb_cols[0]:
            metric_benchmarks['PB_Ratio'] = st.number_input("Benchmark", min_value=0.1, 
                                                max_value=20.0, value=3.0, 
                                                step=0.1, format="%.1f", key="pb_benchmark")
        with pb_cols[1]:
            metric_weights['PB_Ratio'] = abs(st.slider("Weight", min_value=0.0, max_value=1.0, 
                                            value=0.10, step=0.05, format="%.2f", key="pb_weight")) * -1
        
        # Profitability Metrics Section
        st.markdown("### Profitability Metrics (higher is better)")
        
        # ROE (positive weight)
        st.markdown("#### Return on Equity")
        roe_cols = st.columns([1, 4])
        with roe_cols[0]:
            metric_benchmarks['ROE'] = st.number_input("Benchmark (%)", min_value=1.0, 
                                            max_value=50.0, value=15.0, 
                                            step=1.0, format="%.1f") / 100.0
        with roe_cols[1]:
            metric_weights['ROE'] = st.slider("Weight", min_value=0.0, max_value=1.0, 
                                        value=0.20, step=0.05, format="%.2f")
        
        # Profit Margin (positive weight)
        st.markdown("#### Profit Margin")
        pm_cols = st.columns([1, 4])
        with pm_cols[0]:
            metric_benchmarks['Profit_Margin'] = st.number_input("Benchmark (%)", min_value=1.0, 
                                                    max_value=50.0, value=10.0, 
                                                    step=1.0, format="%.1f", key="pm_benchmark") / 100.0
        with pm_cols[1]:
            metric_weights['Profit_Margin'] = st.slider("Weight", min_value=0.0, max_value=1.0, 
                                                value=0.20, step=0.05, format="%.2f", key="pm_weight")
        
        # Financial Health Metrics Section
        st.markdown("### Financial Health Metrics")
        
        # Current Ratio (positive weight)
        st.markdown("#### Current Ratio (higher is better)")
        cr_cols = st.columns([1, 4])
        with cr_cols[0]:
            metric_benchmarks['Current_Ratio'] = st.number_input("Benchmark", min_value=0.5, 
                                                    max_value=5.0, value=2.0, 
                                                    step=0.1, format="%.1f", key="cr_benchmark")
        with cr_cols[1]:
            metric_weights['Current_Ratio'] = st.slider("Weight", min_value=0.0, max_value=1.0, 
                                                value=0.15, step=0.05, format="%.2f", key="cr_weight")
        
        # Debt/Equity Ratio (negative weight)
        st.markdown("#### Debt/Equity Ratio (lower is better)")
        de_cols = st.columns([1, 4])
        with de_cols[0]:
            metric_benchmarks['Debt_to_Equity'] = st.number_input("Benchmark", min_value=0.1, 
                                                    max_value=5.0, value=1.0, 
                                                    step=0.1, format="%.1f", key="de_benchmark")
        with de_cols[1]:
            metric_weights['Debt_to_Equity'] = abs(st.slider("Weight", min_value=0.0, max_value=1.0, 
                                                    value=0.20, step=0.05, format="%.2f", key="de_weight")) * -1
        
        # Weight settings section
        st.markdown("### Summary")
        
        # Calculate and show total weight
        total_weight = sum(abs(w) for w in metric_weights.values())
        st.metric("Total Weight", f"{total_weight:.2f}")
        
        # Warning if total weight is not 1.0
        if abs(total_weight - 1.0) > 0.01:
            st.info(f"Note: Total weight ({total_weight:.2f}) will be automatically normalized when calculating scores.")
        
        st.markdown("---")
        
        # Screen button
        if st.button("Screen Fundamentals"):
            with st.spinner("Analysing fundamental data..."):
                # Store results in a list
                results = []
                invalid_tickers = []
                
                # Create a progress bar
                progress_bar = st.progress(0)
                
                for i, symbol in enumerate(symbols):
                    try:
                        # Update progress
                        progress = (i + 1) / len(symbols)
                        progress_bar.progress(progress)
                        
                        # Validate ticker first
                        ticker = yf.Ticker(symbol)
                        info = ticker.info
                        
                        # Check if we got a valid response with basic info
                        if not info.get('longName') and not info.get('marketCap'):
                            invalid_tickers.append(symbol)
                            continue
                        
                        # Create analyzer and get metrics and score
                        analyzer = FundamentalAnalyser(symbol)
                        
                        # Override default weights with user's weights
                        analyzer.metric_weights = {
                            'PE_Ratio': {'weight': metric_weights['PE_Ratio'], 'benchmark': metric_benchmarks['PE_Ratio']},
                            'PB_Ratio': {'weight': metric_weights['PB_Ratio'], 'benchmark': metric_benchmarks['PB_Ratio']},
                            'ROE': {'weight': metric_weights['ROE'], 'benchmark': metric_benchmarks['ROE']},
                            'Profit_Margin': {'weight': metric_weights['Profit_Margin'], 'benchmark': metric_benchmarks['Profit_Margin']},
                            'Current_Ratio': {'weight': metric_weights['Current_Ratio'], 'benchmark': metric_benchmarks['Current_Ratio']},
                            'Debt_to_Equity': {'weight': metric_weights['Debt_to_Equity'], 'benchmark': metric_benchmarks['Debt_to_Equity']}
                        }
                        
                        metrics = analyzer.get_metrics()
                        score = analyzer.analyse()
                        
                        # Add to results - include all stocks even with minimal data
                        results.append({
                            'Symbol': symbol,
                            'Name': info.get('longName', symbol),
                            'Sector': info.get('sector', 'N/A'),
                            'P/E': metrics.get('PE_Ratio', 0),
                            'P/B': metrics.get('PB_Ratio', 0),
                            'ROE': metrics.get('ROE', 0) * 100,  # Convert to percentage
                            'Profit Margin': metrics.get('Profit_Margin', 0) * 100,  # Convert to percentage
                            'Current Ratio': metrics.get('Current_Ratio', 0),
                            'Debt/Equity': metrics.get('Debt_to_Equity', 0),
                            'Score': score
                        })
                    except Exception as e:
                        invalid_tickers.append(symbol)
                        st.error(f"Error analyzing {symbol}: {str(e)}")
                
                # Clear progress
                progress_bar.empty()
                
                # Show invalid tickers if any
                if invalid_tickers:
                    st.warning(f"Could not analyze the following tickers (may be invalid or missing data): {', '.join(invalid_tickers)}")
                
                if results:
                    # Convert to DataFrame
                    df = pd.DataFrame(results)
                    
                    # Sort by score (descending)
                    df = df.sort_values('Score', ascending=False)
                    
                    # Display results
                    st.subheader("Fundamental Analysis Results")
                    st.dataframe(
                        df, 
                        column_config={
                            'Symbol': st.column_config.TextColumn('Symbol'),
                            'Name': st.column_config.TextColumn('Company'),
                            'Sector': st.column_config.TextColumn('Sector'),
                            'P/E': st.column_config.NumberColumn('P/E', format="%.2f"),
                            'P/B': st.column_config.NumberColumn('P/B', format="%.2f"),
                            'ROE': st.column_config.NumberColumn('ROE (%)', format="%.2f%%"),
                            'Profit Margin': st.column_config.NumberColumn('Margin (%)', format="%.2f%%"),
                            'Current Ratio': st.column_config.NumberColumn('Current Ratio', format="%.2f"),
                            'Debt/Equity': st.column_config.NumberColumn('D/E', format="%.2f"),
                            'Score': st.column_config.ProgressColumn('Fund. Score', format="%.1f", min_value=0, max_value=100)
                        },
                        hide_index=True,
                        use_container_width=True
                    )
                    
                    # Show a bar chart of top stocks by score (already sorted)
                    st.subheader("Top 10 Stocks by Fundamental Score")
                    
                    # Get top 10 stocks for plotting
                    plot_df = df.head(10).copy()
                    
                    # Create a custom chart to ensure correct ordering
                    import altair as alt
                    
                    # Create a chart with explicit ordering
                    chart = alt.Chart(plot_df).mark_bar().encode(
                        x=alt.X('Symbol:N', sort=None),  # No sorting, plot_df already sorted
                        y='Score:Q',
                        color=alt.value('#0068C9')
                    ).properties(
                        height=400
                    )
                    
                    st.altair_chart(chart, use_container_width=True)
                else:
                    st.warning("No valid results found. Try different symbols.")
    
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
    # Create a professional-looking footer
    footer_container = st.container()
    with footer_container:
        st.markdown("---")
        st.caption("Stock Screener App | [Source Code](https://github.com/sup3rlazybaby/algo-trading-sentiment) | For informational purposes only. Not financial advice.")
        st.caption("Created by **Louis Nguyen** | [GitHub](https://github.com/sup3rlazybaby) | [LinkedIn](https://www.linkedin.com/in/louis-sh-nguyen/) | [Email](mailto:louis.sh.nguyen@gmail.com)")

if __name__ == "__main__":
    run_app()