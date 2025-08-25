"""
Bridge to connect the state monitor with the actual LangGraph workflow
This module provides real-time state updates from the workflow to the monitor
"""

import json
import time
from datetime import datetime
from typing import Dict, Any, List
import threading
import os

# Global state storage
_workflow_states = []
_lock = threading.Lock()

class WorkflowStateBridge:
    """Bridge to capture and store workflow states for monitoring"""
    
    def __init__(self):
        self.states = []
        self.current_run_id = None
    
    def start_workflow_run(self, symbol: str, run_id: str = None):
        """Start tracking a new workflow run"""
        self.current_run_id = run_id or f"run_{int(time.time())}"
        self.log_state("workflow_start", {
            'symbol': symbol,
            'run_id': self.current_run_id,
            'status': 'started',
            'progress': 0
        })
    
    def log_state(self, step_name: str, state_data: Dict[str, Any]):
        """Log a workflow state for monitoring"""
        with _lock:
            state_entry = {
                'timestamp': datetime.now(),
                'step_name': step_name,
                'run_id': self.current_run_id,
                'data': state_data,
                'symbol': state_data.get('symbol', 'Unknown')
            }
            
            # Add to global states
            _workflow_states.append(state_entry)
            
            # Keep only last 100 states
            if len(_workflow_states) > 100:
                _workflow_states.pop(0)
            
            # Also save to local instance
            self.states.append(state_entry)
            
            print(f"🔍 [State Bridge] {step_name}: {state_data.get('status', 'unknown')}")
    
    def get_latest_states(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get the latest workflow states"""
        with _lock:
            return _workflow_states[-limit:] if _workflow_states else []
    
    def get_states_for_symbol(self, symbol: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get states for a specific symbol"""
        with _lock:
            symbol_states = [s for s in _workflow_states if s.get('symbol', '').upper() == symbol.upper()]
            return symbol_states[-limit:] if symbol_states else []
    
    def clear_states(self):
        """Clear all stored states"""
        with _lock:
            global _workflow_states
            _workflow_states = []
            self.states = []

# Global bridge instance
workflow_bridge = WorkflowStateBridge()

def get_workflow_states(symbol: str = None, limit: int = 50) -> List[Dict[str, Any]]:
    """Get workflow states for monitoring"""
    if symbol:
        return workflow_bridge.get_states_for_symbol(symbol, limit)
    return workflow_bridge.get_latest_states(limit)

def log_workflow_state(step_name: str, state_data: Dict[str, Any]):
    """Log a workflow state (convenience function)"""
    workflow_bridge.log_state(step_name, state_data)

def start_workflow_monitoring(symbol: str, run_id: str = None):
    """Start monitoring a workflow run"""
    workflow_bridge.start_workflow_run(symbol, run_id)

def clear_workflow_states():
    """Clear all workflow states"""
    workflow_bridge.clear_states()

# Enhanced state monitor with real workflow integration
def create_enhanced_state_monitor():
    """Create an enhanced state monitor that works with real workflow data"""
    
    import streamlit as st
    import pandas as pd
    import plotly.express as px
    from datetime import datetime, timedelta
    
    st.title("🔍 Enhanced LangGraph State Monitor")
    st.markdown("*Connected to Real Workflow*")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Monitor Controls")
        symbol = st.text_input("Stock Symbol", value="AAPL")
        
        if st.button("🔄 Refresh States"):
            st.experimental_rerun()
        
        if st.button("🗑️ Clear History"):
            clear_workflow_states()
            st.success("States cleared!")
        
        auto_refresh = st.checkbox("🔄 Auto Refresh", value=True)
    
    # Get real workflow states
    states = get_workflow_states(symbol, limit=20)
    
    if states:
        # Convert to DataFrame
        df_data = []
        for state in states:
            df_data.append({
                'timestamp': state['timestamp'],
                'step_name': state['step_name'],
                'symbol': state['symbol'],
                'status': state['data'].get('status', 'unknown'),
                'progress': state['data'].get('progress', 0),
                'duration': state['data'].get('duration', 0),
                'run_id': state['run_id']
            })
        
        df = pd.DataFrame(df_data)
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total States", len(df))
        with col2:
            st.metric("Current Symbol", symbol)
        with col3:
            latest_status = df.iloc[-1]['status'] if not df.empty else "None"
            st.metric("Latest Status", latest_status)
        with col4:
            total_duration = df['duration'].sum()
            st.metric("Total Duration", f"{total_duration:.1f}s")
        
        # Charts
        st.subheader("📈 Real-Time Progress")
        if not df.empty:
            fig = px.line(df, x='step_name', y='progress', 
                         title='Workflow Progress', markers=True)
            st.plotly_chart(fig, use_container_width=True)
            
            # State table
            st.subheader("📋 Real Workflow States")
            st.dataframe(df[['timestamp', 'step_name', 'symbol', 'status', 'progress', 'duration']], 
                        use_container_width=True)
    else:
        st.info("🔄 No real workflow states found. Run a trading analysis to see live data!")
        
        # Show instructions
        st.markdown("""
        ### 🚀 To see real workflow states:
        1. Go to the main trading app
        2. Run an analysis for any stock symbol
        3. Come back here to see the real-time states!
        """)
    
    # Auto refresh
    if auto_refresh:
        time.sleep(2)
        st.experimental_rerun()

if __name__ == "__main__":
    create_enhanced_state_monitor()
