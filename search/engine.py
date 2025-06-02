from abc import ABC, abstractclassmethod, abstractmethod
import os
from minio import Minio
from opensearchpy import OpenSearch
from sentence_transformers import SentenceTransformer, CrossEncoder, util
from ragatouille import RAGPretrainedModel
import torch
from osearch.cluster import OSExecutor
from utils.log import logger
from typing import List, Dict, Any
from dotenv import load_dotenv, find_dotenv
import torch
import numpy as np

device = 'cuda' if torch.cuda.is_available() else 'cpu'

load_dotenv(find_dotenv(), override=True)

class AbstractRetriever(ABC):
    @abstractmethod
    def retrieve(self, query: str, index_name: str, top_k: int):
        pass

    @abstractmethod
    def rerank(self, query: str, docs: List[str], top_k: int):
        pass
    
    @abstractmethod
    def rag_query(query: str, index: str, top_k: int):
        pass

class Retriever(AbstractRetriever):
    def __init__(self):
        self.os_executor = OSExecutor()
        self.available_strans = ['BAAI/bge-large-en-v1.5', 'all-MiniLM-L6-v2']
        self.bi_encoder = SentenceTransformer(self.available_strans[0])  # fast bi-encoder
        self.colbert = RAGPretrainedModel.from_pretrained("colbert-ir/colbertv2.0")
        self.cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

    def retrieve(self, query: str, index_name: str, top_k: int):
        query_vector = self.bi_encoder.encode(query).tolist()

        logger.info(f"[retrieve] top_k: {top_k}")

        script_query = {
            "knn": {
               "chunk_embedding": {
                    "vector": query_vector,
                    "k": top_k
               }
            }
        }


        results = self.os_executor.search(
            index=index_name,
            body={"size": top_k, "query": script_query}
        )

        docs = [
            {"chunk_text": hit["_source"]["chunk_text"], "chunk_embedding": hit["_source"]["chunk_embedding"]}
            for hit in results["hits"]["hits"]
        ]
        logger.info(f"[retrieve] docs: {docs}")
        return docs

    def rerank(self, query, docs, top_k):
        logger.info(f"[rerank] top_k: {top_k}")
        logger.info(f"[rerank] docs: {docs}")
        passages = [doc["chunk_text"] for doc in docs]
        ranked = self.colbert.rerank(query=query, documents=passages, k=top_k)
        logger.info(f"[rerank] ranked: {ranked}")
        return [rank["content"] for rank in ranked]

    def rag_query(self, query: str, index: str, top_k: int = 5):
        if self.os_executor.exists_index(index=index):
            num_entries = self.os_executor.count(index=index)
            logger.info(f"[rag_query] num_entries: {num_entries}")
            retrieved_docs = self.retrieve(query=query, index_name=index, top_k=min(top_k * 5, num_entries))
            logger.info(f"[rag_query] retrieved_docs: {retrieved_docs}")
            reranked_docs = self.rerank(query, docs=retrieved_docs, top_k=min(top_k, num_entries))
            return reranked_docs
        return []
    
class ImageRetriever(AbstractRetriever):
    def __init__(self):
        self.os_executor = OSExecutor()
        self.available_strans = ['BAAI/bge-large-en-v1.5', 'all-MiniLM-L6-v2']
        self.bi_encoder = SentenceTransformer(self.available_strans[0])  # fast bi-encoder
        self.colbert = RAGPretrainedModel.from_pretrained("colbert-ir/colbertv2.0")
        self.cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

    def retrieve(self, query: str, index_name: str, top_k: int):
        query_vector = self.bi_encoder.encode(query).tolist()[:512]

        logger.info(f"[retrieve] top_k: {top_k}")

        script_query = {
            "knn": {
               "image_vector": {
                    "vector": query_vector,
                    "k": top_k
               }
            }
        }


        results = self.os_executor.search(
            index=index_name,
            body={"size": top_k, "query": script_query}
        )

        docs = [
            {"minio_image_id": hit["_source"]["minio_image_id"], "image_vector": hit["_source"]["image_vector"]}
            for hit in results["hits"]["hits"]
        ]
        logger.info(f"[retrieve] docs: {docs}")
        return docs

    def rerank(self, query, docs, top_k):
        logger.info(f"[rerank] top_k: {top_k}")
        logger.info(f"[rerank] docs: {docs}")

        minio_ids = [doc["minio_image_id"] for doc in docs]
        passages = [torch.tensor(doc["image_vector"], device=device) for doc in docs]


        query_embedding = torch.tensor(self.bi_encoder.encode(query, convert_to_tensor=True)[:512]).to(device)
        scores = torch.tensor([util.cos_sim(query_embedding, passage).item() for passage in passages], device=device)
        _, top_indices = torch.topk(scores, k=top_k)
        logger.info(f"Top indices: {top_indices}")
        # Retrieve MinIO IDs for the top-ranked documents
        top_minio_ids = [minio_ids[idx] for idx in top_indices.tolist()]

        responses = []
        for minio_id in top_minio_ids:
            values = minio_id.split('_') # intuition: have ID just be composed so we can query a blob store efficiently (ex. get_object )
            bucket_name, object_name = values[0], values[1]
            logger.info(f"Bucket name: {bucket_name}, object_name: {object_name}")
            client = Minio(
                f"{os.environ['MINIO_HOST']}:{os.environ['MINIO_PORT']}",
                access_key="admin",
                secret_key="Xcaliber#7#",
                secure=False
            )
            response = client.get_object(bucket_name, object_name)
            raw_image_bytes = response.read(512)
            logger.info(f"First 512 bytes: {raw_image_bytes}")
            response.close()
            response.release_conn()

            response = client.get_object(bucket_name, object_name)
            responses.append(response.read())
            response.close()
            response.release_conn()
        
        return responses
    
    def rag_query(self, query: str, index: str, top_k: int = 5):
        if self.os_executor.exists_index(index=index):
            num_entries = self.os_executor.count(index=index)
            logger.info(f"[rag_query] num_entries: {num_entries}")
            retrieved_docs: List[Dict[str, Any]] = self.retrieve(query=query, index_name=index, top_k=min(top_k * 5, num_entries))
            logger.info(f"[rag_query] retrieved_docs: {retrieved_docs}")
            reranked_docs = self.rerank(query, docs=retrieved_docs, top_k=min(top_k, num_entries))
            return reranked_docs
        return []

