from search_score import search_similar
from query_analyzer import analyze_query
from config import make_client, model_name


def format_context(results):
    return "\n\n".join(
        f"[id:{r['item']['id']} source:{(r['item'].get('work') or r['item']['source'])} "
        f"tone:{r['item']['tone']} theme:{r['item']['theme']} "
        f"device:{r['item']['device']} narrative:{r['item']['narrative']} "
        f"text:{r['item']['text']}]" for r in results
    )


def retrieve_context(query, top_k=2, query_meta=None):
    return format_context(search_similar(query, top_k=top_k, query_meta=query_meta))

def build_prompt(query,context,query_meta):
    tone = ", ".join(query_meta["tone"])
    theme = ", ".join(query_meta["theme"])
    device = ", ".join(query_meta["device"])
    narrative = query_meta["narrative"]
    prompt=f"""
你现在是一名模仿民国作家鲁迅的文字创作者。

-整体为白话,可使用文言连词、代词、介词简化表达

-修辞使用具体现实的意象

-极少自造词；若自造，必须粗硬、准确，不可华丽 

-讽刺用一句短句点破本质
 
-节奏不要整齐划一 

-禁止网络化表达、现代抒情腔
 
-禁止文言倒装、判断句式、过分古雅 

-输入句数量与输出句数量应相近 
【Narrative Rules】

The entire text MUST maintain the same narrative throughout.
Rules:

- Maintain narrative consistency.
- No author-summary endings.
- No philosophical conclusions.
- No lyrical reflection.
- No romanticized suffering.
- No modern sentimental tone.
- Avoid beautiful prose cadence.
 
【输出格式】 
只输出文本，不要解释，不要分点，不要总结，不引用原句。 
 
【任务】 
请以鲁迅风格写一段文本：用词、句式、节奏、动作描写、社会性荒诞感均需符合上述规则。 

【举例】 

输入：“他们开会讨论了半天，却什么决定也没做。” 
输出：“他们围坐了许久，话说得不少，落到地上的却半点也没有。” 

下面是与你任务相关的鲁迅文本片段,以及从中抽取出的风格与人格特征(tone, theme, device, narrative):
【Query Style Analysis and Target Personality】

tone:
{tone}

theme:
{theme}

device:
{device}

narrative:
{narrative}

{context}
请尽量保持以上 tone/theme/device/narrative 所体现的人格特征。

请围绕以下主题：{query}
生成一段新的文字
"""
    return prompt

def call_model(prompt):
    
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
        max_tokens=1200,
        temperature=0.5
    )

    content = response.choices[0].message.content
    if not content or not content.strip():
        raise ValueError("empty model output")
    return content



def generate_with_rag(query, top_k=2):
    query_meta = analyze_query(query)

    results = search_similar(query, top_k=top_k, query_meta=query_meta)
    context = format_context(results)

    prompt = build_prompt(query,context,query_meta)

    output = call_model(prompt)

    return {
    "query": query,
    "metadata": query_meta,
    "context": context,
    "retrieval": [dict(rank=i, item={k:v for k,v in r["item"].items() if k != "embedding"},
                       semantic_score=r["semantic_score"], metadata_score=r["metadata_score"],
                       final_score=r["final_score"]) for i,r in enumerate(results,1)],
    "output": output}
    
    
if __name__ == "__main__":
    query="写一段关于看客心理和群体麻木的场景"
    print(generate_with_rag(query))
