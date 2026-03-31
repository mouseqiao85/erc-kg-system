"""
舆情评分系统 - 四维评分模型
维度：情感维度、影响力维度、时效性维度、可信度维度
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import re
from openai import OpenAI
from app.core.config import settings


class SentimentScorer:
    """舆情评分器"""
    
    POSITIVE_WORDS = [
        "好", "优秀", "成功", "增长", "创新", "突破", "领先", "优质", "积极", "利好",
        "上涨", "盈利", "获", "赞", "认可", "合作", "发展", "进步", "提升", "增强"
    ]
    
    NEGATIVE_WORDS = [
        "差", "失败", "下降", "亏损", "风险", "问题", "危机", "负面", "利空", "下跌",
        "损失", "违规", "处罚", "投诉", "纠纷", "诉讼", "裁员", "关闭", "破产", "违约"
    ]
    
    def __init__(self, client: OpenAI = None):
        if client is None:
            self.client = OpenAI(
                api_key=settings.llm_api_key,
                base_url=settings.llm_base_url
            )
        else:
            self.client = client
    
    def score_emotion(self, text: str) -> Dict[str, Any]:
        """
        情感维度评分
        
        返回: {"value": 0-1, "label": "positive/neutral/negative"}
        """
        positive_count = sum(1 for w in self.POSITIVE_WORDS if w in text)
        negative_count = sum(1 for w in self.NEGATIVE_WORDS if w in text)
        
        total = positive_count + negative_count
        if total == 0:
            return {"value": 0.5, "label": "neutral"}
        
        score = 0.5 + (positive_count - negative_count) / (total * 2)
        score = max(0, min(1, score))
        
        if score > 0.6:
            label = "positive"
        elif score < 0.4:
            label = "negative"
        else:
            label = "neutral"
        
        return {"value": round(score, 2), "label": label}
    
    def score_influence(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        影响力维度评分
        
        基于: 来源权威性、传播范围、互动量
        """
        source = article.get("source", "")
        url = article.get("url", "")
        
        high_authority = ["gov.cn", "people.com", "xinhua", "cctv", "cnstock"]
        medium_authority = ["sina", "sohu", "163", "qq", "ifeng"]
        
        level = "low"
        base_score = 0.3
        
        for h in high_authority:
            if h in url or h in source:
                level = "high"
                base_score = 0.8
                break
        
        if level == "low":
            for m in medium_authority:
                if m in url or m in source:
                    level = "medium"
                    base_score = 0.6
                    break
        
        return {
            "value": base_score,
            "level": level,
            "metrics": {
                "source_authority": level
            }
        }
    
    def score_timeliness(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        时效性维度评分
        
        基于: 发布时间距离当前的时间差
        """
        published = article.get("published") or article.get("publish_time")
        
        if not published:
            return {"value": 0.5, "label": "unknown"}
        
        try:
            if isinstance(published, str):
                pub_date = datetime.fromisoformat(published.replace("Z", "+00:00"))
            else:
                pub_date = published
            
            now = datetime.now(pub_date.tzinfo) if pub_date.tzinfo else datetime.now()
            hours_diff = (now - pub_date).total_seconds() / 3600
            
            if hours_diff < 24:
                value = 1.0
                label = "fresh"
            elif hours_diff < 72:
                value = 0.8
                label = "recent"
            elif hours_diff < 168:
                value = 0.6
                label = "week"
            elif hours_diff < 720:
                value = 0.4
                label = "month"
            else:
                value = 0.2
                label = "old"
            
            return {"value": value, "label": label, "hours_ago": int(hours_diff)}
        except:
            return {"value": 0.5, "label": "unknown"}
    
    def score_credibility(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        可信度维度评分
        
        基于: 来源可信度、内容完整性
        """
        source = article.get("source", "")
        title = article.get("title", "")
        snippet = article.get("snippet", "")
        url = article.get("url", "")
        
        score = 0.5
        label = "medium"
        
        credible_sources = ["gov.cn", "edu.cn", "org.cn", "people.com", "xinhuanet"]
        for cs in credible_sources:
            if cs in url:
                score = 0.9
                label = "high"
                break
        
        if label != "high":
            if len(title) > 10 and len(snippet) > 50:
                score = 0.7
                label = "medium"
            elif len(title) < 5 or "点击查看" in title:
                score = 0.3
                label = "low"
        
        return {"value": score, "label": label}
    
    def calculate_overall_score(self, dimensions: Dict[str, Dict]) -> float:
        """
        计算综合评分
        
        权重: emotion=0.3, influence=0.25, timeliness=0.2, credibility=0.25
        """
        weights = {
            "emotion": 0.3,
            "influence": 0.25,
            "timeliness": 0.2,
            "credibility": 0.25
        }
        
        total = 0
        for dim, weight in weights.items():
            if dim in dimensions:
                total += dimensions[dim].get("value", 0.5) * weight
        
        return round(total, 2)
    
    def score_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """对单篇文章进行四维评分"""
        text = f"{article.get('title', '')} {article.get('snippet', '')}"
        
        dimensions = {
            "emotion": self.score_emotion(text),
            "influence": self.score_influence(article),
            "timeliness": self.score_timeliness(article),
            "credibility": self.score_credibility(article)
        }
        
        overall = self.calculate_overall_score(dimensions)
        
        return {
            "article": article,
            "overall_score": overall,
            "dimensions": dimensions
        }
    
    def score_articles(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """批量评分"""
        scored = [self.score_article(a) for a in articles]
        
        if not scored:
            return {
                "articles": [],
                "summary": {
                    "average_score": 0,
                    "positive_count": 0,
                    "negative_count": 0,
                    "neutral_count": 0
                }
            }
        
        scores = [s["overall_score"] for s in scored]
        emotions = [s["dimensions"]["emotion"]["label"] for s in scored]
        
        return {
            "articles": scored,
            "summary": {
                "average_score": round(sum(scores) / len(scores), 2),
                "positive_count": emotions.count("positive"),
                "negative_count": emotions.count("negative"),
                "neutral_count": emotions.count("neutral"),
                "total_count": len(scored)
            }
        }


class EntitySentimentAnalyzer:
    """实体舆情分析器"""
    
    def __init__(self):
        self.scorer = SentimentScorer()
    
    def analyze_entity(
        self,
        entity_name: str,
        articles: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        分析实体舆情
        
        Args:
            entity_name: 实体名称
            articles: 相关文章列表
        
        Returns:
            实体舆情分析结果
        """
        scored_result = self.scorer.score_articles(articles)
        
        summary = scored_result["summary"]
        
        trend = "stable"
        if summary["positive_count"] > summary["negative_count"] * 2:
            trend = "rising"
        elif summary["negative_count"] > summary["positive_count"] * 2:
            trend = "declining"
        
        risk_level = "low"
        if summary["negative_count"] > summary["positive_count"]:
            risk_level = "medium"
        if summary["negative_count"] > summary["positive_count"] * 2:
            risk_level = "high"
        
        return {
            "entity": entity_name,
            "sentiment_score": summary["average_score"],
            "trend": trend,
            "risk_level": risk_level,
            "summary": summary,
            "articles": scored_result["articles"][:10]
        }


scorer = SentimentScorer()
analyzer = EntitySentimentAnalyzer()
