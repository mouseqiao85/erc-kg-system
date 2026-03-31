"""
互联网搜索服务 - 获取最新30天舆情数据
支持百度搜索、新闻API等多种数据源
"""
import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import feedparser
from app.core.config import settings


class WebSearcher:
    """互联网搜索器"""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    
    async def get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(headers=self.headers)
        return self.session
    
    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def search_baidu(self, keyword: str, days: int = 30) -> List[Dict[str, Any]]:
        """百度搜索"""
        results = []
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        search_url = f"https://www.baidu.com/s?wd={keyword}&tn=json"
        
        try:
            session = await self.get_session()
            async with session.get(search_url, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    for item in data.get("feed", {}).get("entry", []):
                        results.append({
                            "title": item.get("title", ""),
                            "url": item.get("url", ""),
                            "snippet": item.get("abs", ""),
                            "source": "baidu",
                            "search_keyword": keyword
                        })
        except Exception as e:
            print(f"Baidu search error: {e}")
        
        return results
    
    async def search_news_rss(self, keyword: str) -> List[Dict[str, Any]]:
        """RSS新闻源搜索"""
        results = []
        
        rss_feeds = [
            f"https://news.google.com/rss/search?q={keyword}&hl=zh-CN",
            f"https://www.baidu.com/s?wd={keyword}&rn=20&tn=rss",
        ]
        
        session = await self.get_session()
        
        for feed_url in rss_feeds:
            try:
                async with session.get(feed_url, timeout=30) as response:
                    if response.status == 200:
                        text = await response.text()
                        feed = feedparser.parse(text)
                        
                        for entry in feed.entries[:10]:
                            results.append({
                                "title": entry.get("title", ""),
                                "url": entry.get("link", ""),
                                "snippet": entry.get("summary", ""),
                                "published": entry.get("published", ""),
                                "source": "rss"
                            })
            except Exception as e:
                print(f"RSS feed error {feed_url}: {e}")
        
        return results
    
    async def search_all(self, keyword: str, days: int = 30) -> List[Dict[str, Any]]:
        """综合搜索所有来源"""
        tasks = [
            self.search_baidu(keyword, days),
            self.search_news_rss(keyword)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_results = []
        for r in results:
            if isinstance(r, list):
                all_results.extend(r)
        
        seen = set()
        unique_results = []
        for item in all_results:
            key = item.get("title", "") + item.get("url", "")
            if key not in seen:
                seen.add(key)
                unique_results.append(item)
        
        return unique_results[:50]


class SentimentDataCollector:
    """舆情数据采集器"""
    
    def __init__(self):
        self.searcher = WebSearcher()
    
    async def collect_entity_sentiment(
        self, 
        entity_name: str,
        keywords: List[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        采集指定实体的舆情数据
        
        Args:
            entity_name: 实体名称
            keywords: 额外关键词
            days: 采集天数
        
        Returns:
            采集结果
        """
        search_keywords = [entity_name]
        if keywords:
            search_keywords.extend(keywords)
        
        all_articles = []
        
        for keyword in search_keywords[:5]:
            articles = await self.searcher.search_all(keyword, days)
            all_articles.extend(articles)
        
        seen = set()
        unique_articles = []
        for article in all_articles:
            key = article.get("title", "")
            if key not in seen:
                seen.add(key)
                unique_articles.append(article)
        
        return {
            "entity": entity_name,
            "articles": unique_articles[:30],
            "count": len(unique_articles[:30]),
            "collected_at": datetime.now().isoformat()
        }
    
    async def collect_industry_sentiment(
        self,
        industry: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """采集行业舆情数据"""
        keywords = [
            f"{industry} 新闻",
            f"{industry} 舆情",
            f"{industry} 动态"
        ]
        
        all_articles = []
        
        for kw in keywords:
            articles = await self.searcher.search_all(kw, days)
            all_articles.extend(articles)
        
        return {
            "industry": industry,
            "articles": all_articles[:50],
            "count": len(all_articles[:50])
        }
    
    async def close(self):
        await self.searcher.close()


searcher = WebSearcher()
collector = SentimentDataCollector()
