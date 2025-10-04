import requests
import numpy as np

OLLAMA_HOST = "http://localhost:11434"
MODEL_NAME = "nomic-embed-text"

def text_to_vector(text: str, model: str = MODEL_NAME):
    url = f"{OLLAMA_HOST}/api/embeddings"
    resp = requests.post(url, json={"model": model, "prompt": text})
    resp.raise_for_status()
    vec = np.array(resp.json()["embedding"], dtype="float32")
    # 單位化，方便後續 cosine 相似度
    vec /= np.linalg.norm(vec) + 1e-12
    return vec

if __name__ == "__main__":
    with open("news1.txt", "r", encoding="utf-8") as f:
        content = f.read()

    vec = text_to_vector(content)
    print("向量維度:", vec.shape)     # 應該是 (768,)
    print("前 10 維:", vec[:10])
