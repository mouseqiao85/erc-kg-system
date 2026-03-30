from typing import List, Dict, Any, Optional
import numpy as np
from collections import Counter
import re
import jieba
from sklearn.feature_extraction.text import TfidfVectorizer


class EntityRetriever:
    """
    实体语料检索器
    
    流程：
    1. 特征词抽取：使用 TF-IDF/TextRank 提取关键词
    2. 向量化：使用 Sentence-BERT 对句子和实体进行向量化
    3. 语义检索：计算实体与句子的语义相似度
    4. 区间离散化：应用相似度区间系数 α 进行筛选
    5. 长度控制：自适应控制文本长度
    """
    
    def __init__(
        self,
        embedding_model=None,
        alpha: float = 0.8,
        top_k: int = 10,
        max_length: int = 4096
    ):
        self.embedding_model = embedding_model
        self.alpha = alpha
        self.top_k = top_k
        self.max_length = max_length
        self.tfidf_vectorizer = TfidfVectorizer(
            tokenizer=jieba.cut,
            max_features=5000,
            ngram_range=(1, 2)
        )
    
    def extract_keywords(self, text: str, top_n: int = 20) -> List[str]:
        """提取关键词"""
        words = jieba.cut(text)
        word_list = [w for w in words if len(w) > 1]
        word_freq = Counter(word_list)
        
        try:
            tfidf_matrix = self.tfidf_vectorizer.fit_transform([' '.join(word_list)])
            feature_names = self.tfidf_vectorizer.get_feature_names_out()
            tfidf_scores = tfidf_matrix.toarray()[0]
            
            word_scores = list(zip(feature_names, tfidf_scores))
            word_scores.sort(key=lambda x: x[1], reverse=True)
            
            return [w for w, _ in word_scores[:top_n]]
        except:
            return [w for w, _ in word_freq.most_common(top_n)]
    
    def get_embeddings(self, texts: List[str]) -> Optional[np.ndarray]:
        """获取文本向量嵌入"""
        if self.embedding_model is None:
            return None
        
        try:
            embeddings = self.embedding_model.encode(texts)
            return embeddings
        except Exception as e:
            print(f"Embedding error: {e}")
            return None
    
    def compute_similarity(self, embeddings1: np.ndarray, embeddings2: np.ndarray) -> np.ndarray:
        """计算余弦相似度"""
        norm1 = np.linalg.norm(embeddings1, axis=1, keepdims=True)
        norm2 = np.linalg.norm(embeddings2, axis=1, keepdims=True)
        
        normalized1 = embeddings1 / (norm1 + 1e-8)
        normalized2 = embeddings2 / (norm2 + 1e-8)
        
        return np.dot(normalized1, normalized2.T)
    
    def retrieve(
        self,
        entity: str,
        corpus: List[str],
        entity_description: str = ""
    ) -> List[Dict[str, Any]]:
        """
        检索与实体相关的语料
        
        Args:
            entity: 实体名称
            corpus: 候选句子列表
            entity_description: 实体描述（可选）
        
        Returns:
            排序后的语料列表，包含句子和相似度分数
        """
        if not corpus:
            return []
        
        results = []
        
        combined_entity = entity
        if entity_description:
            combined_entity = f"{entity}: {entity_description}"
        
        if self.embedding_model is not None:
            entity_embedding = self.embedding_model.encode([combined_entity])
            corpus_embeddings = self.embedding_model.encode(corpus)
            
            similarities = self.compute_similarity(entity_embedding, corpus_embeddings)[0]
            
            for i, (sentence, score) in enumerate(zip(corpus, similarities)):
                results.append({
                    "sentence": sentence,
                    "score": float(score),
                    "index": i
                })
        else:
            keywords = self.extract_keywords(combined_entity)
            entity_keywords = set(keywords[:10])
            
            for i, sentence in enumerate(corpus):
                sentence_keywords = set(jieba.cut(sentence))
                overlap = len(entity_keywords & sentence_keywords)
                score = overlap / (len(entity_keywords) + 1)
                
                results.append({
                    "sentence": sentence,
                    "score": score,
                    "index": i
                })
        
        results.sort(key=lambda x: x["score"], reverse=True)
        
        filtered_results = [
            r for r in results 
            if r["score"] >= self.alpha * max(r["score"] for r in results) if results else 0
        ]
        
        selected = filtered_results[:self.top_k]
        
        total_length = 0
        final_results = []
        for r in selected:
            if total_length + len(r["sentence"]) > self.max_length:
                break
            final_results.append(r)
            total_length += len(r["sentence"])
        
        return final_results
    
    def split_into_sentences(self, text: str) -> List[str]:
        """将文本分割成句子"""
        sentences = re.split(r'[。！？；\n]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences
    
    def retrieve_from_document(
        self,
        entity: str,
        document_content: str,
        entity_description: str = ""
    ) -> List[Dict[str, Any]]:
        """从文档中检索实体相关语料"""
        sentences = self.split_into_sentences(document_content)
        return self.retrieve(entity, sentences, entity_description)
