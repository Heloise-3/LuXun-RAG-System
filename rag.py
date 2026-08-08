from search_score import search_similar
from query_analyzer import analyze_query
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

def retrieve_context(query,top_k=3):
    context_blocks = []
    results = search_similar(query,top_k=top_k)

    print("\n[DEBUG] Retrieved Chunks:")

    for result in results:

        item = result["item"]

        print(
            f"""
            id={item['id']}
            semantic_score={result['semantic_score']:.3f}
            metadata_score={result['metadata_score']:.3f}
            final_score={result['final_score']:.3f}
            tone={item['tone']}
            theme={item['theme']}
            narrative={item['narrative']}"""
        )

        tone=", ".join(item.get("tone",[]))
        theme=", ".join(item.get("theme",[]))
        device=", ".join(item.get("device",[]))
        narrative=item.get("narrative","")

        block=f"""[
        source:{item["source"]}
        tone:{tone}
        theme:{theme}
        device:{device}
        narrative:{narrative}
        text:{item["text"]}]"""

        context_blocks.append(block)

    return "\n\n".join(context_blocks)

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
    
    response = client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.5
    )

    return response.choices[0].message.content



def generate_with_rag(query, top_k=3):
    query_meta = analyze_query(query)

    context = retrieve_context(query,top_k)

    prompt = build_prompt(query,context,query_meta)

    output = call_model(prompt)

    return output
    
    
query="写一段关于看客心理和群体麻木的场景"

print(generate_with_rag(query))
