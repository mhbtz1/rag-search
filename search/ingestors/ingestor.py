import io
import nltk
# nltk.data.path.append("/root/nltk_data")
import uuid
from abc import ABC, abstractmethod
from typing import List, Optional
from sentence_transformers import SentenceTransformer
from unstructured.partition.pdf import partition_pdf
from unstructured.chunking.basic import chunk_elements
from unstructured.chunking.title import chunk_by_title
from unstructured.partition.html import partition_html
from configurations.models import SentenceEmbeddingConfiguration
from osearch.cluster import OSExecutor
from utils.log import logger

class Ingestor(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def parse(self, document_path: str, document_content: io.BytesIO, strategy: str):
        pass

    @abstractmethod
    def embed(self, document_path: Optional[str]=None, document_content: Optional[List[str]]=None, strategy: Optional[str]=None):
        """
        Allow chunking to apply on either the document path (reading the content and chunking it according to strategy), or using pre-parsed content.
        """
        pass    

class PDFIngestor(Ingestor):
    def __init__(self):
        self.model_settings = SentenceEmbeddingConfiguration()
        self.os_executor = OSExecutor()

    def parse(self, document_content: io.BytesIO, strategy: str, document_path: Optional[str]=None):
        logger.info(f"Parsing document with strategy [{strategy}]...")
        if not (document_path or document_content):
            raise Exception()

        elements = partition_pdf(
            file=document_content,
            strategy=strategy,
            infer_table_structure=True,
            extract_images_in_pdf=True
        )
        
        from unstructured.documents.elements import NarrativeText, Text, Title, ListItem, Table
        
        chunks = chunk_by_title(
            elements=elements,
            max_characters=1500,
            new_after_n_chars=1200,
            overlap=200
        )

        logger.info(f"[parse] raw chunks: {chunks}")
        text_chunks = []
        
        for el in chunks:
            text = el.text.strip()
            if hasattr(el, "text"):
                text = el.text.strip()
                if text:
                    text_chunks.append(text)
        
        logger.info(f"[parse] text_chunks: {text_chunks}")
        return text_chunks
    

    def embed(self, index: str, model_alias: str, document_path: Optional[str]=None, document_content: Optional[List[str]]=None, strategy: Optional[str]=None):
        if not (document_path or document_content):
            raise Exception("Make sure to either pass a document or pre-chunked content!")
        
        logger.info(f"Embedding w/ embedding mode {model_alias} into index {index}")
        if not document_content:
            document_content = self.parse(document_path)
        
        model_name = "BAAI/bge-large-en-v1.5" if model_alias == "large" else "BAAI/bge-small-en-v1.5"
        dim = 1024 if model_alias == "large" else 384
        model = SentenceTransformer(model_name)

        for chunk in document_content:
            logger.info(f"[embed] chunk: {chunk}")
            embedding = model.encode(chunk).tolist()
            if not self.os_executor.exists_index(index=index):
                mapping = {
                    "settings": {
                        "index": {
                            "knn": True
                        }
                    },
                    "mappings": {
                        "properties": {
                            "chunk_embedding": {
                                "type": "knn_vector",
                                "dimension": dim,
                                "method": {
                                    "name": "hnsw",
                                    "space_type": "cosinesimil",
                                    "engine": "nmslib"
                                }
                            },
                            "chunk_id": {
                                "type": "keyword"
                            },
                            "chunk_text": {
                                "type": "text"
                            }
                        }
                    }
                }
                self.os_executor.create_index(index=index, mapping=mapping)
            
            chunk_id = str(uuid.uuid4())
            document_id = str(uuid.uuid4())
            self.os_executor.update_index(index=index, document_id=document_id, body = {"chunk_embedding": embedding, "chunk_text": chunk, 
                                                                                                  "chunk_id": chunk_id})


class DocxIngestor(Ingestor): 
    def __init__():
        pass

    def parse(self, document_path: str, document_content: io.BytesIO, strategy: str):
        if not (document_path or document_content):
            raise Exception()
        
        elements = partition_pdf(
            document_path,
            strategy=strategy,
            infer_table_structure=True,
            extrat_images_in_pdf=True
        )
        
        chunks = chunk_by_title(
            elements,
            max_characters=1500,
            new_after_n_chars=1200,
            overlap=200
        )

        serialized_chunks = []
        for chunk in chunks:
            if chunk.type not in ["Image", "Table"]:
                serialized_chunks.append(chunk.text)
        
        return serialized_chunks
    
    def embed(self, index: str, model_alias: str, document_path: Optional[str]=None, document_content: Optional[List[str]]=None, strategy: Optional[str]=None):
        if not (document_path or document_content):
            raise Exception("Make sure to either pass a document or pre-chunked content!")
        
        if not document_content:
            document_content = self.parse(document_path)
        
        model_name = "BAAI/bg-large-en" if model_alias == "large" else "BAAI/bge-small-en"
        model = SentenceTransformer(model_name)

        for chunk in document_content:
            embedding = model.encode(chunk).tolist()
            if not self.os_executor.exists_index(index=index):
                mapping = {
                    "mappings": {
                        "properties": {
                            "chunk_embedding": {
                                "type": "knn_vector",
                                "dimension": 1024 if model_alias == "large" else 384,
                                "method": {
                                    "name": "hnsw",
                                    "space_type": "cosinesimil",
                                    "engine": "nmslib"
                                }
                            },
                            "chunk_id": {
                                "type": "keyword"
                            },
                            "chunk_text": {
                                "type": "text"
                            }
                        }
                    }
                }
                self.os_executor.create_index(index=index, mapping=mapping)
                chunk_id = str(uuid.uuid4())
                document_id = str(uuid.uuid4())
                self.os_executor.update_index(index=index, document_id=document_id, body = {"document_embedding": embedding, "chunk_text": chunk, 
                                                                                                  "chunk_id": chunk_id, "document_id": document_id})
class CSVIngestor(Ingestor):
    def __init__():
        pass

    def parse(self, document_path: str, document_content: io.BytesIO, strategy: str):
        if not (document_path or document_content):
            raise Exception()
        

        elements = partition_pdf(
            document_path,
            strategy=strategy,
            infer_table_structure=True,
            extract_images_in_pdf=True
        ) if document_path else partition_pdf(
            document_content,
            strategy=strategy,
            infer_table_structure=True,
            extract_images_in_pdf=True
        ) 
        
        chunks = chunk_by_title(
            elements,
            max_characters=1500,
            new_after_n_chars=1200,
            overlap=200
        )

        serialized_chunks = []
        for chunk in chunks:
            if chunk.type not in ["Image", "Table"]:
                serialized_chunks.append(chunk.text)
        
        return serialized_chunks
    

    def embed(self, index: str, model_alias: str, document_path: Optional[str]=None, document_content: Optional[List[str]]=None, strategy: Optional[str]=None):
        pass

    
if __name__ == "__main__":
    ingestor = PDFIngestor()
    content = ingestor.parse(document_path="Florida_ma_contracts_1.pdf", strategy="hi_res")
    ingestor.embed(index="test-index", model_alias="baai", document_content=content)
    print(f"content: {content}")