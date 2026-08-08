from openai import OpenAI
import json
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

def analyze_query(query):
    prompt=f"""
You are a literary style analyzer.
Analyze the following writing request.
Query:{query}

return only valid JSON.

output format:
{{
"tone":[],
"theme":[],
"device":[],
"narrative":""
}}

Rules:
-use short English tags
-no explanation
-no markdown
-narrative must be only one short tag

example:{{
  "tone":["cold","satirical"],
  "theme":["crowd","apathy"],
  "device":["irony","contrast"],
  "narrative":"observer"
}}
"""
    response = client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3)
    content = response.choices[0].message.content

    return json.loads(content)
if __name__ == "__main__":
    print(analyze_query("写一段关于看客心理和群体麻木的场景"))