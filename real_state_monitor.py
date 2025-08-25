import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import json
import os
from typing import Dict, List, Any

# Configure page
st.set_page_config(
    page_title="LangGraph State Monitor",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .status-running {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    }
    .status-error {
        background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%);
    }
    .status-complete {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
</style>
""", unsafe_allow_html=True)

st.title("🔍 LangGraph Real-Time State Monitor")
st.markdown("---")

# Get symbol from URL parameters or session state
def get_symbol_from_url():
    """Extract symbol from URL query parameters"""
    try:
        # Get the current URL
        query_params = st.query_params
        symbol_param = query_params.get("symbol", None)
        if symbol_param:
            return symbol_param.upper().strip()
    except:
        pass
    return None

# Initialize session state
if 'monitoring' not in st.session_state:
    st.session_state.monitoring = False
if 'state_history' not in st.session_state:
    st.session_state.state_history = []
if 'previous_symbol' not in st.session_state:
    st.session_state.previous_symbol = None
if 'current_symbol' not in st.session_state:
    # Check URL first, then default to AAPL
    url_symbol = get_symbol_from_url()
    st.session_state.current_symbol = url_symbol if url_symbol else "AAPL"

# Sidebar controls
with st.sidebar:
    st.header("⚙️ Monitor Controls")
    
    # Symbol input
    symbol = st.text_input("Stock Symbol", value=st.session_state.current_symbol, key="symbol_input")
    if symbol != st.session_state.current_symbol:
        st.session_state.current_symbol = symbol
    
    # Monitoring toggle
    if st.button("🚀 Start Monitoring" if not st.session_state.monitoring else "⏹️ Stop Monitoring"):
        st.session_state.monitoring = not st.session_state.monitoring
        if st.session_state.monitoring:
            st.success("✅ Monitoring Started!")
        else:
            st.info("⏹️ Monitoring Stopped")
    
    # Clear history
    if st.button("🗑️ Clear History"):
        st.session_state.state_history = []
        st.success("History cleared!")
    
    # Refresh real data
    if st.button("🔄 Refresh Real Data"):
        st.session_state.state_history = get_real_workflow_states(symbol)
        if st.session_state.state_history:
            st.success(f"✅ Loaded {len(st.session_state.state_history)} real workflow states for {symbol}")
        else:
            st.info(f"ℹ️ No real workflow data found for {symbol}. Showing sample data.")
    
    # Auto-refresh
    auto_refresh = st.checkbox("🔄 Auto Refresh (5s)", value=True)
    
    st.markdown("---")
    st.markdown("### 📊 Current Status")
    status_color = "🟢" if st.session_state.monitoring else "🔴"
    st.markdown(f"{status_color} **Monitor: {'Active' if st.session_state.monitoring else 'Inactive'}**")
    
    # Data source indicator
    if st.session_state.state_history:
        # Check if we have real workflow data
        has_real_data = any('workflow_start' in state.get('step_name', '') or 'workflow_complete' in state.get('step_name', '') for state in st.session_state.state_history)
        if has_real_data:
            st.success("✅ **Real Workflow Data**")
        else:
            st.info("ℹ️ **Sample Data** (No real workflow runs yet)")
    else:
        st.info("ℹ️ **No Data**")
    
    # Auto-load data if symbol was passed via URL
    url_symbol = get_symbol_from_url()
    if url_symbol and url_symbol != symbol:
        st.success(f"✅ **Auto-loaded symbol from URL: {url_symbol}**")
        st.info("🔄 **Auto-loading data for symbol from URL...**")
        # This will trigger data loading in the main content area
    
    st.markdown("---")
    st.markdown("### 🔗 **Trading Apps**")
    st.markdown("[📊 Full Analysis](http://localhost:8501)")
    st.markdown("[⚡ Ultra Fast App](http://localhost:8512)")
    
    st.markdown("---")
    st.markdown("### 🧪 **Get Real Data**")
    st.markdown("**To see real workflow states:**")
    st.markdown("1. Open a trading app above")
    st.markdown("2. Run analysis for any symbol")
    st.markdown("3. Come back & click 'Refresh Real Data'")

# Get real workflow states from the bridge
def get_real_workflow_states(symbol: str):
    """Get real workflow states from the state bridge"""
    try:
        from workflow_state_bridge import get_workflow_states
        states = get_workflow_states(symbol, limit=20)
        
        if states:
            # Convert bridge states to display format
            display_states = []
            for i, state in enumerate(states):
                # Calculate progress based on step name
                step_progress = {
                    'workflow_start': 0,
                    'fetch_stock_data': 20,
                    'analyze_stock': 40,
                    'analyze_news': 60,
                    'coordinate_analysis': 80,
                    'workflow_complete': 100
                }.get(state['step_name'], 0)
                
                display_states.append({
                    'timestamp': state['timestamp'],
                    'step_name': state['step_name'],
                    'symbol': state['symbol'],
                    'status': state['data'].get('status', 'unknown'),
                    'duration': state['data'].get('duration', 0),
                    'data_size': 1024,  # Default size
                    'progress': step_progress
                })
            
            return display_states
        else:
            return []
    except ImportError:
        # Fallback to sample data if bridge not available
        return generate_sample_states(symbol)

def generate_sample_states(symbol: str):
    """Generate sample states when real data not available"""
    current_time = datetime.now()
    
    # Sample workflow states
    states = [
        {
            'timestamp': current_time - timedelta(seconds=30),
            'step_name': 'fetch_stock_data',
            'symbol': symbol,
            'status': 'completed',
            'duration': 2.3,
            'data_size': 1024,
            'progress': 20
        },
        {
            'timestamp': current_time - timedelta(seconds=25),
            'step_name': 'fetch_news_data',
            'symbol': symbol,
            'status': 'completed',
            'duration': 3.1,
            'data_size': 2048,
            'progress': 40
        },
        {
            'timestamp': current_time - timedelta(seconds=18),
            'step_name': 'analyze_stock',
            'symbol': symbol,
            'status': 'completed',
            'duration': 4.7,
            'data_size': 512,
            'progress': 60
        },
        {
            'timestamp': current_time - timedelta(seconds=12),
            'step_name': 'analyze_news',
            'symbol': symbol,
            'status': 'completed',
            'duration': 3.9,
            'data_size': 768,
            'progress': 80
        },
        {
            'timestamp': current_time - timedelta(seconds=5),
            'step_name': 'coordinate_analysis',
            'symbol': symbol,
            'status': 'completed',
            'duration': 2.1,
            'data_size': 1536,
            'progress': 100
        }
    ]
    
    return states

# Main content area
col1, col2, col3, col4 = st.columns(4)

# Generate current data
if st.session_state.monitoring or len(st.session_state.state_history) == 0:
    # Check if we should auto-load data from URL
    url_symbol = get_symbol_from_url()
    if url_symbol and url_symbol != symbol:
        # Update symbol if it came from URL
        st.session_state.current_symbol = url_symbol
        symbol = url_symbol
        st.success(f"🎯 **Symbol Auto-Loaded from URL: {symbol}**")
        st.info("🔄 **Loading data for this symbol...**")
    
    current_states = get_real_workflow_states(symbol)
    if current_states:
        st.session_state.state_history = current_states
        if url_symbol and url_symbol != st.session_state.get('previous_symbol'):
            st.success(f"✅ **Data loaded for {symbol}**")
            st.session_state.previous_symbol = symbol
    else:
        # If no real data, use sample data
        st.session_state.state_history = generate_sample_states(symbol)
        if url_symbol and url_symbol != st.session_state.get('previous_symbol'):
            st.info(f"ℹ️ **Sample data loaded for {symbol}** (No real workflow data yet)")
            st.session_state.previous_symbol = symbol

# Metrics
with col1:
    st.markdown("""
    <div class="metric-card">
        <h3>📊 Total Steps</h3>
        <h2>5</h2>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <h3>🏷️ Symbol</h3>
        <h2>{st.session_state.current_symbol}</h2>
    </div>
    """, unsafe_allow_html=True)

with col3:
    current_status = "Running" if st.session_state.monitoring else "Complete"
    status_class = "status-running" if st.session_state.monitoring else "status-complete"
    st.markdown(f"""
    <div class="metric-card {status_class}">
        <h3>⚡ Status</h3>
        <h2>{current_status}</h2>
    </div>
    """, unsafe_allow_html=True)

with col4:
    total_duration = sum(state.get('duration', 0) for state in st.session_state.state_history)
    st.markdown(f"""
    <div class="metric-card">
        <h3>⏱️ Duration</h3>
        <h2>{total_duration:.1f}s</h2>
    </div>
    """, unsafe_allow_html=True)

# Create DataFrame from state history
if st.session_state.state_history:
    df = pd.DataFrame(st.session_state.state_history)
    df['timestamp_str'] = df['timestamp'].dt.strftime('%H:%M:%S')
    
    # Two columns for charts
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.subheader("📈 Workflow Progress")
        fig_progress = px.line(
            df, 
            x='step_name', 
            y='progress',
            title=f'Progress Timeline - {st.session_state.current_symbol}',
            markers=True
        )
        fig_progress.update_layout(
            xaxis_title="Workflow Step",
            yaxis_title="Progress (%)",
            showlegend=False
        )
        st.plotly_chart(fig_progress, use_container_width=True)
    
    with chart_col2:
        st.subheader("⏱️ Step Durations")
        fig_duration = px.bar(
            df,
            x='step_name',
            y='duration',
            title='Step Processing Times',
            color='duration',
            color_continuous_scale='viridis'
        )
        fig_duration.update_layout(
            xaxis_title="Workflow Step",
            yaxis_title="Duration (seconds)",
            showlegend=False
        )
        st.plotly_chart(fig_duration, use_container_width=True)
    
    # Real-time status table
    st.subheader("📋 Real-Time Workflow State")
    
    # Format the data for display
    display_df = df.copy()
    display_df['Step'] = display_df['step_name'].str.replace('_', ' ').str.title()
    display_df['Time'] = display_df['timestamp_str']
    display_df['Duration (s)'] = display_df['duration'].round(2)
    display_df['Data Size (KB)'] = (display_df['data_size'] / 1024).round(1)
    display_df['Progress (%)'] = display_df['progress']
    display_df['Status'] = display_df['status'].str.title()
    
    # Color code status
    def color_status(val):
        if val == 'Running':
            return 'background-color: #90EE90'
        elif val == 'Completed':
            return 'background-color: #87CEEB'
        elif val == 'Error':
            return 'background-color: #FFB6C1'
        return ''
    
    styled_df = display_df[['Step', 'Time', 'Duration (s)', 'Data Size (KB)', 'Progress (%)', 'Status']].style.map(
        color_status, subset=['Status']
    )
    
    st.dataframe(styled_df, use_container_width=True)
    
    # Workflow visualization
    st.subheader("🔄 Workflow Flow")
    
    # Create workflow flow chart
    fig_flow = go.Figure()
    
    steps = df['step_name'].tolist()
    progress_values = df['progress'].tolist()
    
    # Add nodes
    for i, (step, progress) in enumerate(zip(steps, progress_values)):
        color = 'lightgreen' if progress == 100 else 'orange' if progress > 0 else 'lightgray'
        fig_flow.add_trace(go.Scatter(
            x=[i],
            y=[0],
            mode='markers+text',
            marker=dict(size=50, color=color),
            text=[step.replace('_', '<br>')],
            textposition="middle center",
            name=step,
            showlegend=False
        ))
    
    # Add connections
    for i in range(len(steps) - 1):
        fig_flow.add_trace(go.Scatter(
            x=[i, i+1],
            y=[0, 0],
            mode='lines',
            line=dict(color='gray', width=2),
            showlegend=False
        ))
    
    fig_flow.update_layout(
        title="Workflow Step Flow",
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=200
    )
    
    st.plotly_chart(fig_flow, use_container_width=True)

else:
    st.info("🔄 No workflow data available. Start monitoring to see real-time states!")

# Footer with current time
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col2:
    st.markdown(f"""
    <div style="text-align: center; color: #666;">
        🕐 Last Updated: {datetime.now().strftime('%H:%M:%S')}
    </div>
    """, unsafe_allow_html=True)

# Auto-refresh
if auto_refresh and st.session_state.monitoring:
    time.sleep(1)
    st.rerun()

# Instructions
with st.expander("📚 How to Use This Monitor"):
    st.markdown("""
    ### 🎯 **Getting Started**
    1. **Enter a stock symbol** in the sidebar (e.g., AAPL, TSLA, GOOGL)
    2. **Click "Start Monitoring"** to begin real-time tracking
    3. **Click "Refresh Real Data"** to load actual workflow states
    4. **Watch the progress** as the workflow processes your request
    
    ### 📊 **Understanding the Charts**
    - **Progress Timeline**: Shows completion percentage for each step
    - **Step Durations**: Processing time for each workflow component
    - **Workflow Flow**: Visual representation of the step sequence
    
    ### ⚙️ **Features**
    - 🔄 **Auto-refresh** every 5 seconds when monitoring
    - 📋 **Real-time state table** with color-coded status
    - 🗑️ **Clear history** to start fresh
    - ⏹️ **Stop/Start** monitoring as needed
    - 🔄 **Refresh Real Data** to load actual workflow states
    
    ### 🚀 **Integration**
    This monitor connects to your LangGraph workflow and displays:
    - Stock data fetching progress
    - News analysis status  
    - Agent coordination steps
    - Performance metrics
    
    ### 📈 **To See Real Data:**
    1. **Run a trading analysis** from your main app or ultra-fast app
    2. **Come back here** and click "Refresh Real Data"
    3. **Select the symbol** you just analyzed
    4. **View real-time workflow states** with actual progress!
    """)
