# 📁 LangChain Trading Analysis - Project Structure

## 🏗️ **Core Application Files**

### **Main Applications**
- `app.py` - Main Streamlit trading analysis application with full AI features
- `app_fast.py` - Fast analysis version for quick stock insights (<5 seconds)

### **Visualization & Monitoring**
- `visualize_langgraph.py` - Interactive LangGraph workflow visualization
- `state_monitor_demo.py` - State monitoring dashboard with sample data
- `state_inspector.py` - State inspection utilities and debugging tools

### **Core Framework Components**
- `langgraph_workflow.py` - Multi-agent workflow orchestration using LangGraph
- `agents.py` - AI agents (Stock Analysis, News Analysis, Coordinator)
- `api_clients.py` - API clients for stock data (Yahoo Finance, Polygon) and news
- `langsmith_integration.py` - Performance monitoring and error tracking

### **Configuration & Testing**
- `config.py` - Application configuration and environment management
- `test_system.py` - System validation and health checks

### **Documentation**
- `README.md` - Comprehensive project documentation and setup guide
- `PROJECT_STRUCTURE.md` - This file - project organization overview
- `.gitignore` - Git ignore patterns for Python/Streamlit projects

### **Dependencies**
- `requirements.txt` - Python package dependencies with version specifications

## 🎯 **Application Entry Points**

### **For End Users:**
```bash
# Main Trading Analysis (Full AI Features)
streamlit run app.py

# Fast Analysis (Quick Results)
streamlit run app_fast.py --server.port 8502
```

### **For Developers & Monitoring:**
```bash
# LangGraph Workflow Visualization
streamlit run visualize_langgraph.py --server.port 8511

# State Monitoring Dashboard
streamlit run state_monitor_demo.py --server.port 8510

# System Health Check
python test_system.py
```

## 🧠 **Architecture Overview**

### **Multi-Agent System (LangGraph)**
```
START → Fetch Stock Data → Fetch News Data → Analyze Stock   → Coordinate → END
                                           → Analyze News    → Analysis  →
```

### **AI Agents**
1. **Stock Analysis Agent** - Analyzes fundamentals, technical indicators
2. **News Analysis Agent** - Processes news sentiment and market impact  
3. **Coordinator Agent** - Synthesizes results into final recommendations

### **Data Sources**
- **Yahoo Finance** - Real-time stock prices and fundamentals
- **Polygon.io** - Enhanced financial data (optional)
- **NewsAPI** - Financial news and sentiment data (optional)

### **Monitoring & Observability**
- **LangSmith** - Performance tracking and error monitoring
- **State Inspector** - Real-time workflow state debugging
- **Interactive Visualizations** - Workflow and progress charts

## 📦 **Technology Stack**

### **Core Framework**
- **LangChain** - AI agent framework and LLM orchestration
- **LangGraph** - Multi-agent workflow management
- **LangSmith** - Observability and performance monitoring

### **Frontend & Visualization**
- **Streamlit** - Web application framework
- **Plotly** - Interactive charts and graphs
- **Pandas** - Data manipulation and analysis

### **AI & Language Models**
- **OpenAI GPT-4** - Primary language model for analysis
- **OpenAI Embeddings** - Vector embeddings for retrieval

### **Data Sources**
- **yfinance** - Yahoo Finance API client
- **polygon-api-client** - Polygon.io API integration
- **newsapi-python** - News API client

## 🔧 **Development Workflow**

### **Setup**
1. Install dependencies: `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and configure API keys
3. Run system test: `python test_system.py`
4. Launch application: `streamlit run app.py`

### **Testing & Validation**
- System health: `python test_system.py`
- Component testing: Individual agent testing in `agents.py`
- Integration testing: Full workflow validation

### **Monitoring & Debugging**
- Real-time state monitoring via `state_monitor_demo.py`
- LangSmith dashboard for performance analytics
- Console logging for detailed execution traces

## 🌐 **Deployment Considerations**

### **Environment Variables**
- `OPENAI_API_KEY` - Required for AI functionality
- `LANGCHAIN_API_KEY` - Optional for monitoring
- Financial API keys - Optional for enhanced data

### **Port Configuration**
- Main app: 8501 (default)
- Fast app: 8502
- State monitor: 8510
- Workflow visualizer: 8511

### **Scalability**
- Caching implemented for API responses
- Async workflow execution
- Modular agent architecture for easy scaling

## 📋 **Maintenance & Updates**

### **Regular Tasks**
- Monitor API usage and rate limits
- Update dependency versions
- Review and optimize LLM prompts
- Analyze performance metrics via LangSmith

### **Troubleshooting**
- Check `test_system.py` for component health
- Review LangSmith logs for agent performance
- Use state monitor for workflow debugging
- Validate API key configuration in `config.py`
