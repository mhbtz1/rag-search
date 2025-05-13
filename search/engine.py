from opensearchpy import OpenSearch
from sentence_transformers import SentenceTransformer
from ragatouille import RAGPretrainedModel
from .osearch.cluster import OSExecutor
import numpy as np


os_executor = OSExecutor()

# Step 2: Load models
bi_encoder = SentenceTransformer("all-MiniLM-L6-v2")  # fast bi-encoder
colbert = RAGPretrainedModel.from_pretrained("colbert-ir/colbertv2.0")

# Step 3: Retrieve with OpenSearch
def retrieve(query, index_name="docs", top_k=20):
    query_vector = bi_encoder.encode(query).tolist()
    script_query = {
        "script_score": {
            "query": {"match_all": {}},
            "script": {
                "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                "params": {"query_vector": query_vector}
            }
        }
    }

    results = os_executor.search(
        index=index_name,
        body={"size": top_k, "query": script_query}
    )

    docs = [
        {"id": hit["_id"], "title": hit["_source"]["title"], "text": hit["_source"]["text"]}
        for hit in results["hits"]["hits"]
    ]
    return docs

def rerank(query, docs, top_n=5):
    passages = [doc["text"] for doc in docs]
    ranked = colbert.rerank(query=query, passages=passages, k=top_n)
    return [docs[i] for i in ranked["indices"]]

def rag_query(query):
    retrieved_docs = retrieve(query)
    reranked_docs = rerank(query, retrieved_docs)
    return reranked_docs
