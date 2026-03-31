from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:postgres@localhost:5432/erc_kg"
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password"
    milvus_host: str = "localhost"
    milvus_port: int = 19530
    redis_url: str = "redis://localhost:6379"
    
    # LLM API Configuration
    llm_base_url: str = "http://oneapi-comate.baidu-int.com/v1"
    llm_api_key: str = "sk-c9O8GBpqd5xOSEph1e2b29643d294eC2Ae412c41935720A1"
    llm_api_type: str = "anthropic-messages"
    llm_model: str = "glm-5-openclaw"
    llm_temperature: float = 0.7
    
    # Available models
    llm_models: list = ["glm-5-openclaw", "deepseek-v3.1", "ERNIE-5.0", "glm-4.7-internal"]
    
    # Baidu Search API Configuration
    baidu_search_api_key: str = ""
    
    secret_key: str = "secret-key-change-in-production"
    access_token_expire_minutes: int = 30
    
    debug: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
