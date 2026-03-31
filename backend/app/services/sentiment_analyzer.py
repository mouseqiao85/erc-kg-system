from typing import Dict, List, Any, Optional
import re
from openai import OpenAI
from app.core.config import settings


class SentimentAnalyzer:
    """情感分析器"""
    
    def __init__(self, client: OpenAI = None):
        if client is None:
            self.client = OpenAI(
                api_key=settings.llm_api_key,
                base_url=settings.llm_base_url
            )
        else:
            self.client = client
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """分析文本情感"""
        if not text:
            return self._default_result()
        
        try:
            prompt = f"""请分析以下文本的情感倾向和特征。

文本：{text[:1000]}

请以JSON格式返回分析结果：
{{
    "overall": 0.5,
    "dimensions": {{
        "emotion": {{"value": 0.5, "label": "neutral"}},
        "influence": {{"value": 0.5, "level": "medium", "metrics": {{"reach": 0, "shares": 0}}}},
        "timeliness": {{"value": 0.5, "label": "normal"}},
        "credibility": {{"value": 0.5, "label": "medium"}}
    }}
}}

只返回JSON，不要其他内容。"""

            response = self.client.chat.completions.create(
                model=settings.llm_model,
                messages=[
                    {"role": "system", "content": "你是一个专业的情感分析助手。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            result_text = response.choices[0].message.content
            
            import json
            try:
                result = json.loads(result_text)
                return result
            except:
                return self._parse_fallback(result_text)
                
        except Exception as e:
            print(f"Sentiment analysis error: {e}")
            return self._default_result()
    
    def _default_result(self) -> Dict[str, Any]:
        return {
            "overall": 0.5,
            "dimensions": {
                "emotion": {"value": 0.5, "label": "neutral"},
                "influence": {"value": 0.5, "level": "medium", "metrics": {"reach": 0, "shares": 0}},
                "timeliness": {"value": 0.5, "label": "normal"},
                "credibility": {"value": 0.5, "label": "medium"}
            }
        }
    
    def _parse_fallback(self, text: str) -> Dict[str, Any]:
        """备用解析方法"""
        text = text.lower()
        
        positive_words = ["好", "优秀", "棒", "赞", "满意", "positive", "good", "great", "excellent"]
        negative_words = ["差", "坏", "糟", "烂", "负面的", "negative", "bad", "poor", "terrible"]
        
        pos_count = sum(1 for w in positive_words if w in text)
        neg_count = sum(1 for w in negative_words if w in text)
        
        if pos_count > neg_count:
            overall = 0.7
        elif neg_count > pos_count:
            overall = 0.3
        else:
            overall = 0.5
        
        return {
            "overall": overall,
            "dimensions": {
                "emotion": {"value": overall, "label": "neutral"},
                "influence": {"value": 0.5, "level": "medium"},
                "timeliness": {"value": 0.5, "label": "normal"},
                "credibility": {"value": 0.5, "label": "medium"}
            }
        }
    
    def analyze_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """批量分析"""
        return [self.analyze_sentiment(text) for text in texts]


class KeywordExtractor:
    """关键词提取器"""
    
    def __init__(self, client: OpenAI = None):
        self.client = client or OpenAI(api_key=settings.openai_api_key)
    
    def extract_keywords(self, text: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """提取关键词"""
        if not text:
            return []
        
        try:
            prompt = f"""请从以下文本中提取关键词和热点词汇。

文本：{text[:1500]}

请列出最重要的{top_k}个关键词，格式：
关键词1,关键词2,关键词3,...

只返回关键词列表。"""

            response = self.client.chat.completions.create(
                model=settings.llm_model,
                messages=[
                    {"role": "system", "content": "你是一个专业的关键词提取助手。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            result_text = response.choices[0].message.content
            
            keywords = []
            for i, line in enumerate(result_text.split('\n')):
                line = line.strip().strip('-').strip('*').strip()
                if line and len(line) > 1:
                    keywords.append({
                        "word": line,
                        "rank": i + 1,
                        "frequency": max(10 - i, 1)
                    })
                    if len(keywords) >= top_k:
                        break
            
            return keywords
            
        except Exception as e:
            print(f"Keyword extraction error: {e}")
            return self._simple_extract(text, top_k)
    
    def _simple_extract(self, text: str, top_k: int) -> List[Dict[str, Any]]:
        """简单关键词提取"""
        import jieba
        from collections import Counter
        
        words = jieba.cut(text)
        word_counts = Counter(words)
        
        stopwords = set(['的', '了', '是', '在', '和', '有', '与', '为', '与', '及', '或', '等', 'the', 'a', 'an', 'is', 'are'])
        
        filtered = [(w, c) for w, c in word_counts.items() if len(w) > 1 and w not in stopwords]
        filtered.sort(key=lambda x: x[1], reverse=True)
        
        return [
            {"word": w, "rank": i + 1, "frequency": c}
            for i, (w, c) in enumerate(filtered[:top_k])
        ]


class EventDetector:
    """事件检测器"""
    
    def __init__(self, client: OpenAI = None):
        self.client = client or OpenAI(api_key=settings.openai_api_key)
    
    def detect_events(self, articles: List[Dict]) -> List[Dict[str, Any]]:
        """从文章中检测舆情事件"""
        if not articles:
            return []
        
        try:
            articles_text = "\n".join([
                f"- {a.get('title', '')}: {a.get('content', '')[:200]}"
                for a in articles[:10]
            ])
            
            prompt = f"""请从以下文章中识别出重要的舆情事件。

文章：
{articles_text}

请以JSON数组格式返回事件列表：
[
  {{"title": "事件标题", "type": "risk/opportunity/trend", "severity": "high/medium/low", "description": "事件描述"}}
]

只返回JSON数组。"""

            response = self.client.chat.completions.create(
                model=settings.llm_model,
                messages=[
                    {"role": "system", "content": "你是一个专业的舆情事件分析助手。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            result_text = response.choices[0].message.content
            
            import json
            try:
                events = json.loads(result_text)
                return events
            except:
                return []
                
        except Exception as e:
            print(f"Event detection error: {e}")
            return []
    
    def calculate_impact(self, event: Dict, related_articles: List[Dict]) -> Dict[str, Any]:
        """计算事件影响"""
        if not related_articles:
            return {"overall": 0.5, "reach": 0, "sentiment": "neutral"}
        
        sentiments = []
        for article in related_articles:
            sentiment = article.get("sentiment_score", {})
            if isinstance(sentiment, dict):
                sentiments.append(sentiment.get("overall", 0.5))
            else:
                sentiments.append(0.5)
        
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0.5
        
        severity_scores = {"high": 0.8, "medium": 0.5, "low": 0.2}
        severity = event.get("severity", "medium")
        
        impact = {
            "overall": (avg_sentiment + severity_scores.get(severity, 0.5)) / 2,
            "reach": len(related_articles),
            "sentiment": "positive" if avg_sentiment > 0.6 else "negative" if avg_sentiment < 0.4 else "neutral",
            "article_count": len(related_articles)
        }
        
        return impact


class AlertGenerator:
    """预警生成器"""
    
    def __init__(self):
        self.thresholds = {
            "sentiment_low": 0.3,
            "sentiment_high": 0.7,
            "influence_high": 0.8,
            "severity": "high"
        }
    
    def check_alerts(
        self,
        customers: List[Dict],
        events: List[Dict],
        articles: List[Dict]
    ) -> List[Dict[str, Any]]:
        """检查并生成预警"""
        alerts = []
        
        for event in events:
            if event.get("severity") == "high":
                alerts.append({
                    "type": "risk_event",
                    "title": f"高风险事件: {event.get('title', '')}",
                    "severity": "high",
                    "description": event.get("description", ""),
                    "related_count": event.get("related_count", 0)
                })
        
        negative_customers = [
            c for c in customers
            if c.get("sentiment_score", 0.5) < self.thresholds["sentiment_low"]
        ]
        
        if len(negative_customers) > 5:
            alerts.append({
                "type": "mass_negative",
                "title": f"大量客户情感负面 ({len(negative_customers)}家)",
                "severity": "high",
                "description": "多个客户出现负面情感",
                "related_count": len(negative_customers)
            })
        
        for customer in customers:
            sentiment = customer.get("sentiment_score", 0.5)
            if sentiment < 0.2:
                alerts.append({
                    "type": "customer_risk",
                    "title": f"客户风险: {customer.get('name', '')}",
                    "severity": "critical",
                    "description": f"客户情感严重负面 ({sentiment:.2f})",
                    "related_customer_id": customer.get("id")
                })
        
        return sorted(alerts, key=lambda x: {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(x["severity"], 4))
    
    def generate_report(self, alerts: List[Dict]) -> str:
        """生成预警报告"""
        if not alerts:
            return "暂无预警"
        
        report = "## 舆情预警报告\n\n"
        
        critical = [a for a in alerts if a.get("severity") == "critical"]
        high = [a for a in alerts if a.get("severity") == "high"]
        
        if critical:
            report += f"### 🔴 严重预警 ({len(critical)}项)\n"
            for a in critical:
                report += f"- {a.get('title', '')}\n"
        
        if high:
            report += f"\n### 🟠 高危预警 ({len(high)}项)\n"
            for a in high:
                report += f"- {a.get('title', '')}\n"
        
        return report


sentiment_analyzer = SentimentAnalyzer()
keyword_extractor = KeywordExtractor()
event_detector = EventDetector()
alert_generator = AlertGenerator()
