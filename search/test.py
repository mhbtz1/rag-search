from sentence_transformers import SentenceTransformer
import requests
import json

model = SentenceTransformer("BAAI/bge-large-en-v1.5")
embedding = model.encode("What is 12+15?").tolist()

url = "https://localhost:9200/large-embedding-index/_search"
headers = {"Content-Type": "application/json"}

payload = {
    "size": 1,
    "query": {
        "knn": {
            "chunk_embedding": {
                "vector": embedding,
                "k": 1
            }
        }
    }
}

res = requests.post(url, headers=headers, data=json.dumps(payload), auth=("admin", "Xcaliber#7#"), verify=False)
print(res.json())

