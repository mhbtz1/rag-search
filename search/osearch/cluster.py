import logging
from opensearchpy import OpenSearch, AsyncOpenSearch
from typing import Dict

logger = logging.getLogger("osearch-logger")
fh = logging.FileHandler()
fh.setLevel(logging.INFO)
logger.addHandler(fh)

class OSExecutor():
    def __init__(self):
        self.client = OpenSearch(
            hosts=[{"host": "0.0.0.0", "port": 9200}],
            http_compress=True,
            use_ssl=True,
            verify_certs=False
        )
        self.async_client = AsyncOpenSearch(
            hosts=[{"host": "0.0.0.0", "port": 9200}],
            http_compress=True,
            use_ssl=True,
            verify_certs=False
        )

    def create_index(self, index: str, mapping: Dict):
        pass

    
    def list_available_indices(self):
        return self.client.get("*")

    def update_index(self, index: str, document_id: int, body: Dict):
        try:
            logger.info(f"Inserting document {document_id} into index {index} with the following content: {body}")
            self.client.index(index=index, document_id=document_id, body=body)
        except Exception as e:
            raise e
        
    def delete_index(self):
        pass



