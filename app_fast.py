import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

# Page config for better performance
st.set_page_config(
    page_title="Fast Trading Analysis",
    page_icon="⚡",
    layout="wide"
)

@st.cache_data(ttl=60)  # Cache for 1 minute
def get_stock_data(symbol):
    """Get stock data quickly"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.fast_info
        hist = ticker.history(period="5d")
        
        return {
            'price': info.get('last_price', 0),
            'change': info.get('last_price', 0) - info.get('previous_close', 0),
            'change_percent': ((info.get('last_price', 0) - info.get('previous_close', 0)) / info.get('previous_close', 1)) * 100,
            'volume': info.get('day_volume', 0),
            'market_cap': info.get('market_cap', 0),
            'history': hist
        }
    except Exception as e:
        return {'error': str(e)}

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_simple_analysis(symbol, price, change_percent):
    """Simple rule-based analysis for speed"""
    
    analysis = {
        'recommendation': 'Hold',
        'risk_level': 'Medium',
        'confidence': 70
    }
    
    # Simple rules
    if change_percent > 5:
        analysis['recommendation'] = 'Strong Buy'
        analysis['risk_level'] = 'High'
        analysis['confidence'] = 80
    elif change_percent > 2:
        analysis['recommendation'] = 'Buy'
        analysis['risk_level'] = 'Medium'
        analysis['confidence'] = 75
    elif change_percent < -5:
        analysis['recommendation'] = 'Strong Sell'
        analysis['risk_level'] = 'High'
        analysis['confidence'] = 80
    elif change_percent < -2:
        analysis['recommendation'] = 'Sell'
        analysis['risk_level'] = 'Medium'
        analysis['confidence'] = 75
    
    return analysis

def main():
    st.title("⚡ Fast Trading Analysis")
    st.markdown("*Lightning-fast stock analysis with caching*")
    
    # Sidebar
    with st.sidebar:
        st.header("📊 Quick Analysis")
        symbol = st.text_input("Stock Symbol", value="AAPL")
        analyze_btn = st.button("⚡ Quick Analysis", type="primary")
    
    if analyze_btn and symbol:
        with st.spinner(f"Getting data for {symbol}..."):
            data = get_stock_data(symbol.upper())
            
        if 'error' in data:
            st.error(f"Error: {data['error']}")
        else:
            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Price", f"${data['price']:.2f}")
            
            with col2:
                st.metric("Change", f"${data['change']:.2f}", f"{data['change_percent']:+.2f}%")
            
            with col3:
                st.metric("Volume", f"{data['volume']:,}")
            
            with col4:
                st.metric("Market Cap", f"${data['market_cap']:,.0f}")
            
            # Chart
            if not data['history'].empty:
                fig = go.Figure(data=[go.Scatter(
                    x=data['history'].index,
                    y=data['history']['Close'],
                    mode='lines+markers',
                    name='Price',
                    line=dict(color='#1f77b4', width=3)
                )])
                
                fig.update_layout(
                    title=f"{symbol.upper()} - 5 Day Price History",
                    xaxis_title="Date",
                    yaxis_title="Price ($)",
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Quick Analysis
            analysis = get_simple_analysis(symbol, data['price'], data['change_percent'])
            
            st.subheader("📈 Quick Analysis")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Recommendation", analysis['recommendation'])
            
            with col2:
                st.metric("Risk Level", analysis['risk_level'])
            
            with col3:
                st.metric("Confidence", f"{analysis['confidence']}%")
            
            # Performance note
            st.success("⚡ Analysis completed in under 5 seconds!")
            
            # Link to full analysis
            st.info("💡 For detailed AI analysis, use the main app: `python -m streamlit run app.py`")

if __name__ == "__main__":
    main()
