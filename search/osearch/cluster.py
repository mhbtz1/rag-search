import logging
from opensearchpy import OpenSearch
from configurations.opensearch import OpensearchConfiguration
from typing import Any, Dict, Optional
from utils.log import logger

class OSExecutor():
    def __init__(self):
        self.os_config = OpensearchConfiguration()

        self.client = OpenSearch(
            hosts=[{"host": "localhost", "port": 9200}],
            http_auth=self.os_config.user_config.auth_info,
            http_compress=True,
            use_ssl=True,
            verify_certs=False
        )

    def exists_index(self, index: str):
        try:
            result = self.client.indices.exists(index=index)
            return result
        except Exception as e:
            raise e

    def create_index(self, index: str, mapping: Optional[Dict]=None, knn_index: bool = False):
        if mapping is None:
            mapping = {}

        if knn_index:
            mapping.update({"settings": {"index": { "knn": True }}})

        try:
            self.client.indices.create(index=index, body=mapping)
            logger.info(f"Created index {index} with the following schema: {mapping}")
        except Exception as e:
            raise e
    
    def count(self, index: str):
        try:
            num_entries = self.client.count(index=index)['count']
            return num_entries
        except Exception as e:
            raise e

    def list_available_indices(self):
        try:
            indices = [idx["index"] for idx in self.client.cat.indices(format="json")]
            logger.info(f"Listed available indices: {indices}")
            return indices
        except Exception as e:
            raise e

    def update_index(self, index: str, document_id: int, body: Dict):
        try:
            logger.info(f"Inserting document {document_id} into index {index} with the following content: {body}")
            self.client.index(index=index, id=document_id, body=body)
            logger.info(f"Inserting body {body} with document id {document_id} into index {index}")
        except Exception as e:
            raise e
    
    def search(self, index: str, body: Dict[str, Any]):
        try:
            docs = self.client.search(
                index=index,
                body=body
            )
            logger.info(f"[search] index: {index}")
            logger.info(f"[search] body: {body}")
            return docs
        except Exception as e:
            raise e

    def delete_index(self, index_name: str):
        try:
            self.client.indices.delete(index=index_name)
            logger.info(f"Deleting index {index_name}")
        except Exception as e:
            raise e



