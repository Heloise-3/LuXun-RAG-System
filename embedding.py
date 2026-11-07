"""Embedding provider; imported safely without credentials."""
import os
from config import make_client

def embedding_model():
    return os.getenv('EMBEDDING_MODEL', 'Qwen/Qwen3-Embedding-8B')

def embed_text(text: str) -> list[float]:
    with make_client('siliconflow') as client:
        response = client.embeddings.create(model=embedding_model(), input=text)
    return response.data[0].embedding

if __name__ == '__main__':
    print(len(embed_text('你好')))
