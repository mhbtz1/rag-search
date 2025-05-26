from sentence_transformers import SentenceTransformer

model = SentenceTransformer("BAAI/bge-large-en-v1.5")
embedding = model.encode("What is 12+15?").tolist()
print(embedding)