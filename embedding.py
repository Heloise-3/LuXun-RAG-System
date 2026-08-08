from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("SILICONFLOW_API_KEY"),
    base_url="https://api.siliconflow.com/v1"
)
def embed_text(text:str)->list[float]:
    response=client.embeddings.create(
        model="Qwen/Qwen3-Embedding-8B",
        input=text)
    return response.data[0].embedding
    
if __name__ == "__main__":
    print(len(embed_text("你好")))



