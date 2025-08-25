"""
LangGraph State Inspector
Tool for monitoring and debugging LangGraph workflow states
"""

import json
from typing import Dict, Any, List, TypedDict
from datetime import datetime
import streamlit as st

# Define WorkflowState here to avoid circular import
class WorkflowState(TypedDict):
    symbol: str
    stock_data: Dict[str, Any]
    news_data: List[Dict[str, Any]]
    stock_analysis: Dict[str, Any]
    news_analysis: Dict[str, Any]
    final_analysis: Dict[str, Any]
    errors: List[str]
    status: str

class StateInspector:
    """Inspector for monitoring LangGraph workflow states"""
    
    def __init__(self):
        self.state_history: List[Dict[str, Any]] = []
        self.current_step = 0
    
    def log_state(self, step_name: str, state: WorkflowState):
        """Log the current state at a specific step"""
        state_snapshot = {
            'timestamp': datetime.now().isoformat(),
            'step': self.current_step,
            'step_name': step_name,
            'symbol': state.get('symbol', 'Unknown'),
            'status': state.get('status', 'Unknown'),
            'errors_count': len(state.get('errors', [])),
            'errors': state.get('errors', []),
            'has_stock_data': bool(state.get('stock_data')),
            'has_news_data': bool(state.get('news_data')),
            'has_stock_analysis': bool(state.get('stock_analysis')),
            'has_news_analysis': bool(state.get('news_analysis')),
            'has_final_analysis': bool(state.get('final_analysis')),
            'state_size': self._calculate_state_size(state)
        }
        
        self.state_history.append(state_snapshot)
        self.current_step += 1
        
        # Print to console
        print(f"\n{'='*50}")
        print(f"🔍 STATE INSPECTOR - Step {self.current_step}: {step_name}")
        print(f"{'='*50}")
        print(f"Symbol: {state_snapshot['symbol']}")
        print(f"Status: {state_snapshot['status']}")
        print(f"Errors: {state_snapshot['errors_count']}")
        print(f"Data Status:")
        print(f"  ├── Stock Data: {'✅' if state_snapshot['has_stock_data'] else '❌'}")
        print(f"  ├── News Data: {'✅' if state_snapshot['has_news_data'] else '❌'}")
        print(f"  ├── Stock Analysis: {'✅' if state_snapshot['has_stock_analysis'] else '❌'}")
        print(f"  ├── News Analysis: {'✅' if state_snapshot['has_news_analysis'] else '❌'}")
        print(f"  └── Final Analysis: {'✅' if state_snapshot['has_final_analysis'] else '❌'}")
        print(f"State Size: {state_snapshot['state_size']} bytes")
        
        if state_snapshot['errors_count'] > 0:
            print(f"\n⚠️ ERRORS:")
            for i, error in enumerate(state_snapshot['errors'], 1):
                print(f"  {i}. {error}")
        
        print(f"{'='*50}\n")
    
    def _calculate_state_size(self, state: WorkflowState) -> int:
        """Calculate approximate size of state in bytes"""
        try:
            return len(json.dumps(dict(state), default=str))
        except:
            return 0
    
    def get_state_summary(self) -> Dict[str, Any]:
        """Get a summary of all state changes"""
        if not self.state_history:
            return {'message': 'No state history available'}
        
        return {
            'total_steps': len(self.state_history),
            'current_symbol': self.state_history[-1]['symbol'],
            'final_status': self.state_history[-1]['status'],
            'total_errors': sum(s['errors_count'] for s in self.state_history),
            'steps_completed': [s['step_name'] for s in self.state_history],
            'timeline': self.state_history
        }
    
    def export_state_history(self, filename: str = None) -> str:
        """Export state history to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"langgraph_state_history_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.state_history, f, indent=2)
        
        return filename
    
    def clear_history(self):
        """Clear state history"""
        self.state_history = []
        self.current_step = 0

# Global state inspector instance
state_inspector = StateInspector()

def display_state_dashboard():
    """Streamlit dashboard for state inspection"""
    st.sidebar.markdown("---")
    st.sidebar.header("🔍 State Inspector")
    
    if st.sidebar.button("Clear State History"):
        state_inspector.clear_history()
        st.sidebar.success("State history cleared!")
    
    if st.sidebar.button("Export State History"):
        filename = state_inspector.export_state_history()
        st.sidebar.success(f"Exported to: {filename}")
    
    # Show state summary
    summary = state_inspector.get_state_summary()
    
    if 'message' not in summary:
        st.sidebar.subheader("📊 Workflow Progress")
        st.sidebar.metric("Total Steps", summary['total_steps'])
        st.sidebar.metric("Total Errors", summary['total_errors'])
        
        # Show completed steps
        st.sidebar.subheader("✅ Completed Steps")
        for i, step in enumerate(summary['steps_completed'], 1):
            st.sidebar.write(f"{i}. {step}")
        
        # Show detailed timeline in expander
        with st.sidebar.expander("🕐 Detailed Timeline"):
            for state in summary['timeline']:
                st.write(f"**{state['step_name']}**")
                st.write(f"Status: {state['status']}")
                st.write(f"Errors: {state['errors_count']}")
                st.write(f"Time: {state['timestamp']}")
                st.write("---")

def inspect_state(step_name: str, state: WorkflowState):
    """Convenience function to inspect state"""
    state_inspector.log_state(step_name, state)

# Example usage in workflow nodes
def monitored_fetch_stock_data(state: WorkflowState) -> WorkflowState:
    """Example of how to add monitoring to workflow nodes"""
    inspect_state("fetch_stock_data_start", state)
    
    # Your actual logic here
    # ... 
    
    inspect_state("fetch_stock_data_end", state)
    return state
