"""
百度搜索服务 - 用于舆情信息获取

使用百度搜索API获取舆情相关信息
API文档: https://cloud.baidu.com/doc/SEARCH/index.html
"""

import requests
import json
from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BaiduSearchConfig:
    """百度搜索API配置"""
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.baidu.com/smartsearch/v1"
    ):
        self.api_key = api_key
        self.base_url = base_url


class BaiduSearchResult:
    """百度搜索结果"""
    def __init__(
        self,
        title: str,
        url: str,
        snippet: str,
        source: str,
        published_time: Optional[datetime] = None,
        **kwargs
    ):
        self.title = title
        self.url = url
        self.snippet = snippet
        self.source = source
        self.published_time = published_time
        self.extra = kwargs

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "title": self.title,
            "url": self.url,
            "snippet": self.snippet,
            "source": self.source,
            "published_time": self.published_time.isoformat() if self.published_time else None,
            **self.extra
        }


class BaiduSearchClient:
    """百度搜索客户端"""
    
    def __init__(self, config: BaiduSearchConfig):
        self.config = config
        self.headers = {
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json"
        }
    
    def search(
        self,
        query: str,
        num_results: int = 10,
        date_range: Optional[str] = None,
        site: Optional[str] = None,
        **filters
    ) -> List[BaiduSearchResult]:
        """
        执行搜索
        
        Args:
            query: 搜索关键词
            num_results: 返回结果数量
            date_range: 时间范围 (e.g., "1d", "1w", "1m")
            site: 指定站点 (e.g., "news.baidu.com")
            **filters: 其他过滤条件
        
        Returns:
            搜索结果列表
        """
        try:
            # 构建请求参数
            params = {
                "query": query,
                "num": num_results,
            }
            
            if date_range:
                params["date_range"] = date_range
            
            if site:
                params["site"] = site
            
            if filters:
                params.update(filters)
            
            # 调用百度搜索API
            response = requests.post(
                f"{self.config.base_url}/search",
                headers=self.headers,
                json=params,
                timeout=30
            )
            
            response.raise_for_status()
            
            # 解析响应
            data = response.json()
            results = []
            
            if "results" in data:
                for item in data["results"]:
                    result = BaiduSearchResult(
                        title=item.get("title", ""),
                        url=item.get("url", ""),
                        snippet=item.get("snippet", ""),
                        source=item.get("source", ""),
                        published_time=self._parse_time(item.get("published_time")),
                        **item.get("extra", {})
                    )
                    results.append(result)
            
            logger.info(f"搜索完成: 查询='{query}', 结果数={len(results)}")
            return results
            
        except requests.exceptions.RequestException as e:
            logger.error(f"搜索请求失败: {e}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"解析搜索结果失败: {e}")
            return []
    
    def search_news(
        self,
        query: str,
        num_results: int = 10,
        date_range: Optional[str] = None
    ) -> List[BaiduSearchResult]:
        """
        搜索新闻
        
        Args:
            query: 搜索关键词
            num_results: 返回结果数量
            date_range: 时间范围
        
        Returns:
            新闻搜索结果列表
        """
        return self.search(
            query=query,
            num_results=num_results,
            date_range=date_range,
            type="news"
        )
    
    def search_by_entity(
        self,
        entity_name: str,
        entity_type: Optional[str] = None,
        num_results: int = 20
    ) -> List[BaiduSearchResult]:
        """
        根据实体搜索舆情信息
        
        Args:
            entity_name: 实体名称
            entity_type: 实体类型 (e.g., "company", "person", "product")
            num_results: 返回结果数量
        
        Returns:
            舆情搜索结果列表
        """
        query = entity_name
        if entity_type:
            query = f"{entity_name} {entity_type}"
        
        return self.search_news(query=query, num_results=num_results, date_range="1m")
    
    def search_sentiment_events(
        self,
        keywords: List[str],
        date_range: str = "1w",
        num_results: int = 50
    ) -> List[BaiduSearchResult]:
        """
        搜索舆情事件
        
        Args:
            keywords: 关键词列表
            date_range: 时间范围
            num_results: 返回结果数量
        
        Returns:
            舆情事件搜索结果列表
        """
        query = " ".join(keywords)
        return self.search_news(
            query=query,
            num_results=num_results,
            date_range=date_range
        )
    
    def _parse_time(self, time_str: Optional[str]) -> Optional[datetime]:
        """解析时间字符串"""
        if not time_str:
            return None
        
        try:
            # 尝试解析ISO格式
            return datetime.fromisoformat(time_str)
        except ValueError:
            try:
                # 尝试解析其他格式
                return datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                logger.warning(f"无法解析时间: {time_str}")
                return None


# 便捷函数
def create_baidu_search_client(api_key: str) -> BaiduSearchClient:
    """创建百度搜索客户端"""
    config = BaiduSearchConfig(api_key=api_key)
    return BaiduSearchClient(config)


def search_sentiment_info(
    query: str,
    api_key: str,
    num_results: int = 10
) -> List[Dict]:
    """
    搜索舆情信息（便捷函数）
    
    Args:
        query: 搜索关键词
        api_key: 百度API密钥
        num_results: 返回结果数量
    
    Returns:
        搜索结果字典列表
    """
    client = create_baidu_search_client(api_key)
    results = client.search_news(query=query, num_results=num_results)
    return [r.to_dict() for r in results]
