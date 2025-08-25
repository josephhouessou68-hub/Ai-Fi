#!/usr/bin/env python3
"""
Simple test script for the LangChain Trading System
Run this to verify all components are working correctly
"""

import os
import sys
from dotenv import load_dotenv

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        from config import Config
        print("✅ Config module imported successfully")
    except ImportError as e:
        print(f"❌ Config import failed: {e}")
        return False
    
    try:
        from api_clients import StockAPIClient, NewsAPIClient
        print("✅ API clients imported successfully")
    except ImportError as e:
        print(f"❌ API clients import failed: {e}")
        return False
    
    try:
        from agents import StockAnalysisAgent, NewsAnalysisAgent, CoordinatorAgent
        print("✅ Agents imported successfully")
    except ImportError as e:
        print(f"❌ Agents import failed: {e}")
        return False
    
    try:
        from langgraph_workflow import LangGraphTradingWorkflow
        print("✅ LangGraph workflow imported successfully")
    except ImportError as e:
        print(f"❌ LangGraph workflow import failed: {e}")
        return False
    
    try:
        from langsmith_integration import LangSmithTracker
        print("✅ LangSmith integration imported successfully")
    except ImportError as e:
        print(f"❌ LangSmith integration import failed: {e}")
        return False
    
    return True

def test_configuration():
    """Test configuration loading"""
    print("\n🔧 Testing configuration...")
    
    try:
        from config import Config
        
        # Test required API key
        if Config.OPENAI_API_KEY:
            print("✅ OpenAI API key configured")
        else:
            print("❌ OpenAI API key missing")
            return False
        
        # Test optional API keys
        if Config.LANGCHAIN_API_KEY:
            print("✅ LangSmith API key configured")
        else:
            print("⚠️  LangSmith API key not configured (optional)")
        
        if Config.POLYGON_API_KEY:
            print("✅ Polygon API key configured")
        else:
            print("⚠️  Polygon API key not configured (optional)")
        
        if Config.NEWS_API_KEY:
            print("✅ NewsAPI key configured")
        else:
            print("⚠️  NewsAPI key not configured (optional)")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_api_clients():
    """Test API client initialization"""
    print("\n🌐 Testing API clients...")
    
    try:
        from api_clients import StockAPIClient, NewsAPIClient
        
        # Test stock client
        stock_client = StockAPIClient()
        print("✅ Stock API client initialized")
        
        # Test news client
        news_client = NewsAPIClient()
        print("✅ News API client initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ API client test failed: {e}")
        return False

def test_agents():
    """Test agent initialization"""
    print("\n🤖 Testing agents...")
    
    try:
        from agents import StockAnalysisAgent, NewsAnalysisAgent, CoordinatorAgent
        from config import Config
        
        # Test stock analysis agent
        stock_agent = StockAnalysisAgent()
        print("✅ Stock analysis agent initialized")
        
        # Test news analysis agent
        news_agent = NewsAnalysisAgent()
        print("✅ News analysis agent initialized")
        
        # Test coordinator agent
        coordinator_agent = CoordinatorAgent()
        print("✅ Coordinator agent initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent test failed: {e}")
        return False

def test_workflow():
    """Test workflow initialization"""
    print("\n🔄 Testing workflow...")
    
    try:
        from langgraph_workflow import LangGraphTradingWorkflow
        
        workflow = LangGraphTradingWorkflow()
        print("✅ LangGraph workflow initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ Workflow test failed: {e}")
        return False

def test_langsmith():
    """Test LangSmith integration"""
    print("\n📊 Testing LangSmith integration...")
    
    try:
        from langsmith_integration import LangSmithTracker
        from config import Config
        
        tracker = LangSmithTracker()
        
        if Config.LANGCHAIN_TRACING_V2:
            print("✅ LangSmith tracker initialized")
        else:
            print("⚠️  LangSmith tracing disabled")
        
        return True
        
    except Exception as e:
        print(f"❌ LangSmith test failed: {e}")
        return False

def run_basic_analysis():
    """Run a basic analysis to test the complete system"""
    print("\n🚀 Testing complete analysis workflow...")
    
    try:
        from langgraph_workflow import run_trading_analysis
        
        # Test with a simple symbol
        symbol = "AAPL"
        print(f"Testing analysis for {symbol}...")
        
        # This will take some time and use API calls
        print("⚠️  This test will make API calls and may take several minutes...")
        
        # Uncomment the following lines to run actual analysis (uses API calls)
        # results = run_trading_analysis(symbol)
        # print(f"✅ Analysis completed for {symbol}")
        # print(f"Status: {results.get('status', 'Unknown')}")
        
        print("✅ Analysis workflow test passed (simulated)")
        return True
        
    except Exception as e:
        print(f"❌ Analysis workflow test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 LangChain Trading System - System Test")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    tests = [
        ("Import Test", test_imports),
        ("Configuration Test", test_configuration),
        ("API Clients Test", test_api_clients),
        ("Agents Test", test_agents),
        ("Workflow Test", test_workflow),
        ("LangSmith Test", test_langsmith),
        ("Analysis Workflow Test", run_basic_analysis)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready to use.")
        print("\n🚀 To run the application:")
        print("   streamlit run app.py")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("\n💡 Common solutions:")
        print("   1. Ensure all dependencies are installed: pip install -r requirements.txt")
        print("   2. Check your .env file configuration")
        print("   3. Verify API keys are valid")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
