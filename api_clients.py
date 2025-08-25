import yfinance as yf
import requests
import pandas as pd
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import time
from config import Config
import concurrent.futures
from functools import lru_cache

class StockAPIClient:
    """Client for fetching stock market data from multiple sources"""
    
    def __init__(self):
        self.polygon_api_key = Config.POLYGON_API_KEY
        self.timeout = Config.REQUEST_TIMEOUT
    
    @lru_cache(maxsize=32)
    def get_basic_stock_info(self, symbol: str) -> Dict[str, Any]:
        """Get basic stock info quickly (cached)"""
        try:
            ticker = yf.Ticker(symbol)
            # Get just the essential info quickly
            info = ticker.fast_info
            
            return {
                'symbol': symbol,
                'current_price': info.get('last_price', 0),
                'previous_close': info.get('previous_close', 0),
                'change': info.get('last_price', 0) - info.get('previous_close', 0),
                'change_percent': ((info.get('last_price', 0) - info.get('previous_close', 0)) / info.get('previous_close', 1)) * 100,
                'volume': info.get('day_volume', 0),
                'market_cap': info.get('market_cap', 0),
                'source': 'Yahoo Finance (Fast)'
            }
        except Exception as e:
            return {
                'symbol': symbol,
                'error': f"Failed to fetch basic data: {str(e)}",
                'source': 'Yahoo Finance (Fast)'
            }
    
    def get_stock_info_yahoo(self, symbol: str) -> Dict[str, Any]:
        """Get stock information using Yahoo Finance"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Get historical data
            hist = ticker.history(period="1y")
            
            # Calculate basic metrics
            current_price = info.get('currentPrice', 0)
            previous_close = info.get('previousClose', 0)
            change = current_price - previous_close
            change_percent = (change / previous_close * 100) if previous_close else 0
            
            return {
                'symbol': symbol,
                'company_name': info.get('longName', 'N/A'),
                'current_price': current_price,
                'previous_close': previous_close,
                'change': round(change, 2),
                'change_percent': round(change_percent, 2),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'volume': info.get('volume', 0),
                'avg_volume': info.get('averageVolume', 0),
                'fifty_two_week_high': info.get('fiftyTwoWeekHigh', 0),
                'fifty_two_week_low': info.get('fiftyTwoWeekLow', 0),
                'historical_data': hist.to_dict('records') if not hist.empty else [],
                'source': 'Yahoo Finance'
            }
        except Exception as e:
            return {
                'symbol': symbol,
                'error': f"Failed to fetch data from Yahoo Finance: {str(e)}",
                'source': 'Yahoo Finance'
            }
    
    def get_stock_fundamentals_polygon(self, symbol: str) -> Dict[str, Any]:
        """Get stock fundamentals using Polygon API"""
        if not self.polygon_api_key:
            return {'error': 'Polygon API key not configured'}
        
        try:
            # Get company financials
            url = f"{Config.POLYGON_BASE_URL}/v3/reference/tickers/{symbol}/financials"
            params = {
                'apiKey': self.polygon_api_key,
                'limit': 10
            }
            
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            if 'results' in data and data['results']:
                latest = data['results'][0]
                return {
                    'symbol': symbol,
                    'revenue': latest.get('revenue', 0),
                    'net_income': latest.get('net_income_loss', 0),
                    'total_assets': latest.get('total_assets', 0),
                    'total_liabilities': latest.get('total_liabilities', 0),
                    'cash_equivalents': latest.get('cash_and_cash_equivalents', 0),
                    'debt': latest.get('total_debt', 0),
                    'source': 'Polygon'
                }
            else:
                return {'symbol': symbol, 'error': 'No financial data found', 'source': 'Polygon'}
                
        except Exception as e:
            return {
                'symbol': symbol,
                'error': f"Failed to fetch data from Polygon: {str(e)}",
                'source': 'Polygon'
            }
    
    def get_stock_data(self, symbol: str) -> Dict[str, Any]:
        """Get comprehensive stock data from multiple sources"""
        yahoo_data = self.get_stock_info_yahoo(symbol)
        polygon_data = self.get_stock_fundamentals_polygon(symbol)
        
        # Merge data
        combined_data = {**yahoo_data}
        if 'error' not in polygon_data:
            combined_data['fundamentals'] = polygon_data
        
        return combined_data

class NewsAPIClient:
    """Client for fetching news data from multiple sources"""
    
    def __init__(self):
        self.news_api_key = Config.NEWS_API_KEY
        self.bing_api_key = Config.BING_SEARCH_API_KEY
        self.timeout = Config.REQUEST_TIMEOUT
    
    def get_news_newsapi(self, query: str, days: int = 7) -> List[Dict[str, Any]]:
        """Get news from NewsAPI"""
        if not self.news_api_key:
            return [{'error': 'NewsAPI key not configured'}]
        
        try:
            from_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            url = f"{Config.NEWS_API_BASE_URL}/everything"
            params = {
                'q': query,
                'from': from_date,
                'sortBy': 'relevancy',
                'apiKey': self.news_api_key,
                'language': 'en',
                'pageSize': 20
            }
            
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == 'ok' and 'articles' in data:
                articles = []
                for article in data['articles']:
                    articles.append({
                        'title': article.get('title', ''),
                        'description': article.get('description', ''),
                        'url': article.get('url', ''),
                        'published_at': article.get('publishedAt', ''),
                        'source': article.get('source', {}).get('name', ''),
                        'relevance_score': 0.8,  # Placeholder for relevance scoring
                        'source_api': 'NewsAPI'
                    })
                return articles
            else:
                return [{'error': f"NewsAPI error: {data.get('message', 'Unknown error')}"}]
                
        except Exception as e:
            return [{'error': f"Failed to fetch news from NewsAPI: {str(e)}"}]
    
    def get_news_bing(self, query: str) -> List[Dict[str, Any]]:
        """Get news from Bing Search API"""
        if not self.bing_api_key:
            return [{'error': 'Bing Search API key not configured'}]
        
        try:
            # Note: This is a simplified implementation
            # Bing Search API requires more complex setup
            return [{'error': 'Bing Search API implementation pending'}]
            
        except Exception as e:
            return [{'error': f"Failed to fetch news from Bing: {str(e)}"}]
    
    def get_news(self, query: str, days: int = 7) -> List[Dict[str, Any]]:
        """Get news from multiple sources"""
        newsapi_news = self.get_news_newsapi(query, days)
        bing_news = self.get_news_bing(query)
        
        # Combine and deduplicate news
        all_news = newsapi_news + bing_news
        return all_news
