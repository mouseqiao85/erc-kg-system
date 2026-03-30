import asyncio
import aiohttp
import feedparser
from typing import List, Dict, Any, Optional
from datetime import datetime
import re


class DataCollector:
    """数据采集器 - 通用网页爬虫"""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def fetch_url(self, url: str) -> Optional[str]:
        """获取URL内容"""
        try:
            session = await self.get_session()
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    return await response.text()
        except Exception as e:
            print(f"Fetch error: {url} - {e}")
        return None
    
    async def fetch_rss(self, url: str) -> List[Dict[str, Any]]:
        """获取RSS订阅源"""
        try:
            text = await self.fetch_url(url)
            if not text:
                return []
            
            feed = feedparser.parse(text)
            articles = []
            
            for entry in feed.entries[:20]:
                articles.append({
                    "title": entry.get("title", ""),
                    "content": entry.get("summary", "") or entry.get("description", ""),
                    "url": entry.get("link", ""),
                    "publish_time": entry.get("published", ""),
                    "source": url
                })
            
            return articles
        except Exception as e:
            print(f"RSS parse error: {e}")
            return []
    
    async def fetch_news_api(self, api_url: str, api_key: str = None) -> List[Dict[str, Any]]:
        """调用新闻API"""
        try:
            headers = {}
            if api_key:
                headers["X-Api-Key"] = api_key
            
            session = await self.get_session()
            async with session.get(api_url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("articles", []) if isinstance(data, dict) else data
        except Exception as e:
            print(f"News API error: {e}")
        return []


class NewsCollector(DataCollector):
    """新闻采集器"""
    
    RSS_SOURCES = {
        "sina_tech": "https://tech.sina.com.cn/rss/",
        "sina_finance": "https://finance.sina.com.cn/rss/",
        "36kr": "https://www.36kr.com/feed/",
        "techcrunch": "https://techcrunch.com/feed/",
    }
    
    def __init__(self):
        super().__init__()
        self.sources = self.RSS_SOURCES
    
    async def collect_from_rss(self, source_name: str) -> List[Dict[str, Any]]:
        """从RSS源采集"""
        url = self.sources.get(source_name)
        if not url:
            return []
        
        return await self.fetch_rss(url)
    
    async def collect_all_sources(self) -> List[Dict[str, Any]]:
        """采集所有RSS源"""
        all_articles = []
        
        for source_name in self.sources:
            articles = await self.collect_from_rss(source_name)
            for article in articles:
                article["source_type"] = "news"
                article["source_name"] = source_name
            all_articles.extend(articles)
        
        return all_articles
    
    def clean_text(self, text: str) -> str:
        """清理文本"""
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        return text


class WebCollector(DataCollector):
    """网页采集器 - 针对特定网站"""
    
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    async def fetch_html(self, url: str) -> Optional[str]:
        """获取HTML内容"""
        try:
            session = await self.get_session()
            headers = {"User-Agent": self.USER_AGENT}
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    return await response.text()
        except Exception as e:
            print(f"HTML fetch error: {e}")
        return None
    
    def extract_article_from_html(self, html: str, url: str) -> Dict[str, Any]:
        """从HTML中提取文章信息"""
        import re
        
        title_match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.I)
        title = title_match.group(1).strip() if title_match else ""
        
        meta_desc = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']+)["\']', html, re.I)
        description = meta_desc.group(1) if meta_desc else ""
        
        og_title = re.search(r'<meta[^>]*property=["\']og:title["\'][^>]*content=["\']([^"\']+)["\']', html, re.I)
        if og_title:
            title = og_title.group(1)
        
        return {
            "title": title,
            "content": description,
            "url": url,
            "source_type": "web"
        }


class AnnouncementCollector(DataCollector):
    """公告采集器 - 采集上市公司公告"""
    
    ANNOUNCEMENT_URLS = {
        "sse": "http://www.sse.com.cn/disclosure/listedinfo/announcement/",
        "szse": "http://www.szse.cn/disclosure/company/announcement.html",
    }
    
    async def fetch_announcements(self, exchange: str = "sse") -> List[Dict[str, Any]]:
        """采集公告"""
        url = self.ANNOUNCEMENT_URLS.get(exchange)
        if not url:
            return []
        
        html = await self.fetch_html(url)
        if not html:
            return []
        
        announcements = []
        
        import re
        pattern = r'<a[^>]*href=["\']([^"\']+)["\'][^>]*>([^<]+)</a>'
        matches = re.findall(pattern, html)
        
        for href, title in matches[:20]:
            if "公告" in title or " announcement" in title.lower():
                announcements.append({
                    "title": title.strip(),
                    "url": href if href.startswith("http") else f"{url}{href}",
                    "source": exchange.upper(),
                    "source_type": "announcement"
                })
        
        return announcements


class SocialMediaCollector(DataCollector):
    """社交媒体采集器"""
    
    async def fetch_keyword_search(self, keyword: str, platform: str = "twitter") -> List[Dict[str, Any]]:
        """关键词搜索（需要API）"""
        return []


collector = NewsCollector()
web_collector = WebCollector()
announcement_collector = AnnouncementCollector()
