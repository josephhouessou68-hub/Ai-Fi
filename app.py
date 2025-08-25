import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
from langgraph_workflow import run_trading_analysis
from langsmith_integration import LangSmithTracker
from config import Config
import json
# from state_inspector import display_state_dashboard  # Removed due to circular import

# Enable caching for better performance
st.cache_data.clear()  # Clear cache on restart

# Page configuration
st.set_page_config(
    page_title="LangChain Trading Analysis",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Performance settings
if 'analysis_cache' not in st.session_state:
    st.session_state.analysis_cache = {}
    
# Add performance mode toggle
FAST_MODE = st.sidebar.checkbox("⚡ Fast Mode (Basic Analysis)", value=False)

# Add ultra fast mode link
st.sidebar.markdown("---")
st.sidebar.markdown("### 🚀 **Speed Options**")
if st.sidebar.button("⚡ **ULTRA FAST APP**", type="primary"):
    st.sidebar.markdown("**Opening Ultra Fast App...**")
    st.sidebar.markdown("[Click here if it doesn't open](http://localhost:8512)")
    # Note: Will start the ultra fast app below

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-status {
        color: #28a745;
        font-weight: bold;
    }
    .error-status {
        color: #dc3545;
        font-weight: bold;
    }
    .info-box {
        background-color: #e7f3ff;
        border: 1px solid #b3d9ff;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300)  # Cache for 5 minutes
def cached_trading_analysis(symbol: str) -> dict:
    """Cached version of trading analysis to improve performance"""
    return run_trading_analysis(symbol)

@st.cache_data(ttl=60)  # Cache for 1 minute
def get_quick_stock_data(symbol: str) -> dict:
    """Get just basic stock data quickly"""
    from api_clients import StockAPIClient
    client = StockAPIClient()
    return client.get_stock_info_yahoo(symbol)

def main():
    # Header
    st.markdown('<h1 class="main-header">📈 LangChain Trading Analysis</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 Configuration")
        
        # API Keys status
        st.subheader("API Status")
        openai_status = "✅ Configured" if Config.OPENAI_API_KEY else "❌ Missing"
        langsmith_status = "✅ Configured" if Config.LANGCHAIN_API_KEY else "❌ Missing"
        
        st.write(f"OpenAI: {openai_status}")
        st.write(f"LangSmith: {langsmith_status}")
        
        # Stock symbol input
        st.subheader("📊 Stock Analysis")
        symbol = st.text_input("Enter Stock Symbol", value="AAPL", placeholder="e.g., AAPL, MSFT, GOOGL")
        
        # Analysis options
        st.subheader("⚙️ Analysis Options")
        include_news = st.checkbox("Include News Analysis", value=True)
        include_fundamentals = st.checkbox("Include Fundamentals", value=True)
        
        # Run analysis button
        if st.button("🚀 Run Analysis", type="primary", use_container_width=True):
            if symbol:
                st.session_state.run_analysis = True
                st.session_state.symbol = symbol.upper()
            else:
                st.error("Please enter a stock symbol")
        
        # LangSmith monitoring
        if Config.LANGCHAIN_TRACING_V2:
            st.subheader("📊 LangSmith Monitoring")
            if st.button("View Performance Metrics"):
                st.session_state.show_metrics = True
        
        st.markdown("---")
        st.markdown("**Powered by:**")
        st.markdown("- LangChain")
        st.markdown("- LangGraph")
        st.markdown("- LangSmith")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📊 Stock Analysis Results")
        
        if st.session_state.get('run_analysis', False):
            # Show quick data first
            with st.spinner(f"Loading basic data for {st.session_state.symbol}..."):
                try:
                    quick_data = get_quick_stock_data(st.session_state.symbol)
                    if 'error' not in quick_data:
                        # Show basic info immediately
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Current Price", f"${quick_data.get('current_price', 0):.2f}")
                        with col2:
                            change = quick_data.get('change', 0)
                            st.metric("Change", f"${change:.2f}", f"{quick_data.get('change_percent', 0):+.2f}%")
                        with col3:
                            st.metric("Volume", f"{quick_data.get('volume', 0):,}")
                except:
                    pass
            
            # Progress bar for full analysis
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Run full analysis with progress updates
            status_text.text("🔄 Starting analysis...")
            progress_bar.progress(10)
            
            start_time = time.time()
            
            # Use cached version for better performance
            status_text.text("🧠 Running AI analysis (this may take 1-2 minutes)...")
            progress_bar.progress(50)
            
            results = cached_trading_analysis(st.session_state.symbol)
            progress_bar.progress(90)
            
            duration = time.time() - start_time
            
            # Log to LangSmith
            status_text.text("📊 Logging results...")
            try:
                tracker = LangSmithTracker()
                tracker.log_workflow_run(st.session_state.symbol, results, duration)
            except:
                pass  # Don't fail if logging fails
            
            progress_bar.progress(100)
            status_text.text("✅ Analysis complete!")
            
            # Store results in session state
            st.session_state.results = results
            st.session_state.analysis_complete = True
            st.session_state.run_analysis = False
            
            # Clear progress indicators
            time.sleep(1)
            progress_bar.empty()
            status_text.empty()
        
        # Display results
        if st.session_state.get('analysis_complete', False):
            display_analysis_results(st.session_state.results)
    
    with col2:
        st.header("📈 Quick Stats")
        
        if st.session_state.get('analysis_complete', False):
            display_quick_stats(st.session_state.results)
        
        # Recent analysis history
        if Config.LANGCHAIN_TRACING_V2:
            st.subheader("🕒 Recent Runs")
            display_recent_runs()
        
        # State inspection link
        st.subheader("🔍 State Monitor")
        if st.session_state.get('symbol'):
            monitor_url = f"http://localhost:8503/?symbol={st.session_state.symbol}"
            st.markdown(f"Monitor workflow states: [Open State Monitor for {st.session_state.symbol}]({monitor_url})")
        else:
            st.markdown("Monitor workflow states: [Open State Monitor](http://localhost:8503)")
        if st.button("🚀 Launch State Monitor"):
            if st.session_state.get('symbol'):
                monitor_url = f"http://localhost:8503/?symbol={st.session_state.symbol}"
                st.markdown(f"State monitor should open at: {monitor_url}")
            else:
                st.markdown("State monitor should be running at http://localhost:8503")
    
    # Performance metrics section
    if st.session_state.get('show_metrics', False):
        st.markdown("---")
        display_performance_metrics()
        st.session_state.show_metrics = False

def display_analysis_results(results):
    """Display the complete analysis results"""
    
    # Status indicator
    if results.get('status') == 'Analysis completed successfully':
        st.success("✅ Analysis completed successfully!")
    else:
        st.error(f"❌ Analysis failed: {results.get('status', 'Unknown error')}")
    
    # Stock Data Section
    if results.get('stock_data'):
        st.subheader("📊 Stock Data")
        stock_data = results['stock_data']
        
        if 'error' not in stock_data:
            # Create metrics display
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Current Price", f"${stock_data.get('current_price', 0):.2f}")
            
            with col2:
                change = stock_data.get('change', 0)
                change_percent = stock_data.get('change_percent', 0)
                st.metric("Change", f"${change:.2f}", f"{change_percent:+.2f}%")
            
            with col3:
                st.metric("Market Cap", f"${stock_data.get('market_cap', 0):,.0f}")
            
            with col4:
                st.metric("P/E Ratio", f"{stock_data.get('pe_ratio', 'N/A')}")
            
            # Company info
            st.info(f"**Company:** {stock_data.get('company_name', 'N/A')}")
            
            # Price chart if historical data available
            if stock_data.get('historical_data'):
                st.subheader("📈 Price History")
                display_price_chart(stock_data['historical_data'])
        else:
            st.error(f"Stock data error: {stock_data['error']}")
    
    # Stock Analysis Section
    if results.get('stock_analysis'):
        st.subheader("🧠 Stock Analysis")
        stock_analysis = results['stock_analysis']
        
        if stock_analysis.get('status') == 'success':
            analysis = stock_analysis.get('analysis', {})
            
            # Recommendation
            recommendation = analysis.get('recommendation', 'No recommendation')
            st.markdown(f"**Recommendation:** {recommendation}")
            
            # Key points
            key_points = analysis.get('key_points', [])
            if key_points:
                st.markdown("**Key Points:**")
                for point in key_points:
                    st.markdown(f"• {point}")
            
            # Full analysis
            with st.expander("📖 Full Stock Analysis"):
                st.write(analysis.get('full_analysis', 'No analysis available'))
        else:
            st.error(f"Stock analysis failed: {stock_analysis.get('error', 'Unknown error')}")
    
    # News Analysis Section
    if results.get('news_analysis'):
        st.subheader("📰 News Analysis")
        news_analysis = results['news_analysis']
        
        if news_analysis.get('status') == 'success':
            analysis = news_analysis.get('news_analysis', {})
            
            # Sentiment
            sentiment = analysis.get('sentiment', 'Unknown')
            sentiment_color = {
                'Positive': '🟢',
                'Negative': '🔴',
                'Neutral': '🟡'
            }.get(sentiment, '⚪')
            
            st.markdown(f"**Overall Sentiment:** {sentiment_color} {sentiment}")
            
            # Market impact
            market_impact = analysis.get('market_impact', 'Unknown')
            st.markdown(f"**Market Impact:** {market_impact}")
            
            # Key insights
            key_insights = analysis.get('key_insights', [])
            if key_insights:
                st.markdown("**Key Insights:**")
                for insight in key_insights:
                    st.markdown(f"• {insight}")
            
            # News articles
            news_data = results.get('news_data', [])
            if news_data and len(news_data) > 0:
                st.subheader("📰 Recent News Articles")
                display_news_articles(news_data)
            
            # Full analysis
            with st.expander("📖 Full News Analysis"):
                st.write(analysis.get('full_analysis', 'No analysis available'))
        else:
            st.error(f"News analysis failed: {news_analysis.get('error', 'Unknown error')}")
    
    # Final Analysis Section
    if results.get('final_analysis'):
        st.subheader("🎯 Final Investment Recommendation")
        final_analysis = results['final_analysis']
        
        if final_analysis.get('status') == 'success':
            analysis = final_analysis.get('final_analysis', {})
            
            # Create recommendation card
            col1, col2, col3 = st.columns(3)
            
            with col1:
                recommendation = analysis.get('investment_recommendation', 'Unknown')
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Recommendation</h3>
                    <h2>{recommendation}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                risk_level = analysis.get('risk_level', 'Unknown')
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Risk Level</h3>
                    <h2>{risk_level}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                confidence = analysis.get('confidence_score', 0)
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Confidence</h3>
                    <h2>{confidence}%</h2>
                </div>
                """, unsafe_allow_html=True)
            
            # Key factors
            key_factors = analysis.get('key_factors', [])
            if key_factors:
                st.markdown("**Key Factors:**")
                for factor in key_factors:
                    st.markdown(f"• {factor}")
            
            # Full analysis
            with st.expander("📖 Complete Investment Analysis"):
                st.write(analysis.get('full_analysis', 'No analysis available'))
        else:
            st.error(f"Final analysis failed: {final_analysis.get('error', 'Unknown error')}")
    
    # Errors section
    if results.get('errors'):
        st.subheader("⚠️ Errors & Warnings")
        for error in results['errors']:
            st.error(error)

def display_quick_stats(results):
    """Display quick statistics in the sidebar"""
    
    if results.get('stock_data') and 'error' not in results['stock_data']:
        stock_data = results['stock_data']
        
        # Price change indicator
        change = stock_data.get('change', 0)
        if change > 0:
            st.success(f"📈 +${change:.2f}")
        elif change < 0:
            st.error(f"📉 ${change:.2f}")
        else:
            st.info("➡️ $0.00")
        
        # Volume indicator
        volume = stock_data.get('volume', 0)
        avg_volume = stock_data.get('avg_volume', 0)
        if avg_volume > 0:
            volume_ratio = volume / avg_volume
            if volume_ratio > 1.5:
                st.info(f"🔥 High Volume ({volume_ratio:.1f}x)")
            elif volume_ratio < 0.5:
                st.info(f"📉 Low Volume ({volume_ratio:.1f}x)")
            else:
                st.info(f"📊 Normal Volume ({volume_ratio:.1f}x)")
    
    # Analysis status
    if results.get('stock_analysis', {}).get('status') == 'success':
        st.success("✅ Stock Analysis")
    else:
        st.error("❌ Stock Analysis")
    
    if results.get('news_analysis', {}).get('status') == 'success':
        st.success("✅ News Analysis")
    else:
        st.error("❌ News Analysis")
    
    if results.get('final_analysis', {}).get('status') == 'success':
        st.success("✅ Final Analysis")
    else:
        st.error("❌ Final Analysis")

def display_price_chart(historical_data):
    """Display price chart using Plotly"""
    if not historical_data:
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(historical_data)
    
    if 'Date' in df.columns and 'Close' in df.columns:
        # Create candlestick chart
        fig = go.Figure(data=[go.Scatter(
            x=df['Date'],
            y=df['Close'],
            mode='lines',
            name='Close Price',
            line=dict(color='#1f77b4', width=2)
        )])
        
        fig.update_layout(
            title=f"Price History",
            xaxis_title="Date",
            yaxis_title="Price ($)",
            height=400,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)

def display_news_articles(news_data):
    """Display news articles in a clean format"""
    for i, article in enumerate(news_data[:5]):  # Show first 5 articles
        if 'error' not in article:
            with st.expander(f"📰 {article.get('title', 'No title')}"):
                st.write(f"**Source:** {article.get('source', 'Unknown')}")
                st.write(f"**Published:** {article.get('published_at', 'Unknown')}")
                st.write(f"**Description:** {article.get('description', 'No description')}")
                
                if article.get('url'):
                    st.markdown(f"[Read Full Article]({article['url']})")

def display_recent_runs():
    """Display recent LangSmith runs"""
    try:
        tracker = LangSmithTracker()
        runs = tracker.get_run_history(limit=5)
        
        if runs:
            for run in runs:
                status_icon = "✅" if run['status'] == 'completed' else "❌"
                st.write(f"{status_icon} {run['name']}")
                st.caption(f"Duration: {run.get('duration', 0):.1f}s")
        else:
            st.info("No recent runs found")
    except Exception as e:
        st.error(f"Failed to load recent runs: {e}")

def display_performance_metrics():
    """Display LangSmith performance metrics"""
    st.header("📊 Performance Metrics")
    
    try:
        tracker = LangSmithTracker()
        metrics = tracker.get_performance_metrics()
        
        if metrics:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Runs", metrics['total_runs'])
            
            with col2:
                st.metric("Success Rate", f"{metrics['overall_success_rate']:.1f}%")
            
            with col3:
                st.metric("Failed Runs", metrics['failed_runs'])
            
            with col4:
                st.metric("Avg Duration", f"{metrics['average_duration_seconds']:.1f}s")
            
            # Agent performance breakdown
            st.subheader("Agent Performance")
            agent_metrics = metrics.get('agent_performance', {})
            
            if agent_metrics:
                agent_data = []
                for agent_type, data in agent_metrics.items():
                    agent_data.append({
                        'Agent Type': agent_type.replace('_', ' ').title(),
                        'Total Runs': data['total'],
                        'Success Rate': f"{data['success_rate']:.1f}%"
                    })
                
                df = pd.DataFrame(agent_data)
                st.dataframe(df, use_container_width=True)
        else:
            st.info("No performance data available")
            
    except Exception as e:
        st.error(f"Failed to load performance metrics: {e}")

if __name__ == "__main__":
    # Initialize session state
    if 'run_analysis' not in st.session_state:
        st.session_state.run_analysis = False
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False
    if 'results' not in st.session_state:
        st.session_state.results = {}
    if 'symbol' not in st.session_state:
        st.session_state.symbol = ""
    if 'show_metrics' not in st.session_state:
        st.session_state.show_metrics = False
    
    # Validate configuration
    try:
        Config.validate_config()
        main()
    except ValueError as e:
        st.error(f"Configuration Error: {e}")
        st.info("Please check your .env file and ensure all required API keys are configured.")
    except Exception as e:
        st.error(f"Application Error: {e}")
        st.info("Please check the console for more details.")
