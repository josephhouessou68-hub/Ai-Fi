"""
Visualize LangGraph Workflow Structure
"""

import streamlit as st
from langgraph_workflow import LangGraphTradingWorkflow
import plotly.graph_objects as go
import networkx as nx
from datetime import datetime

st.set_page_config(
    page_title="LangGraph Workflow Visualizer",
    page_icon="🕸️",
    layout="wide"
)

def create_workflow_graph():
    """Create a visual representation of the LangGraph workflow"""
    
    # Define the workflow structure
    nodes = [
        {"id": "start", "label": "START", "type": "start", "x": 1, "y": 3},
        {"id": "fetch_stock_data", "label": "Fetch Stock Data", "type": "process", "x": 2, "y": 3},
        {"id": "fetch_news_data", "label": "Fetch News Data", "type": "process", "x": 3, "y": 3},
        {"id": "analyze_stock", "label": "Analyze Stock", "type": "agent", "x": 4, "y": 4},
        {"id": "analyze_news", "label": "Analyze News", "type": "agent", "x": 4, "y": 2},
        {"id": "coordinate_analysis", "label": "Coordinate Analysis", "type": "agent", "x": 5, "y": 3},
        {"id": "end", "label": "END", "type": "end", "x": 6, "y": 3}
    ]
    
    edges = [
        {"from": "start", "to": "fetch_stock_data"},
        {"from": "fetch_stock_data", "to": "fetch_news_data"},
        {"from": "fetch_news_data", "to": "analyze_stock"},
        {"from": "fetch_news_data", "to": "analyze_news"},
        {"from": "analyze_stock", "to": "coordinate_analysis"},
        {"from": "analyze_news", "to": "coordinate_analysis"},
        {"from": "coordinate_analysis", "to": "end"}
    ]
    
    return nodes, edges

def create_plotly_graph(nodes, edges):
    """Create a Plotly graph of the workflow"""
    
    # Create traces for edges
    edge_trace = []
    for edge in edges:
        from_node = next(n for n in nodes if n["id"] == edge["from"])
        to_node = next(n for n in nodes if n["id"] == edge["to"])
        
        edge_trace.append(go.Scatter(
            x=[from_node["x"], to_node["x"], None],
            y=[from_node["y"], to_node["y"], None],
            mode='lines',
            line=dict(width=2, color='#888'),
            hoverinfo='none',
            showlegend=False
        ))
    
    # Create node trace
    node_x = [node["x"] for node in nodes]
    node_y = [node["y"] for node in nodes]
    node_text = [node["label"] for node in nodes]
    node_colors = []
    node_sizes = []
    
    for node in nodes:
        if node["type"] == "start":
            node_colors.append('#00ff00')
            node_sizes.append(30)
        elif node["type"] == "end":
            node_colors.append('#ff0000')
            node_sizes.append(30)
        elif node["type"] == "agent":
            node_colors.append('#0099ff')
            node_sizes.append(40)
        else:
            node_colors.append('#ffaa00')
            node_sizes.append(35)
    
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=node_text,
        textposition="middle center",
        marker=dict(
            size=node_sizes,
            color=node_colors,
            line=dict(width=2, color='white')
        ),
        hovertemplate='<b>%{text}</b><extra></extra>',
        showlegend=False
    )
    
    # Create the figure
    fig = go.Figure(data=edge_trace + [node_trace])
    
    fig.update_layout(
        title="🕸️ LangGraph Trading Workflow",
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20,l=5,r=5,t=40),
        annotations=[ dict(
            text="LangGraph Multi-Agent Trading Workflow",
            showarrow=False,
            xref="paper", yref="paper",
            x=0.005, y=-0.002,
            xanchor='left', yanchor='bottom',
            font=dict(color="gray", size=12)
        )],
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=600
    )
    
    return fig

def create_mermaid_diagram():
    """Create a Mermaid diagram of the workflow"""
    mermaid_code = """
    graph TD
        A[START] --> B[Fetch Stock Data]
        B --> C[Fetch News Data]
        C --> D[Analyze Stock]
        C --> E[Analyze News]
        D --> F[Coordinate Analysis]
        E --> F
        F --> G[END]
        
        style A fill:#90EE90
        style G fill:#FFB6C1
        style D fill:#87CEEB
        style E fill:#87CEEB
        style F fill:#DDA0DD
    """
    return mermaid_code

def main():
    st.title("🕸️ LangGraph Workflow Visualizer")
    st.markdown("**Visual representation of the multi-agent trading workflow**")
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["📊 Interactive Graph", "🎨 Mermaid Diagram", "📋 Workflow Details"])
    
    with tab1:
        st.subheader("Interactive Workflow Graph")
        
        nodes, edges = create_workflow_graph()
        fig = create_plotly_graph(nodes, edges)
        st.plotly_chart(fig, use_container_width=True)
        
        # Legend
        st.subheader("🏷️ Legend")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("🟢 **Start/End Nodes**")
        with col2:
            st.markdown("🟠 **Data Fetching**")
        with col3:
            st.markdown("🔵 **AI Agents**")
        with col4:
            st.markdown("➡️ **Flow Direction**")
    
    with tab2:
        st.subheader("Mermaid Workflow Diagram")
        
        mermaid_code = create_mermaid_diagram()
        st.code(mermaid_code, language="mermaid")
        
        st.markdown("**Copy this code to visualize in Mermaid Live Editor:**")
        st.markdown("[🔗 Open Mermaid Live Editor](https://mermaid.live/)")
    
    with tab3:
        st.subheader("📋 Workflow Details")
        
        # Node details
        st.markdown("### Workflow Nodes")
        
        node_details = [
            {"Node": "START", "Type": "Entry Point", "Description": "Workflow initialization"},
            {"Node": "Fetch Stock Data", "Type": "Data Collection", "Description": "Get stock prices, fundamentals from Yahoo Finance/Polygon"},
            {"Node": "Fetch News Data", "Type": "Data Collection", "Description": "Get financial news from NewsAPI/Bing Search"},
            {"Node": "Analyze Stock", "Type": "AI Agent", "Description": "Stock Analysis Agent - fundamentals, technical analysis"},
            {"Node": "Analyze News", "Type": "AI Agent", "Description": "News Analysis Agent - sentiment, market impact"},
            {"Node": "Coordinate Analysis", "Type": "AI Agent", "Description": "Coordinator Agent - merge results, final recommendation"},
            {"Node": "END", "Type": "Exit Point", "Description": "Workflow completion with final results"}
        ]
        
        import pandas as pd
        df = pd.DataFrame(node_details)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Agent details
        st.markdown("### 🤖 AI Agents")
        
        agent_details = [
            {
                "Agent": "Stock Analysis Agent",
                "Purpose": "Analyze stock fundamentals and technical indicators",
                "Inputs": "Stock price data, financial metrics, historical data",
                "Outputs": "Investment recommendation, risk assessment, key insights"
            },
            {
                "Agent": "News Analysis Agent", 
                "Purpose": "Analyze news sentiment and market impact",
                "Inputs": "Financial news articles, market sentiment data",
                "Outputs": "Sentiment score, market impact assessment, key insights"
            },
            {
                "Agent": "Coordinator Agent",
                "Purpose": "Synthesize all analysis into final recommendation",
                "Inputs": "Stock analysis results, news analysis results",
                "Outputs": "Final investment recommendation, confidence score, risk level"
            }
        ]
        
        agent_df = pd.DataFrame(agent_details)
        st.dataframe(agent_df, use_container_width=True, hide_index=True)
        
        # State flow
        st.markdown("### 🔄 State Flow")
        
        state_flow = [
            {"Step": 1, "State Change": "Initialize workflow state with symbol"},
            {"Step": 2, "State Change": "Add stock data to state"},
            {"Step": 3, "State Change": "Add news data to state"},
            {"Step": 4, "State Change": "Add stock analysis results to state"},
            {"Step": 5, "State Change": "Add news analysis results to state"},
            {"Step": 6, "State Change": "Add final coordinated analysis to state"}
        ]
        
        state_df = pd.DataFrame(state_flow)
        st.dataframe(state_df, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    main()
