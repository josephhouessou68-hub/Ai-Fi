import os
from langsmith import Client
from langsmith.run_trees import RunTree
from langsmith.run_helpers import traceable
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
from config import Config

class LangSmithTracker:
    """LangSmith integration for tracking and monitoring the trading system"""
    
    def __init__(self):
        self.client = Client(api_key=Config.LANGCHAIN_API_KEY)
        self.project_name = Config.LANGCHAIN_PROJECT
        self.enabled = Config.LANGCHAIN_TRACING_V2
        
        if not self.enabled:
            print("LangSmith tracing is disabled. Set LANGCHAIN_TRACING_V2=true to enable.")
    
    def start_run(self, run_name: str, inputs: Dict[str, Any], tags: List[str] = None) -> Optional[RunTree]:
        """Start a new LangSmith run"""
        if not self.enabled:
            return None
        
        try:
            run_tree = RunTree(
                name=run_name,
                inputs=inputs,
                tags=tags or [],
                project_name=self.project_name
            )
            return run_tree
        except Exception as e:
            print(f"Failed to start LangSmith run: {e}")
            return None
    
    def end_run(self, run_tree: Optional[RunTree], outputs: Dict[str, Any], error: Optional[str] = None):
        """End a LangSmith run"""
        if not self.enabled or not run_tree:
            return
        
        try:
            if error:
                run_tree.end(error=error)
            else:
                run_tree.end(outputs=outputs)
        except Exception as e:
            print(f"Failed to end LangSmith run: {e}")
    
    def log_agent_run(self, agent_name: str, symbol: str, inputs: Dict[str, Any], outputs: Dict[str, Any], 
                      error: Optional[str] = None, metadata: Dict[str, Any] = None):
        """Log a specific agent run"""
        if not self.enabled:
            return
        
        try:
            run_name = f"{agent_name}_{symbol}"
            tags = [agent_name, symbol, "agent_run"]
            
            run_tree = self.start_run(run_name, inputs, tags)
            
            if metadata:
                for key, value in metadata.items():
                    run_tree.add_metadata(key, value)
            
            self.end_run(run_tree, outputs, error)
            
        except Exception as e:
            print(f"Failed to log agent run: {e}")
    
    def log_workflow_run(self, symbol: str, workflow_state: Dict[str, Any], duration: float):
        """Log the complete workflow run"""
        if not self.enabled:
            return
        
        try:
            run_name = f"Trading_Analysis_Workflow_{symbol}"
            tags = ["workflow", symbol, "trading_analysis"]
            
            # Extract key metrics
            inputs = {
                "symbol": symbol,
                "timestamp": datetime.now().isoformat()
            }
            
            outputs = {
                "status": workflow_state.get("status", "unknown"),
                "duration_seconds": duration,
                "has_errors": len(workflow_state.get("errors", [])) > 0,
                "error_count": len(workflow_state.get("errors", [])),
                "stock_analysis_success": workflow_state.get("stock_analysis", {}).get("status") == "success",
                "news_analysis_success": workflow_state.get("news_analysis", {}).get("status") == "success",
                "final_analysis_success": workflow_state.get("final_analysis", {}).get("status") == "success"
            }
            
            # Add final analysis if available
            if workflow_state.get("final_analysis", {}).get("status") == "success":
                final_analysis = workflow_state["final_analysis"]["final_analysis"]
                outputs.update({
                    "recommendation": final_analysis.get("investment_recommendation", "Unknown"),
                    "risk_level": final_analysis.get("risk_level", "Unknown"),
                    "confidence_score": final_analysis.get("confidence_score", 0)
                })
            
            run_tree = self.start_run(run_name, inputs, tags)
            
            # Add metadata (simplified to avoid API issues)
            if run_tree:
                try:
                    run_tree.add_metadata({"workflow_type": "multi_agent_trading", "agent_count": 3})
                except:
                    pass  # Skip metadata if it fails
            
            self.end_run(run_tree, outputs)
            
        except Exception as e:
            print(f"Failed to log workflow run: {e}")
    
    def get_run_history(self, symbol: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get run history for analysis"""
        if not self.enabled:
            return []
        
        try:
            filters = {}
            if symbol:
                filters["tags"] = [symbol]
            
            runs = self.client.list_runs(
                project_name=self.project_name,
                filter=filters,
                limit=limit
            )
            
            run_history = []
            for run in runs:
                run_history.append({
                    "id": run.id,
                    "name": run.name,
                    "status": run.status,
                    "start_time": run.start_time.isoformat() if run.start_time else None,
                    "end_time": run.end_time.isoformat() if run.end_time else None,
                    "duration": run.duration.total_seconds() if run.duration else None,
                    "tags": run.tags,
                    "inputs": run.inputs,
                    "outputs": run.outputs,
                    "error": run.error
                })
            
            return run_history
            
        except Exception as e:
            print(f"Failed to get run history: {e}")
            return []
    
    def get_performance_metrics(self, symbol: str = None, days: int = 30) -> Dict[str, Any]:
        """Get performance metrics for the trading system"""
        if not self.enabled:
            return {}
        
        try:
            runs = self.get_run_history(symbol, limit=1000)
            
            if not runs:
                return {}
            
            # Calculate metrics
            total_runs = len(runs)
            successful_runs = len([r for r in runs if r["status"] == "completed"])
            failed_runs = len([r for r in runs if r["status"] == "failed"])
            
            # Calculate average duration
            durations = [r["duration"] for r in runs if r["duration"] is not None]
            avg_duration = sum(durations) / len(durations) if durations else 0
            
            # Calculate success rate by agent type
            agent_runs = {}
            for run in runs:
                agent_type = None
                if "StockAnalysisAgent" in run["name"]:
                    agent_type = "stock_analysis"
                elif "NewsAnalysisAgent" in run["name"]:
                    agent_type = "news_analysis"
                elif "CoordinatorAgent" in run["name"]:
                    agent_type = "coordinator"
                elif "workflow" in run["name"]:
                    agent_type = "workflow"
                
                if agent_type:
                    if agent_type not in agent_runs:
                        agent_runs[agent_type] = {"total": 0, "successful": 0}
                    
                    agent_runs[agent_type]["total"] += 1
                    if run["status"] == "completed":
                        agent_runs[agent_type]["successful"] += 1
            
            # Calculate success rates
            for agent_type in agent_runs:
                total = agent_runs[agent_type]["total"]
                successful = agent_runs[agent_type]["successful"]
                agent_runs[agent_type]["success_rate"] = (successful / total * 100) if total > 0 else 0
            
            return {
                "total_runs": total_runs,
                "successful_runs": successful_runs,
                "failed_runs": failed_runs,
                "overall_success_rate": (successful_runs / total_runs * 100) if total_runs > 0 else 0,
                "average_duration_seconds": avg_duration,
                "agent_performance": agent_runs,
                "analysis_period_days": days
            }
            
        except Exception as e:
            print(f"Failed to calculate performance metrics: {e}")
            return {}
    
    def replay_failed_run(self, run_id: str) -> Dict[str, Any]:
        """Replay a failed run for debugging"""
        if not self.enabled:
            return {"error": "LangSmith tracing is disabled"}
        
        try:
            # Get the failed run
            run = self.client.read_run(run_id)
            
            if not run:
                return {"error": "Run not found"}
            
            if run.status != "failed":
                return {"error": "Run is not failed, cannot replay"}
            
            # Extract the original inputs and configuration
            replay_data = {
                "run_id": run_id,
                "original_name": run.name,
                "original_inputs": run.inputs,
                "original_tags": run.tags,
                "error": run.error,
                "replay_timestamp": datetime.now().isoformat()
            }
            
            # Start a new replay run
            replay_run = self.start_run(
                f"Replay_{run.name}",
                run.inputs,
                run.tags + ["replay"]
            )
            
            if replay_run:
                replay_run.add_metadata("original_run_id", run_id)
                replay_run.add_metadata("replay_reason", "debugging_failed_run")
                
                # End the replay run
                self.end_run(replay_run, {"replay_data": replay_data})
                
                replay_data["replay_run_id"] = replay_run.id
                replay_data["status"] = "replay_started"
            
            return replay_data
            
        except Exception as e:
            return {"error": f"Failed to replay run: {str(e)}"}
    
    def export_run_data(self, symbol: str = None, format: str = "json") -> str:
        """Export run data for analysis"""
        if not self.enabled:
            return "LangSmith tracing is disabled"
        
        try:
            runs = self.get_run_history(symbol, limit=1000)
            
            if format.lower() == "json":
                return json.dumps(runs, indent=2, default=str)
            elif format.lower() == "csv":
                # Simple CSV export
                if not runs:
                    return "No data to export"
                
                headers = runs[0].keys()
                csv_lines = [",".join(headers)]
                
                for run in runs:
                    row = [str(run.get(header, "")) for header in headers]
                    csv_lines.append(",".join(row))
                
                return "\n".join(csv_lines)
            else:
                return f"Unsupported format: {format}"
                
        except Exception as e:
            return f"Export failed: {str(e)}"

# Decorator for tracing functions
def trace_function(func_name: str = None, tags: List[str] = None):
    """Decorator to trace function execution with LangSmith"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            tracker = LangSmithTracker()
            
            if not tracker.enabled:
                return func(*args, **kwargs)
            
            # Extract symbol from args if available
            symbol = None
            if args and isinstance(args[0], str):
                symbol = args[0]
            elif 'symbol' in kwargs:
                symbol = kwargs['symbol']
            
            run_name = func_name or f"{func.__name__}_{symbol or 'unknown'}"
            run_tags = tags or []
            if symbol:
                run_tags.append(symbol)
            
            # Start run
            run_tree = tracker.start_run(run_name, {"args": str(args), "kwargs": kwargs}, run_tags)
            
            try:
                result = func(*args, **kwargs)
                tracker.end_run(run_tree, {"result": str(result)})
                return result
            except Exception as e:
                tracker.end_run(run_tree, {}, str(e))
                raise
        
        return wrapper
    return decorator
