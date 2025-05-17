from pydantic import BaseModel
from typing import Dict, Any

class SentenceEmbeddingConfiguration(BaseModel):
    available_models: Dict[str, Any] = {
        "baai": {"model": 'BAAI/bge-large-en-v1.5', "dim": 1024},
        "minilm": {"model": "all-MiniLM-L6-v2", "dim": 324}
    }
    
    def fetch_model_name(self, model_alias: str) -> str:
        return self.available_models[model_alias]["model"]

    def fetch_model_dim(self, model_alias: str) -> str:
        return self.available_models[model_alias]["model"]

