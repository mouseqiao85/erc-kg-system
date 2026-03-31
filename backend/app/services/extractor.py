from typing import List, Dict, Any, Optional
import json
import re
from openai import OpenAI
from app.core.config import settings


class LLMTripleExtractor:
    """
    LLM三元组抽取引擎
    
    职责：使用LLM从语料中抽取结构化三元组
    """
    
    DEFAULT_PROMPT_TEMPLATE = """## 任务描述
你是一个知识图谱构建专家，请从以下文本中提取领域相关三元组。

## 输出格式
请以 JSON 格式输出三元组列表：
[
  {{"head": "头实体", "relation": "关系", "tail": "尾实体"}},
  ...
]

## 示例（Few-shot）
文本：RSA是一种非对称加密算法，由Ron Rivest等人于1977年提出。
输出：
[
  {{"head": "RSA", "relation": "是一种", "tail": "非对称加密算法"}},
  {{"head": "RSA", "relation": "发明者", "tail": "Ron Rivest"}},
  {{"head": "RSA", "relation": "发明时间", "tail": "1977年"}}
]

## 待处理文本
{context}

## 注意事项
1. 仅输出文本中明确陈述的事实
2. 不要添加文本中未提及的信息
3. 保持关系的简洁和规范
4. 返回有效的JSON数组格式
"""
    
    def __init__(
        self,
        client: Optional[OpenAI] = None,
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        prompt_template: str = None
    ):
        if client is None:
            self.client = OpenAI(
                api_key=settings.llm_api_key,
                base_url=settings.llm_base_url
            )
        else:
            self.client = client
        self.model = model or settings.llm_model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.prompt_template = prompt_template or self.DEFAULT_PROMPT_TEMPLATE
    
    def build_prompt(self, context: str) -> str:
        """构建提示词"""
        return self.prompt_template.format(context=context)
    
    def parse_response(self, response_text: str) -> List[Dict[str, Any]]:
        """解析LLM响应，提取三元组"""
        try:
            text = response_text.strip()
            
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            
            text = text.strip()
            
            if not text.startswith("["):
                json_match = re.search(r'\[.*\]', text, re.DOTALL)
                if json_match:
                    text = json_match.group(0)
            
            triples = json.loads(text)
            
            valid_triples = []
            for t in triples:
                if isinstance(t, dict) and all(k in t for k in ["head", "relation", "tail"]):
                    valid_triples.append({
                        "head": str(t["head"]).strip(),
                        "relation": str(t["relation"]).strip(),
                        "tail": str(t["tail"]).strip()
                    })
            
            return valid_triples
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}")
            return self._fallback_parse(response_text)
        except Exception as e:
            print(f"Parse error: {e}")
            return []
    
    def _fallback_parse(self, text: str) -> List[Dict[str, Any]]:
        """备用解析方法"""
        triples = []
        patterns = [
            r'[""]?(\w+)[""]?\s*[,，]\s*[""]?(\w+)[""]?\s*[,，]\s*[""]?(\w+)[""]?',
            r'head[:：]\s*[""]?(\w+)[""]?.*?relation[:：]\s*[""]?(\w+)[""]?.*?tail[:：]\s*[""]?(\w+)[""]?',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if len(match) == 3:
                    triples.append({
                        "head": match[0].strip(),
                        "relation": match[1].strip(),
                        "tail": match[2].strip()
                    })
        
        return triples
    
    def extract(
        self,
        entity: str,
        corpus: List[str],
        context: str = ""
    ) -> Dict[str, Any]:
        """
        抽取三元组
        
        Args:
            entity: 目标实体
            corpus: 相关语料列表
            context: 额外上下文信息
        
        Returns:
            包含三元组和置信度的字典
        """
        combined_context = "\n".join(corpus)
        if context:
            combined_context = f"{context}\n{combined_context}"
        
        prompt = self.build_prompt(combined_context)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的知识图谱构建助手，擅长从文本中提取结构化的实体关系三元组。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            response_text = response.choices[0].message.content
            triples = self.parse_response(response_text)
            
            confidence = self._calculate_confidence(triples, combined_context)
            
            return {
                "triples": triples,
                "confidence": confidence,
                "raw_response": response_text
            }
        except Exception as e:
            print(f"Extraction error: {e}")
            return {
                "triples": [],
                "confidence": 0.0,
                "error": str(e)
            }
    
    def _calculate_confidence(self, triples: List[Dict], source_text: str) -> float:
        """计算三元组的置信度"""
        if not triples:
            return 0.0
        
        confidence_scores = []
        
        for triple in triples:
            head = triple.get("head", "")
            relation = triple.get("relation", "")
            tail = triple.get("tail", "")
            
            all_in_text = all(
                word in source_text 
                for word in [head, tail] 
                if len(word) > 1
            )
            
            score = 0.8 if all_in_text else 0.5
            confidence_scores.append(score)
        
        return sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
    
    def extract_batch(
        self,
        entity_corpus_map: Dict[str, List[str]]
    ) -> Dict[str, Dict[str, Any]]:
        """
        批量抽取三元组
        
        Args:
            entity_corpus_map: 实体到语料的映射
        
        Returns:
            每个实体的抽取结果
        """
        results = {}
        
        for entity, corpus in entity_corpus_map.items():
            if corpus:
                results[entity] = self.extract(entity, corpus)
        
        return results
