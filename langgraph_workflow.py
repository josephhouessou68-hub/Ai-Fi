from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from typing import Dict, List, Any, TypedDict, Annotated
import asyncio
from agents import StockAnalysisAgent, NewsAnalysisAgent, CoordinatorAgent
from api_clients import StockAPIClient, NewsAPIClient
from config import Config
import streamlit as st
import time
import operator

# Define the state structure for the workflow
class WorkflowState(TypedDict):
    symbol: str
    stock_data: Dict[str, Any]
    news_data: List[Dict[str, Any]]
    stock_analysis: Dict[str, Any]
    news_analysis: Dict[str, Any]
    final_analysis: Dict[str, Any]
    errors: Annotated[List[str], operator.add]
    status: str

# Global state inspector for debugging
_state_history = []

def inspect_state(step_name: str, state: WorkflowState):
    """Inspect and log workflow state"""
    try:
        state_snapshot = {
            'timestamp': time.time(),
            'step_name': step_name,
            'symbol': state.get('symbol', 'Unknown'),
            'status': state.get('status', 'Unknown'),
            'errors_count': len(state.get('errors', [])),
            'has_stock_data': bool(state.get('stock_data')),
            'has_news_data': bool(state.get('news_data')),
            'has_stock_analysis': bool(state.get('stock_analysis')),
            'has_news_analysis': bool(state.get('news_analysis')),
            'has_final_analysis': bool(state.get('final_analysis'))
        }
        
        _state_history.append(state_snapshot)
        
        # Print to console for debugging
        print(f"🔍 [{step_name}] Symbol: {state_snapshot['symbol']}, Status: {state_snapshot['status']}, Errors: {state_snapshot['errors_count']}")
        
    except Exception as e:
        print(f"Error in state inspection: {e}")

class LangGraphTradingWorkflow:
    """LangGraph-based multi-agent trading analysis workflow"""
    
    def __init__(self):
        # Initialize agents
        self.stock_agent = StockAnalysisAgent()
        self.news_agent = NewsAnalysisAgent()
        self.coordinator_agent = CoordinatorAgent()
        
        # Initialize API clients
        self.stock_client = StockAPIClient()
        self.news_client = NewsAPIClient()
        
        # Initialize memory and workflow
        self.memory = MemorySaver()
        self.workflow = self._create_workflow()
    
    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow"""
        
        # Create the workflow graph
        workflow = StateGraph(WorkflowState)
        
        # Add nodes for each agent
        workflow.add_node("fetch_stock_data", self._fetch_stock_data)
        workflow.add_node("fetch_news_data", self._fetch_news_data)
        workflow.add_node("analyze_stock", self._analyze_stock)
        workflow.add_node("analyze_news", self._analyze_news)
        workflow.add_node("coordinate_analysis", self._coordinate_analysis)
        workflow.add_node("handle_errors", self._handle_errors)
        
        # Define the workflow edges
        workflow.set_entry_point("fetch_stock_data")
        
        # Sequential workflow to avoid concurrency issues
        workflow.add_edge("fetch_stock_data", "fetch_news_data")
        workflow.add_edge("fetch_news_data", "analyze_stock")
        workflow.add_edge("analyze_stock", "analyze_news")
        workflow.add_edge("analyze_news", "coordinate_analysis")
        
        # Handle any errors
        workflow.add_edge("handle_errors", END)
        workflow.add_edge("coordinate_analysis", END)
        
        # Set conditional edges for error handling
        workflow.add_conditional_edges(
            "fetch_stock_data",
            self._should_continue,
            {
                "continue": "fetch_news_data",
                "error": "handle_errors"
            }
        )
        
        workflow.add_conditional_edges(
            "fetch_news_data",
            self._should_continue,
            {
                "continue": "analyze_stock",
                "error": "handle_errors"
            }
        )
        
        return workflow.compile(checkpointer=self.memory)
    
    def _should_continue(self, state: WorkflowState) -> str:
        """Determine if workflow should continue or handle errors"""
        if state.get("errors"):
            return "error"
        return "continue"
    
    async def _fetch_stock_data(self, state: WorkflowState) -> WorkflowState:
        """Fetch stock data from APIs"""
        inspect_state("fetch_stock_data_start", state)
        
        try:
            symbol = state["symbol"]
            
            # Fetch stock data
            stock_data = self.stock_client.get_stock_data(symbol)
            
            if "error" in stock_data:
                state["errors"].append(f"Stock data fetch failed: {stock_data['error']}")
                state["stock_data"] = {}
                print(f"🔍 [STATE CHECK] Stock data fetch failed: {stock_data['error']}")
            else:
                state["stock_data"] = stock_data
                state["status"] = "Stock data fetched successfully"
                print(f"🔍 [STATE CHECK] Stock data fetched successfully for {symbol}")
            
        except Exception as e:
            state["errors"].append(f"Stock data fetch error: {str(e)}")
            state["stock_data"] = {}
            print(f"🔍 [STATE CHECK] Exception in fetch_stock_data: {str(e)}")
        
        inspect_state("fetch_stock_data_end", state)
        return state
    
    async def _fetch_news_data(self, state: WorkflowState) -> WorkflowState:
        """Fetch news data from APIs"""
        try:
            symbol = state["symbol"]
            
            # Fetch news data
            news_data = self.news_client.get_news(symbol, days=7)
            
            if not news_data or (len(news_data) == 1 and "error" in news_data[0]):
                state["errors"].append("News data fetch failed")
                state["news_data"] = []
            else:
                state["news_data"] = news_data
                state["status"] = "News data fetched successfully"
            
        except Exception as e:
            state["errors"].append(f"News data fetch error: {str(e)}")
            state["news_data"] = []
        
        return state
    
    async def _analyze_stock(self, state: WorkflowState) -> WorkflowState:
        """Analyze stock data using the Stock Analysis Agent"""
        try:
            symbol = state["symbol"]
            stock_data = state["stock_data"]
            
            if not stock_data or "error" in stock_data:
                state["errors"].append("No stock data available for analysis")
                state["stock_analysis"] = {"status": "error", "error": "No stock data"}
            else:
                # Analyze stock data
                stock_analysis = self.stock_agent.analyze_stock(symbol, stock_data)
                state["stock_analysis"] = stock_analysis
                
                if stock_analysis.get("status") == "success":
                    state["status"] = "Stock analysis completed"
                else:
                    state["errors"].append(f"Stock analysis failed: {stock_analysis.get('error', 'Unknown error')}")
            
        except Exception as e:
            state["errors"].append(f"Stock analysis error: {str(e)}")
            state["stock_analysis"] = {"status": "error", "error": str(e)}
        
        return state
    
    async def _analyze_news(self, state: WorkflowState) -> WorkflowState:
        """Analyze news data using the News Analysis Agent"""
        try:
            symbol = state["symbol"]
            news_data = state["news_data"]
            
            if not news_data:
                state["errors"].append("No news data available for analysis")
                state["news_analysis"] = {"status": "error", "error": "No news data"}
            else:
                # Analyze news data
                news_analysis = self.news_agent.analyze_news(symbol, news_data)
                state["news_analysis"] = news_analysis
                
                if news_analysis.get("status") == "success":
                    state["status"] = "News analysis completed"
                else:
                    state["errors"].append(f"News analysis failed: {news_analysis.get('error', 'Unknown error')}")
            
        except Exception as e:
            state["errors"].append(f"News analysis error: {str(e)}")
            state["news_analysis"] = {"status": "error", "error": str(e)}
        
        return state
    
    async def _coordinate_analysis(self, state: WorkflowState) -> WorkflowState:
        """Coordinate analysis using the Coordinator Agent"""
        try:
            symbol = state["symbol"]
            stock_analysis = state["stock_analysis"]
            news_analysis = state["news_analysis"]
            
            # Coordinate the analysis
            final_analysis = self.coordinator_agent.coordinate_analysis(
                symbol, stock_analysis, news_analysis
            )
            
            state["final_analysis"] = final_analysis
            
            if final_analysis.get("status") == "success":
                state["status"] = "Analysis completed successfully"
            else:
                state["errors"].append(f"Coordination failed: {final_analysis.get('error', 'Unknown error')}")
            
        except Exception as e:
            state["errors"].append(f"Coordination error: {str(e)}")
            state["final_analysis"] = {"status": "error", "error": str(e)}
        
        return state
    
    async def _handle_errors(self, state: WorkflowState) -> WorkflowState:
        """Handle errors in the workflow"""
        state["status"] = f"Workflow failed with errors: {', '.join(state['errors'])}"
        return state
    
    async def run_analysis(self, symbol: str) -> WorkflowState:
        """Run the complete analysis workflow"""
        try:
            # Initialize the workflow state
            initial_state = WorkflowState(
                symbol=symbol.upper(),
                stock_data={},
                news_data=[],
                stock_analysis={},
                news_analysis={},
                final_analysis={},
                errors=[],
                status="Initialized"
            )
            
            # Run the workflow
            config = {"configurable": {"thread_id": f"analysis_{symbol}_{int(time.time())}"}}
            result = await self.workflow.ainvoke(initial_state, config)
            
            return result
            
        except Exception as e:
            return WorkflowState(
                symbol=symbol.upper(),
                stock_data={},
                news_data=[],
                stock_analysis={},
                news_analysis={},
                final_analysis={},
                errors=[f"Workflow execution failed: {str(e)}"],
                status="Failed"
            )
    
    def run_analysis_sync(self, symbol: str) -> WorkflowState:
        """Run the analysis workflow synchronously (for Streamlit compatibility)"""
        return asyncio.run(self.run_analysis(symbol))

# Utility function for Streamlit
def run_trading_analysis(symbol: str) -> Dict[str, Any]:
    """Run trading analysis and return results (Streamlit-friendly)"""
    try:
        workflow = LangGraphTradingWorkflow()
        result = workflow.run_analysis_sync(symbol)
        
        # Convert to regular dict for Streamlit
        return {
            'symbol': result['symbol'],
            'status': result['status'],
            'stock_data': result['stock_data'],
            'news_data': result['news_data'],
            'stock_analysis': result['stock_analysis'],
            'news_analysis': result['news_analysis'],
            'final_analysis': result['final_analysis'],
            'errors': result['errors']
        }
        
    except Exception as e:
        return {
            'symbol': symbol.upper(),
            'status': 'Failed',
            'error': str(e),
            'stock_data': {},
            'news_data': [],
            'stock_analysis': {},
            'news_analysis': {},
            'final_analysis': {},
            'errors': [str(e)]
        }
