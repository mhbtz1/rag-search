from opensearchpy import OpenSearch
from sentence_transformers import SentenceTransformer, CrossEncoder
from ragatouille import RAGPretrainedModel
from osearch.cluster import OSExecutor
from utils.log import logger
import numpy as np


class Retriever:
    os_executor = OSExecutor()
    available_strans = ['BAAI/bge-large-en-v1.5', 'all-MiniLM-L6-v2']
    bi_encoder = SentenceTransformer(available_strans[0])  # fast bi-encoder
    colbert = RAGPretrainedModel.from_pretrained("colbert-ir/colbertv2.0")
    cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

    def retrieve(self, query: str, index_name: str, top_k=20):
        query_vector = self.bi_encoder.encode(query).tolist()
        script_query = {
            "script_score": {
                "query": {"match_all": {}},
                "script": {
                    "source": "cosineSimilarity(params.query_vector, 'chunk_embedding') + 1.0",
                    "params": {"query_vector": query_vector}
                }
            }
        }

        results = self.os_executor.search(
            index=index_name,
            body={"size": top_k, "query": script_query}
        )

        docs = [
            {"id": hit["_id"], "chunk_text": hit["_source"]["chunk_text"], "chunk_embedding": hit["_source"]["chunk_embedding"]}
            for hit in results["hits"]["hits"]
        ]
        return docs

    def rerank(self, query, docs, top_k):
        passages = [doc["chunk_text"] for doc in docs]
        ranked = self.colbert.rerank(query=query, passages=passages, k=top_k)
        return [docs[i] for i in ranked["indices"]]

    def rag_query(self, query: str, index: str, top_k: int = 5):
        retrieved_docs = self.retrieve(query=query, index_name=index, top_k=(top_k * 5))
        logger.info(f"[rag_query] retrieved_docs: {retrieved_docs}")
        reranked_docs = self.rerank(query, docs=retrieved_docs, top_k=top_k)
        return reranked_docs
