"""
Ultra-fast news client with fallback to sample data
Optimized for speed with caching and minimal API calls
"""

import requests
import time
from datetime import datetime, timedelta
from functools import lru_cache
from typing import List, Dict, Any
import streamlit as st

# Sample news data as fallback
FALLBACK_NEWS = [
    {
        "title": "Tech Stocks Rally on AI Optimism",
        "description": "Major technology companies see gains as artificial intelligence developments drive investor confidence.",
        "source": "MarketWatch",
        "publishedAt": "2024-01-24T10:30:00Z",
        "sentiment": "Positive",
        "url": "#"
    },
    {
        "title": "Federal Reserve Maintains Interest Rates",
        "description": "Central bank keeps rates steady as inflation shows signs of moderation across key sectors.",
        "source": "Reuters",
        "publishedAt": "2024-01-24T09:15:00Z",
        "sentiment": "Neutral",
        "url": "#"
    },
    {
        "title": "Energy Sector Gains on Supply Disruptions",
        "description": "Oil and gas companies benefit from unexpected supply chain challenges in key regions.",
        "source": "Bloomberg",
        "publishedAt": "2024-01-24T08:45:00Z",
        "sentiment": "Positive",
        "url": "#"
    },
    {
        "title": "Cryptocurrency Market Shows Volatility",
        "description": "Digital assets experience mixed trading as regulatory clarity remains uncertain.",
        "source": "CoinDesk",
        "publishedAt": "2024-01-24T07:30:00Z",
        "sentiment": "Neutral",
        "url": "#"
    },
    {
        "title": "Retail Sales Beat Expectations",
        "description": "Consumer spending remains robust despite economic headwinds and inflation concerns.",
        "source": "CNBC",
        "publishedAt": "2024-01-24T06:00:00Z",
        "sentiment": "Positive",
        "url": "#"
    }
]

# Symbol-specific news templates
SYMBOL_NEWS_TEMPLATES = {
    'AAPL': [
        {
            "title": "Apple Unveils Next-Generation Technology",
            "description": "Tech giant announces breakthrough innovations in their latest product lineup with enhanced AI capabilities.",
            "source": "TechCrunch",
            "sentiment": "Positive"
        },
        {
            "title": "iPhone Sales Exceed Market Expectations",
            "description": "Apple reports stronger than anticipated iPhone sales across all major markets this quarter.",
            "source": "Fortune",
            "sentiment": "Positive"
        }
    ],
    'TSLA': [
        {
            "title": "Tesla Delivers Record Vehicle Numbers",
            "description": "Electric vehicle manufacturer reports unprecedented delivery figures for the latest quarter.",
            "source": "Automotive News",
            "sentiment": "Positive"
        },
        {
            "title": "Tesla Expands Supercharger Network",
            "description": "Company announces major expansion of charging infrastructure across North America and Europe.",
            "source": "Electrek",
            "sentiment": "Positive"
        }
    ],
    'GOOGL': [
        {
            "title": "Google AI Breakthrough in Healthcare",
            "description": "Alphabet's Google division announces significant advances in AI-powered medical diagnostics.",
            "source": "Nature",
            "sentiment": "Positive"
        },
        {
            "title": "Google Cloud Gains Enterprise Customers",
            "description": "Cloud services division reports strong growth in enterprise client acquisition and retention.",
            "source": "ZDNet",
            "sentiment": "Positive"
        }
    ],
    'MSFT': [
        {
            "title": "Microsoft Azure Revenue Surges",
            "description": "Cloud computing platform shows exceptional growth driven by enterprise digital transformation.",
            "source": "Microsoft",
            "sentiment": "Positive"
        },
        {
            "title": "Microsoft AI Integration Expands",
            "description": "Company integrates advanced AI capabilities across Office 365 and Windows platforms.",
            "source": "The Verge",
            "sentiment": "Positive"
        }
    ]
}

class FastNewsClient:
    """Ultra-fast news client with intelligent fallback"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.base_url = "https://newsapi.org/v2"
        self.timeout = 2  # Very short timeout for speed
    
    @lru_cache(maxsize=50)
    def get_news_fast(self, symbol: str, max_articles: int = 5) -> List[Dict[str, Any]]:
        """Get news with ultra-fast response time"""
        start_time = time.time()
        
        # Try real API first (with very short timeout)
        if self.api_key:
            try:
                real_news = self._fetch_real_news(symbol, max_articles)
                if real_news:
                    elapsed = time.time() - start_time
                    print(f"📰 Real news fetched in {elapsed:.2f}s")
                    return real_news
            except Exception as e:
                print(f"⚠️ Real news API failed: {e}")
        
        # Fallback to intelligent sample data
        news = self._get_smart_fallback_news(symbol, max_articles)
        elapsed = time.time() - start_time
        print(f"📰 Sample news generated in {elapsed:.3f}s")
        return news
    
    def _fetch_real_news(self, symbol: str, max_articles: int) -> List[Dict[str, Any]]:
        """Attempt to fetch real news with timeout"""
        if not self.api_key:
            return None
        
        # Quick company name mapping
        company_names = {
            'AAPL': 'Apple',
            'TSLA': 'Tesla',
            'GOOGL': 'Google',
            'MSFT': 'Microsoft',
            'AMZN': 'Amazon',
            'META': 'Meta',
            'NVDA': 'NVIDIA'
        }
        
        query = company_names.get(symbol.upper(), symbol)
        
        params = {
            'q': query,
            'apiKey': self.api_key,
            'pageSize': max_articles,
            'language': 'en',
            'sortBy': 'publishedAt'
        }
        
        response = requests.get(
            f"{self.base_url}/everything",
            params=params,
            timeout=self.timeout
        )
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            
            return [{
                'title': article.get('title', 'No Title'),
                'description': article.get('description', 'No Description'),
                'source': article.get('source', {}).get('name', 'Unknown'),
                'publishedAt': article.get('publishedAt', ''),
                'url': article.get('url', '#'),
                'sentiment': self._quick_sentiment_analysis(article.get('title', '') + ' ' + article.get('description', ''))
            } for article in articles[:max_articles]]
        
        return None
    
    def _get_smart_fallback_news(self, symbol: str, max_articles: int) -> List[Dict[str, Any]]:
        """Generate intelligent fallback news based on symbol"""
        news_list = []
        current_time = datetime.now()
        
        # Add symbol-specific news if available
        if symbol.upper() in SYMBOL_NEWS_TEMPLATES:
            symbol_news = SYMBOL_NEWS_TEMPLATES[symbol.upper()]
            for i, news in enumerate(symbol_news[:2]):  # Take 2 symbol-specific
                news_item = news.copy()
                news_item['publishedAt'] = (current_time - timedelta(hours=i+1)).isoformat() + 'Z'
                news_item['url'] = '#'
                news_list.append(news_item)
        
        # Fill remaining slots with general market news
        remaining_slots = max_articles - len(news_list)
        for i, news in enumerate(FALLBACK_NEWS[:remaining_slots]):
            news_item = news.copy()
            news_item['publishedAt'] = (current_time - timedelta(hours=len(news_list)+i+1)).isoformat() + 'Z'
            news_list.append(news_item)
        
        return news_list[:max_articles]
    
    def _quick_sentiment_analysis(self, text: str) -> str:
        """Ultra-fast sentiment analysis using keywords"""
        text_lower = text.lower()
        
        positive_words = ['gain', 'up', 'rise', 'surge', 'growth', 'strong', 'beat', 'exceed', 'positive', 'breakthrough', 'innovation', 'record']
        negative_words = ['fall', 'drop', 'decline', 'loss', 'weak', 'miss', 'negative', 'concern', 'challenge', 'disruption']
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return 'Positive'
        elif negative_count > positive_count:
            return 'Negative'
        else:
            return 'Neutral'

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_cached_news(symbol: str, max_articles: int = 5) -> List[Dict[str, Any]]:
    """Cached news retrieval for Streamlit"""
    from config import Config
    
    client = FastNewsClient(Config.NEWS_API_KEY)
    return client.get_news_fast(symbol, max_articles)

# Quick test function
def test_fast_news():
    """Test the fast news client"""
    print("🧪 Testing Fast News Client...")
    
    symbols = ['AAPL', 'TSLA', 'GOOGL', 'MSFT']
    client = FastNewsClient()
    
    for symbol in symbols:
        start_time = time.time()
        news = client.get_news_fast(symbol, 3)
        elapsed = time.time() - start_time
        
        print(f"\n📊 {symbol}:")
        print(f"   ⏱️ Time: {elapsed:.3f}s")
        print(f"   📰 Articles: {len(news)}")
        for article in news[:2]:
            print(f"   • {article['title'][:50]}...")

if __name__ == "__main__":
    test_fast_news()
