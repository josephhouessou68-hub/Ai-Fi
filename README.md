# 📈 LangChain Trading Analysis System

A comprehensive AI-powered trading analysis system built with LangChain, LangGraph, and LangSmith, featuring a beautiful Streamlit interface for multi-agent stock analysis.

## 🚀 Features

### **LangChain Integration**
- **Retrieval + Reasoning**: Combines knowledge from multiple sources using RetrievalQA chains
- **Multi-source Data**: Connects to Yahoo Finance, Polygon.io, NewsAPI, and Bing Search
- **Intelligent Analysis**: Uses OpenAI GPT models for comprehensive financial analysis

### **LangGraph Multi-Agent Workflow**
- **Stock Analysis Agent**: Analyzes stock fundamentals, technical indicators, and financial health
- **News Analysis Agent**: Processes news sentiment and market impact assessment
- **Coordinator Agent**: Synthesizes all analysis into final investment recommendations

### **LangSmith Monitoring**
- **Performance Tracking**: Monitors agent performance and workflow success rates
- **Error Handling**: Automatic replay of failed runs for debugging
- **Metrics Dashboard**: Real-time performance analytics and insights

### **Streamlit Interface**
- **Beautiful UI**: Modern, responsive design with interactive charts
- **Real-time Analysis**: Live stock data and news analysis
- **Performance Metrics**: Built-in monitoring and analytics dashboard


## 🛠️ Installation

### Prerequisites
- Python 3.8+
- OpenAI API Key
- LangSmith API Key (optional but recommended)
- NewsAPI Key (optional)
- Polygon.io API Key (optional)

### Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd langchain-trading
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
cp .env.example .env
```

Edit `.env` file with your API keys:
```env
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional but recommended
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=langchain-trading

# Optional APIs for enhanced functionality
POLYGON_API_KEY=your_polygon_api_key_here
NEWS_API_KEY=your_news_api_key_here
BING_SEARCH_API_KEY=your_bing_search_api_key_here
```

4. **Run the application**
```bash
streamlit run app.py
```

## 🔑 API Keys Setup

### Required APIs
- **OpenAI**: [Get API Key](https://platform.openai.com/api-keys)
  - Used for all AI analysis and reasoning
  - Supports GPT-4 and other models

### Optional APIs (for enhanced functionality)
- **LangSmith**: [Get API Key](https://smith.langchain.com/)
  - Enables performance monitoring and debugging
  - Provides run history and metrics

- **NewsAPI**: [Get API Key](https://newsapi.org/)
  - Provides financial news and sentiment data
  - Enhances news analysis capabilities

- **Polygon.io**: [Get API Key](https://polygon.io/)
  - Provides detailed financial data and fundamentals
  - Enhances stock analysis accuracy

## 📊 Usage

### Basic Stock Analysis
1. Enter a stock symbol (e.g., AAPL, MSFT, GOOGL)
2. Click "Run Analysis"
3. View comprehensive analysis results

### Analysis Components
- **Stock Data**: Real-time price, volume, and fundamental metrics
- **Technical Analysis**: Price trends, support/resistance levels
- **News Sentiment**: Market sentiment and impact assessment
- **Investment Recommendation**: AI-generated buy/sell/hold advice

### Monitoring & Debugging
- **Performance Metrics**: View agent success rates and response times
- **Run History**: Track all analysis runs and their outcomes
- **Error Replay**: Automatically retry failed analyses

## 🧠 Multi-Agent System

### Stock Analysis Agent
- Analyzes financial fundamentals (P/E ratio, market cap, debt levels)
- Evaluates technical indicators and price trends
- Provides risk assessment and investment recommendations

### News Analysis Agent
- Processes financial news articles for relevance
- Assesses sentiment (positive/negative/neutral)
- Evaluates potential market impact

### Coordinator Agent
- Synthesizes analysis from all agents
- Provides final investment recommendation
- Calculates confidence scores and risk levels

## 📈 LangSmith Integration

### Performance Monitoring
- Track agent success rates and response times
- Monitor workflow completion rates
- Identify bottlenecks and optimization opportunities

### Error Handling
- Automatic replay of failed runs
- Detailed error logging and debugging
- Performance trend analysis

### Analytics Dashboard
- Real-time metrics and KPIs
- Historical performance data
- Agent performance comparison

## 🚀 Advanced Features

### RetrievalQA System
- Creates knowledge base from analysis results
- Enables semantic search across historical analyses
- Supports complex financial queries

### Custom Prompts
- Configurable system prompts for each agent
- Adjustable analysis depth and focus areas
- Customizable output formats

### Batch Processing
- Analyze multiple stocks simultaneously
- Portfolio-level analysis and recommendations
- Comparative analysis across sectors

## 🔧 Configuration

### Model Settings
```python
# In config.py
OPENAI_MODEL = "gpt-4"  # or "gpt-3.5-turbo"
TEMPERATURE = 0.1        # Lower = more focused analysis
```

### API Timeouts
```python
REQUEST_TIMEOUT = 30     # API request timeout in seconds
```

### Analysis Options
- News analysis period (default: 7 days)
- Fundamental data depth
- Technical indicator selection

## 📊 Performance Optimization

### Caching
- Stock data caching to reduce API calls
- Analysis result caching for repeated queries
- Vector store optimization for knowledge retrieval

### Parallel Processing
- Concurrent agent execution
- Async API calls for improved performance
- Background task processing

### Error Recovery
- Automatic retry mechanisms
- Graceful degradation for API failures
- Fallback data sources

## 🧪 Testing

### Unit Tests
```bash
python -m pytest tests/
```

### Integration Tests
```bash
python -m pytest tests/integration/
```

### Performance Tests
```bash
python -m pytest tests/performance/
```

## 📚 API Documentation

### Stock Analysis
```python
from langgraph_workflow import run_trading_analysis

# Run complete analysis
results = run_trading_analysis("AAPL")

# Access specific components
stock_data = results['stock_data']
news_analysis = results['news_analysis']
final_recommendation = results['final_analysis']
```

### LangSmith Monitoring
```python
from langsmith_integration import LangSmithTracker

tracker = LangSmithTracker()
metrics = tracker.get_performance_metrics()
runs = tracker.get_run_history()
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Common Issues
- **API Key Errors**: Ensure all required API keys are configured in `.env`
- **Rate Limiting**: Check API usage limits and implement appropriate delays
- **Memory Issues**: Large datasets may require increased memory allocation

### Getting Help
- Check the [Issues](https://github.com/your-repo/issues) page
- Review the [Documentation](docs/)
- Join our [Discord Community](https://discord.gg/your-community)

## 🎯 Roadmap

### Phase 1 (Current)
- ✅ Multi-agent trading analysis
- ✅ LangSmith integration
- ✅ Streamlit interface
- ✅ Basic error handling

### Phase 2 (Next)
- 🔄 Portfolio analysis
- 🔄 Real-time alerts
- 🔄 Advanced technical indicators
- 🔄 Machine learning models

### Phase 3 (Future)
- 📋 Options analysis
- 📋 Cryptocurrency support
- 📋 Social sentiment analysis
- 📋 Automated trading signals

## 🙏 Acknowledgments

- **LangChain Team** for the amazing framework
- **OpenAI** for GPT models
- **Streamlit** for the beautiful UI framework
- **Financial APIs** for data access

---

**Disclaimer**: This system is for educational and research purposes only. Investment decisions should not be based solely on automated analysis. Always consult with qualified financial advisors.
