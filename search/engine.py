from abc import ABC, abstractclassmethod, abstractmethod
from opensearchpy import OpenSearch
from sentence_transformers import SentenceTransformer, CrossEncoder
from ragatouille import RAGPretrainedModel
from osearch.cluster import OSExecutor
from utils.log import logger
from typing import List
import numpy as np

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
        num_entries = self.os_executor.count(index=index)
        logger.info(f"[rag_query] num_entries: {num_entries}")
        retrieved_docs = self.retrieve(query=query, index_name=index, top_k=min(top_k * 5, num_entries))
        logger.info(f"[rag_query] retrieved_docs: {retrieved_docs}")
        reranked_docs = self.rerank(query, docs=retrieved_docs, top_k=min(top_k, num_entries))
        return reranked_docs
