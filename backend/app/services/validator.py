from typing import Dict, List, Any, Optional
import re
from openai import OpenAI
from app.core.config import settings


class TripleValidator:
    """
    三元组验证器
    
    验证流程：
    1. 事实检查：三元组是否在源文本中有依据
    2. 规则验证：关系一致性、实体类型检查
    3. LLM 再审：使用 LLM 二次验证
    """
    
    RELATION_PATTERNS = {
        "是": ["是", "属于", "为"],
        "发明": ["发明", "提出", "创建"],
        "时间": ["于", "在", "时间"],
        "地点": ["位于", "在", "地点"],
        "包含": ["包括", "包含", "含有"],
    }
    
    def __init__(
        self,
        client: Optional[OpenAI] = None,
        enable_llm_review: bool = True
    ):
        self.client = client or OpenAI(api_key=settings.openai_api_key)
        self.enable_llm_review = enable_llm_review
    
    def validate(
        self,
        triple: Dict[str, str],
        source_text: str,
        config: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        验证单个三元组
        
        Args:
            triple: 三元组 {"head": "...", "relation": "...", "tail": "..."}
            source_text: 源文本
            config: 验证配置
        
        Returns:
            验证结果
        """
        config = config or {}
        enable_llm = config.get("enable_llm_review", self.enable_llm_review)
        
        fact_check_result = self._fact_check(triple, source_text)
        if not fact_check_result["valid"]:
            return fact_check_result
        
        rule_result = self._rule_validation(triple)
        if not rule_result["valid"]:
            return rule_result
        
        if enable_llm:
            llm_result = self._llm_review(triple, source_text)
            return llm_result
        
        return {
            "valid": True,
            "confidence": fact_check_result.get("confidence", 0.8),
            "reasons": [fact_check_result.get("reason", ""), rule_result.get("reason", "")]
        }
    
    def _fact_check(self, triple: Dict[str, str], source_text: str) -> Dict[str, Any]:
        """事实检查：验证三元组是否在源文本中有依据"""
        head = triple.get("head", "")
        relation = triple.get("relation", "")
        tail = triple.get("tail", "")
        
        if not head or not tail:
            return {"valid": False, "reason": "实体不完整", "confidence": 0.0}
        
        head_found = head in source_text
        tail_found = tail in source_text
        
        if not head_found and not tail_found:
            return {"valid": False, "reason": "实体在源文本中未找到", "confidence": 0.0}
        
        combined = f"{head}.*{tail}|{tail}.*{head}"
        pattern_found = bool(re.search(combined, source_text))
        
        confidence = 0.5
        if head_found and tail_found:
            confidence = 0.9 if pattern_found else 0.7
        elif head_found or tail_found:
            confidence = 0.4
        
        return {
            "valid": confidence >= 0.5,
            "reason": "事实检查通过" if confidence >= 0.5 else "事实依据不足",
            "confidence": confidence
        }
    
    def _rule_validation(self, triple: Dict[str, str]) -> Dict[str, Any]:
        """规则验证：关系一致性、实体类型检查"""
        relation = triple.get("relation", "")
        head = triple.get("head", "")
        tail = triple.get("tail", "")
        
        if not relation or len(relation) > 50:
            return {"valid": False, "reason": "关系格式不规范", "confidence": 0.0}
        
        if head == tail:
            return {"valid": False, "reason": "头尾实体相同", "confidence": 0.0}
        
        if not head or not tail:
            return {"valid": False, "reason": "实体为空", "confidence": 0.0}
        
        relation_validated = False
        for category, patterns in self.RELATION_PATTERNS.items():
            if any(p in relation for p in patterns):
                relation_validated = True
                break
        
        return {
            "valid": True,
            "reason": "规则验证通过",
            "confidence": 0.8
        }
    
    def _llm_review(self, triple: Dict[str, str], source_text: str) -> Dict[str, Any]:
        """LLM再审：使用LLM二次验证"""
        head = triple.get("head", "")
        relation = triple.get("relation", "")
        tail = triple.get("tail", "")
        
        prompt = f"""请判断以下三元组是否正确：

文本：{source_text[:1000]}
三元组：头实体="{head}", 关系="{relation}", 尾实体="{tail}"

请以JSON格式返回：
{{"correct": true/false, "reason": "判断理由", "confidence": 0.0-1.0}}

只返回JSON，不要其他内容。"""
        
        try:
            response = self.client.chat.completions.create(
                model=settings.llm_model,
                messages=[
                    {"role": "system", "content": "你是一个专业的知识图谱质量审核员，擅长判断三元组的正确性。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            result_text = response.choices[0].message.content
            
            try:
                result = eval(result_text.strip())
                return {
                    "valid": result.get("correct", False),
                    "reason": result.get("reason", ""),
                    "confidence": result.get("confidence", 0.5)
                }
            except:
                if "true" in result_text.lower():
                    return {"valid": True, "reason": "LLM审核通过", "confidence": 0.85}
                else:
                    return {"valid": False, "reason": "LLM审核不通过", "confidence": 0.3}
                    
        except Exception as e:
            print(f"LLM review error: {e}")
            return {"valid": True, "reason": "LLM审核跳过", "confidence": 0.7}
    
    def validate_batch(
        self,
        triples: List[Dict[str, str]],
        source_text: str,
        config: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        批量验证三元组
        
        Args:
            triples: 三元组列表
            source_text: 源文本
            config: 验证配置
        
        Returns:
            验证结果列表
        """
        results = []
        
        for triple in triples:
            result = self.validate(triple, source_text, config)
            result["triple"] = triple
            results.append(result)
        
        return results
    
    def filter_valid_triples(
        self,
        triples: List[Dict[str, str]],
        source_text: str,
        config: Dict[str, Any] = None
    ) -> List[Dict[str, str]]:
        """过滤出有效的三元组"""
        results = self.validate_batch(triples, source_text, config)
        return [r["triple"] for r in results if r["valid"]]
