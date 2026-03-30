from typing import List, Dict, Any, Optional
import numpy as np
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility


class MilvusClient:
    """Milvus向量数据库客户端"""
    
    def __init__(self, host: str = "localhost", port: int = 19530):
        self.host = host
        self.port = port
        self.connected = False
        self.collection = None
    
    def connect(self):
        """连接到Milvus"""
        try:
            connections.connect(host=self.host, port=self.port)
            self.connected = True
            return True
        except Exception as e:
            print(f"Milvus connection error: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """断开连接"""
        if self.connected:
            connections.disconnect("default")
            self.connected = False
    
    def create_collection(self, name: str, dimension: int = 384):
        """创建向量集合"""
        if not self.connected:
            self.connect()
        
        if utility.has_collection(name):
            utility.drop_collection(name)
        
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="entity_id", dtype=DataType.VARCHAR, max_length=256),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=4096),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=dimension)
        ]
        
        schema = CollectionSchema(fields, description=f"ERC-KG {name} collection")
        collection = Collection(name, schema)
        
        index_params = {
            "index_type": "IVF_FLAT",
            "metric_type": "L2",
            "params": {"nlist": 128}
        }
        collection.create_index("embedding", index_params)
        
        self.collection = collection
        return collection
    
    def insert_vectors(
        self, 
        collection_name: str, 
        entity_ids: List[str], 
        texts: List[str], 
        embeddings: List[List[float]]
    ):
        """插入向量"""
        if not self.connected:
            self.connect()
        
        collection = Collection(collection_name)
        data = [
            entity_ids,
            texts,
            embeddings
        ]
        
        insert_result = collection.insert(data)
        collection.flush()
        return insert_result
    
    def search(
        self,
        collection_name: str,
        query_embedding: List[float],
        top_k: int = 10,
        expr: str = None
    ) -> List[Dict[str, Any]]:
        """向量搜索"""
        if not self.connected:
            self.connect()
        
        collection = Collection(collection_name)
        collection.load()
        
        search_params = {
            "metric_type": "L2",
            "params": {"nprobe": 10}
        }
        
        results = collection.search(
            data=[query_embedding],
            anns_field="embedding",
            param=search_params,
            limit=top_k,
            expr=expr,
            output_fields=["entity_id", "text"]
        )
        
        search_results = []
        for hits in results:
            for hit in hits:
                search_results.append({
                    "id": hit.id,
                    "entity_id": hit.entity.get("entity_id"),
                    "text": hit.entity.get("text"),
                    "distance": hit.distance
                })
        
        return search_results
    
    def delete_collection(self, name: str):
        """删除集合"""
        if not self.connected:
            self.connect()
        
        if utility.has_collection(name):
            utility.drop_collection(name)
    
    def list_collections(self) -> List[str]:
        """列出所有集合"""
        if not self.connected:
            self.connect()
        
        return utility.list_collections()


milvus_client = MilvusClient()
