from neo4j import GraphDatabase
from typing import Optional, Dict, Any
from app.core.config import settings


class Neo4jClient:
    def __init__(self):
        self.driver = get_neo4j_driver()
    
    def close(self):
        if self.driver:
            self.driver.close()
    
    def create_entity(self, name: str, entity_type: str = "Entity", properties: dict = None):
        """创建实体节点"""
        properties = properties or {}
        query = """
        MERGE (e:Entity {name: $name})
        SET e.type = $type, e += $properties
        """
        with self.driver.session() as session:
            session.run(query, name=name, type=entity_type, properties=properties)
    
    def create_relationship(self, head: str, tail: str, relation: str, properties: dict = None):
        """创建关系"""
        properties = properties or {}
        query = """
        MATCH (a:Entity {name: $head})
        MATCH (b:Entity {name: $tail})
        MERGE (a)-[r:RELATION {type: $relation}]->(b)
        SET r += $properties
        """
        with self.driver.session() as session:
            session.run(query, head=head, tail=tail, relation=relation, properties=properties)
    
    def get_entities(self, limit: int = 100):
        """获取实体列表"""
        query = "MATCH (e:Entity) RETURN e LIMIT $limit"
        with self.driver.session() as session:
            result = session.run(query, limit=limit)
            return [dict(record["e"]) for record in result]
    
    def get_relationships(self, entity_name: str = None, limit: int = 100):
        """获取关系列表"""
        if entity_name:
            query = """
            MATCH (a:Entity {name: $name})-[r]->(b:Entity)
            RETURN a.name as head, r.type as relation, b.name as tail
            LIMIT $limit
            """
            with self.driver.session() as session:
                result = session.run(query, name=entity_name, limit=limit)
        else:
            query = """
            MATCH (a:Entity)-[r:RELATION]->(b:Entity)
            RETURN a.name as head, r.type as relation, b.name as tail
            LIMIT $limit
            """
            with self.driver.session() as session:
                result = session.run(query, limit=limit)
        
        return [{"head": r["head"], "relation": r["relation"], "tail": r["tail"]} for r in result]
    
    def execute_cypher(self, query: str):
        """执行Cypher查询"""
        with self.driver.session() as session:
            result = session.run(query)
            return [dict(record) for record in result]
    
    def delete_all(self):
        """删除所有节点和关系"""
        query = "MATCH (n) DETACH DELETE n"
        with self.driver.session() as session:
            session.run(query)


driver = None


def get_neo4j_driver():
    global driver
    if driver is None:
        driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password)
        )
    return driver


def close_neo4j_driver():
    global driver
    if driver:
        driver.close()
        driver = None
