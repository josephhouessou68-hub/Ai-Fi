from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from typing import Dict, List, Any, Optional
import json
from config import Config

class StockAnalysisAgent:
    """Agent responsible for analyzing stock fundamentals and technical data"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=Config.OPENAI_MODEL,
            temperature=Config.TEMPERATURE,
            openai_api_key=Config.OPENAI_API_KEY
        )
        
        self.system_prompt = """You are a professional stock analyst with expertise in fundamental and technical analysis. 
        Your role is to analyze stock data and provide insights on:
        1. Company fundamentals (P/E ratio, market cap, financial health)
        2. Technical indicators and price trends
        3. Risk assessment
        4. Investment recommendation
        
        Always provide data-driven analysis and clearly state any assumptions or limitations."""
        
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", "Analyze the following stock data for {symbol}:\n\n{stock_data}\n\nProvide a comprehensive analysis including fundamentals, technical indicators, risks, and investment recommendation.")
        ])
    
    def analyze_stock(self, symbol: str, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze stock data and provide insights"""
        try:
            # Format stock data for analysis
            formatted_data = self._format_stock_data(stock_data)
            
            # Create messages for the LLM
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=f"Analyze the following stock data for {symbol}:\n\n{formatted_data}\n\nProvide a comprehensive analysis including fundamentals, technical indicators, risks, and investment recommendation.")
            ]
            
            # Get analysis from LLM
            response = self.llm.invoke(messages)
            
            # Parse and structure the response
            analysis = self._parse_analysis_response(response.content)
            
            return {
                'symbol': symbol,
                'analysis': analysis,
                'raw_response': response.content,
                'status': 'success'
            }
            
        except Exception as e:
            return {
                'symbol': symbol,
                'error': f"Analysis failed: {str(e)}",
                'status': 'error'
            }
    
    def _format_stock_data(self, stock_data: Dict[str, Any]) -> str:
        """Format stock data for LLM consumption"""
        if 'error' in stock_data:
            return f"Error in stock data: {stock_data['error']}"
        
        formatted = f"""
        Company: {stock_data.get('company_name', 'N/A')}
        Current Price: ${stock_data.get('current_price', 0):.2f}
        Change: ${stock_data.get('change', 0):.2f} ({stock_data.get('change_percent', 0):.2f}%)
        Market Cap: ${stock_data.get('market_cap', 0):,}
        P/E Ratio: {stock_data.get('pe_ratio', 'N/A')}
        Volume: {stock_data.get('volume', 0):,}
        52-Week High: ${stock_data.get('fifty_two_week_high', 0):.2f}
        52-Week Low: ${stock_data.get('fifty_two_week_low', 0):.2f}
        """
        
        if 'fundamentals' in stock_data and 'error' not in stock_data['fundamentals']:
            fundamentals = stock_data['fundamentals']
            formatted += f"""
        Financial Fundamentals:
        - Revenue: ${fundamentals.get('revenue', 0):,}
        - Net Income: ${fundamentals.get('net_income', 0):,}
        - Total Assets: ${fundamentals.get('total_assets', 0):,}
        - Total Debt: ${fundamentals.get('debt', 0):,}
        """
        
        return formatted
    
    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """Parse the LLM response into structured format"""
        # This is a simplified parser - in production, you might want to use structured output
        return {
            'summary': response[:200] + "..." if len(response) > 200 else response,
            'full_analysis': response,
            'key_points': self._extract_key_points(response),
            'recommendation': self._extract_recommendation(response)
        }
    
    def _extract_key_points(self, response: str) -> List[str]:
        """Extract key points from the analysis"""
        # Simple extraction - could be enhanced with more sophisticated parsing
        lines = response.split('\n')
        key_points = [line.strip() for line in lines if line.strip().startswith(('-', '•', '*'))]
        return key_points[:5]  # Limit to 5 key points
    
    def _extract_recommendation(self, response: str) -> str:
        """Extract investment recommendation from the analysis"""
        # Look for recommendation keywords
        recommendation_keywords = ['buy', 'sell', 'hold', 'strong buy', 'strong sell', 'outperform', 'underperform']
        response_lower = response.lower()
        
        for keyword in recommendation_keywords:
            if keyword in response_lower:
                return keyword.title()
        
        return "No clear recommendation"

class NewsAnalysisAgent:
    """Agent responsible for analyzing news sentiment and relevance"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=Config.OPENAI_MODEL,
            temperature=Config.TEMPERATURE,
            openai_api_key=Config.OPENAI_API_KEY
        )
        
        self.system_prompt = """You are a financial news analyst specializing in market sentiment analysis.
        Your role is to:
        1. Analyze news articles for relevance to specific stocks/companies
        2. Assess sentiment (positive, negative, neutral)
        3. Identify potential market impact
        4. Summarize key information
        
        Focus on factual analysis and avoid speculation."""
        
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", "Analyze the following news articles related to {symbol}:\n\n{news_data}\n\nProvide sentiment analysis, relevance assessment, and key insights.")
        ])
    
    def analyze_news(self, symbol: str, news_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze news data and provide sentiment analysis"""
        try:
            # Filter out error articles
            valid_news = [article for article in news_data if 'error' not in article]
            
            if not valid_news:
                return {
                    'symbol': symbol,
                    'error': 'No valid news articles found',
                    'status': 'error'
                }
            
            # Format news data for analysis
            formatted_news = self._format_news_data(valid_news)
            
            # Create messages for the LLM
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=f"Analyze the following news articles related to {symbol}:\n\n{formatted_news}\n\nProvide sentiment analysis, relevance assessment, and key insights.")
            ]
            
            # Get analysis from LLM
            response = self.llm.invoke(messages)
            
            # Parse and structure the response
            analysis = self._parse_news_analysis(response.content, valid_news)
            
            return {
                'symbol': symbol,
                'news_analysis': analysis,
                'raw_response': response.content,
                'articles_analyzed': len(valid_news),
                'status': 'success'
            }
            
        except Exception as e:
            return {
                'symbol': symbol,
                'error': f"News analysis failed: {str(e)}",
                'status': 'error'
            }
    
    def _format_news_data(self, news_data: List[Dict[str, Any]]) -> str:
        """Format news data for LLM consumption"""
        formatted = ""
        for i, article in enumerate(news_data[:10], 1):  # Limit to 10 articles
            formatted += f"""
        Article {i}:
        Title: {article.get('title', 'N/A')}
        Source: {article.get('source', 'N/A')}
        Published: {article.get('published_at', 'N/A')}
        Description: {article.get('description', 'N/A')}
        URL: {article.get('url', 'N/A')}
        """
        return formatted
    
    def _parse_news_analysis(self, response: str, news_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Parse the LLM response into structured format"""
        return {
            'summary': response[:300] + "..." if len(response) > 300 else response,
            'full_analysis': response,
            'sentiment': self._extract_sentiment(response),
            'key_insights': self._extract_key_insights(response),
            'market_impact': self._extract_market_impact(response)
        }
    
    def _extract_sentiment(self, response: str) -> str:
        """Extract overall sentiment from the analysis"""
        response_lower = response.lower()
        if any(word in response_lower for word in ['positive', 'bullish', 'favorable']):
            return "Positive"
        elif any(word in response_lower for word in ['negative', 'bearish', 'unfavorable']):
            return "Negative"
        else:
            return "Neutral"
    
    def _extract_key_insights(self, response: str) -> List[str]:
        """Extract key insights from the analysis"""
        lines = response.split('\n')
        insights = [line.strip() for line in lines if line.strip().startswith(('-', '•', '*'))]
        return insights[:5]
    
    def _extract_market_impact(self, response: str) -> str:
        """Extract potential market impact assessment"""
        response_lower = response.lower()
        if any(word in response_lower for word in ['high impact', 'significant', 'major']):
            return "High"
        elif any(word in response_lower for word in ['moderate impact', 'moderate']):
            return "Moderate"
        elif any(word in response_lower for word in ['low impact', 'minimal']):
            return "Low"
        else:
            return "Unclear"

class CoordinatorAgent:
    """Agent responsible for coordinating and merging results from other agents"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=Config.OPENAI_MODEL,
            temperature=Config.TEMPERATURE,
            openai_api_key=Config.OPENAI_API_KEY
        )
        
        self.system_prompt = """You are a senior investment analyst and portfolio manager.
        Your role is to synthesize information from multiple sources and provide:
        1. Comprehensive investment analysis
        2. Risk assessment
        3. Clear investment recommendation
        4. Actionable insights
        
        Consider both fundamental and sentiment factors in your analysis."""
        
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", "Synthesize the following analysis for {symbol}:\n\nStock Analysis: {stock_analysis}\n\nNews Analysis: {news_analysis}\n\nProvide a comprehensive investment recommendation and analysis.")
        ])
    
    def coordinate_analysis(self, symbol: str, stock_analysis: Dict[str, Any], news_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate and merge analysis from multiple agents"""
        try:
            # Check if we have valid data from both agents
            if stock_analysis.get('status') == 'error' and news_analysis.get('status') == 'error':
                return {
                    'symbol': symbol,
                    'error': 'Both stock and news analysis failed',
                    'status': 'error'
                }
            
            # Create messages for the LLM
            stock_summary = stock_analysis.get('analysis', {}).get('summary', 'No stock analysis available')
            news_summary = news_analysis.get('news_analysis', {}).get('summary', 'No news analysis available')
            
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=f"""Synthesize the following analysis for {symbol}:

Stock Analysis: {stock_summary}

News Analysis: {news_summary}

Provide a comprehensive investment recommendation and analysis.""")
            ]
            
            # Get coordinated analysis from LLM
            response = self.llm.invoke(messages)
            
            # Create final recommendation
            final_analysis = self._create_final_analysis(symbol, stock_analysis, news_analysis, response.content)
            
            return {
                'symbol': symbol,
                'final_analysis': final_analysis,
                'raw_response': response.content,
                'status': 'success',
                'timestamp': self._get_timestamp()
            }
            
        except Exception as e:
            return {
                'symbol': symbol,
                'error': f"Coordination failed: {str(e)}",
                'status': 'error'
            }
    
    def _create_final_analysis(self, symbol: str, stock_analysis: Dict[str, Any], news_analysis: Dict[str, Any], llm_response: str) -> Dict[str, Any]:
        """Create the final comprehensive analysis"""
        return {
            'symbol': symbol,
            'investment_recommendation': self._extract_recommendation(llm_response),
            'risk_level': self._assess_risk_level(stock_analysis, news_analysis),
            'confidence_score': self._calculate_confidence(stock_analysis, news_analysis),
            'key_factors': self._extract_key_factors(llm_response),
            'summary': llm_response[:400] + "..." if len(llm_response) > 400 else llm_response,
            'full_analysis': llm_response
        }
    
    def _extract_recommendation(self, response: str) -> str:
        """Extract investment recommendation from the coordinated analysis"""
        response_lower = response.lower()
        if 'buy' in response_lower and 'strong' in response_lower:
            return "Strong Buy"
        elif 'buy' in response_lower:
            return "Buy"
        elif 'sell' in response_lower and 'strong' in response_lower:
            return "Strong Sell"
        elif 'sell' in response_lower:
            return "Sell"
        elif 'hold' in response_lower:
            return "Hold"
        else:
            return "No clear recommendation"
    
    def _assess_risk_level(self, stock_analysis: Dict[str, Any], news_analysis: Dict[str, Any]) -> str:
        """Assess overall risk level based on available data"""
        # Simple risk assessment - could be enhanced with more sophisticated logic
        if stock_analysis.get('status') == 'error' or news_analysis.get('status') == 'error':
            return "High (Insufficient data)"
        
        # Check for negative indicators
        stock_data = stock_analysis.get('analysis', {})
        news_data = news_analysis.get('news_analysis', {})
        
        negative_indicators = 0
        
        # Stock indicators
        if stock_data.get('recommendation', '').lower() in ['sell', 'strong sell']:
            negative_indicators += 2
        
        # News indicators
        if news_data.get('sentiment') == 'Negative':
            negative_indicators += 1
        
        if negative_indicators >= 2:
            return "High"
        elif negative_indicators == 1:
            return "Medium"
        else:
            return "Low"
    
    def _calculate_confidence(self, stock_analysis: Dict[str, Any], news_analysis: Dict[str, Any]) -> int:
        """Calculate confidence score (0-100) based on data quality"""
        confidence = 50  # Base confidence
        
        # Add confidence for successful analysis
        if stock_analysis.get('status') == 'success':
            confidence += 25
        
        if news_analysis.get('status') == 'success':
            confidence += 25
        
        return min(confidence, 100)
    
    def _extract_key_factors(self, response: str) -> List[str]:
        """Extract key factors from the coordinated analysis"""
        lines = response.split('\n')
        factors = [line.strip() for line in lines if line.strip().startswith(('-', '•', '*'))]
        return factors[:5]
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()

class RetrievalQASystem:
    """RetrievalQA system for combining knowledge from multiple sources"""
    
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(openai_api_key=Config.OPENAI_API_KEY)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        self.vectorstore = None
    
    def create_knowledge_base(self, documents: List[Dict[str, Any]]) -> None:
        """Create a knowledge base from documents"""
        try:
            # Convert documents to LangChain Document format
            docs = []
            for doc in documents:
                if isinstance(doc, dict):
                    content = json.dumps(doc, default=str)
                    docs.append(Document(page_content=content, metadata={'source': 'trading_data'}))
            
            # Split documents into chunks
            if docs:
                split_docs = self.text_splitter.split_documents(docs)
                
                # Create vector store
                self.vectorstore = FAISS.from_documents(split_docs, self.embeddings)
            
        except Exception as e:
            print(f"Error creating knowledge base: {e}")
    
    def query_knowledge_base(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Query the knowledge base for relevant information"""
        if not self.vectorstore:
            return []
        
        try:
            # Search for similar documents
            docs = self.vectorstore.similarity_search(query, k=k)
            
            # Convert back to dictionary format
            results = []
            for doc in docs:
                try:
                    data = json.loads(doc.page_content)
                    results.append(data)
                except:
                    results.append({'content': doc.page_content, 'metadata': doc.metadata})
            
            return results
            
        except Exception as e:
            print(f"Error querying knowledge base: {e}")
            return []
