# from sentence_transformers import SentenceTransformer
# import numpy as np

# model = SentenceTransformer("BAAI/bge-small-en-v1.5")

# text = "Python is widely used in AI."

# embedding1 = model.encode(text)
# embedding2 = model.encode(text)

# print("Exactly Equal:", np.array_equal(embedding1, embedding2))
# print("Almost Equal :", np.allclose(embedding1, embedding2))
# print("Max Difference:", np.max(np.abs(embedding1 - embedding2)))


from sentence_transformers import SentenceTransformer

model= SentenceTransformer("BAAI/bge-small-en-v1.5")

text= [
    "Python is the one of the most unique and easy language to learn",
    "I love Virat Kolhi so much and he is my idol from cricket",
    "I am a big Prabhas fan"
]

embeddings= model.encode(text)
print(f"Embeddings are: {len(embeddings)}")

for i, embedding in enumerate(embeddings):
    print(f"\nSentence {i+1}:")
    print(text[i])
    print(f"First 10 values: {embedding[:10]}")