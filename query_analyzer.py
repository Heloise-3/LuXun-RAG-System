import json
import re
from pydantic import BaseModel, Field, field_validator
from config import ROOT, make_client, model_name

# Read the same vocabulary the corpus editor uses; do not invent parallel labels.
TAXONOMY = {
    name: re.findall(r'"([^"]+)"', block)
    for name, block in re.findall(
        r'(tone|theme|device|narrative):\[(.*?)\]',
        (ROOT / 'dictionary.md').read_text(encoding='utf-8'), re.S
    )
}

class QueryMetadata(BaseModel):
    tone: list[str] = Field(max_length=20)
    theme: list[str] = Field(max_length=20)
    device: list[str] = Field(max_length=20)
    narrative: str = Field(min_length=1, max_length=80)

    @field_validator('tone', 'theme', 'device', 'narrative')
    @classmethod
    def require_known_tags(cls, value, info):
        tags = [value] if info.field_name == 'narrative' else value
        if any(tag not in TAXONOMY[info.field_name] for tag in tags):
            raise ValueError(f'{info.field_name} must use the corpus vocabulary')
        return value

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

Allowed vocabulary (choose only exact values from the matching category):
{json.dumps(TAXONOMY, ensure_ascii=False)}

Rules:
-use only the allowed vocabulary above, never synonyms or invented labels
-for tone/theme/device, use [] if no allowed tag fits
-narrative must be exactly one allowed narrative tag
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
    with make_client('deepseek') as client:
        response = client.chat.completions.create(
        model=model_name(),
        extra_body={"thinking": {"type": "disabled"}},
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3,
        max_tokens=512,
        response_format={"type": "json_object"})
    content = response.choices[0].message.content

    return QueryMetadata.model_validate(json.loads(content)).model_dump()
if __name__ == "__main__":
    print(analyze_query("写一段关于看客心理和群体麻木的场景"))