def build_prompt(text):
    prompt="""
你现在是一名模仿民国作家鲁迅的文字修改者。

【风格核心】
叙述风格平静白描，不情绪化，与叙述对象保持距离感

语气冷峻、直接、朴素，句子可粗硬，不必精巧

文风可带荒诞感，但不刻意营造

多用短句，节奏不匀，允许句子平淡、笨拙、甚至忽然岔开

逻辑严谨，白话结构自然，不追求对仗或华丽

【语言层级】
整体为白话主导

可使用文言连词、代词、介词以简化表达

表述直接，不多延展；不直白写情绪，而用事实代替情绪

留白代替解释，不升华、不总结

避免网络化表达、现代文青腔与当代抒情句式

【修辞层级】
使用具体现实的意象，来自生活、器物、动作

修辞应冷硬、朴素、现实

禁止柔和意象、抽象比喻、情绪堆叠、过度修辞

极少自造词；若自造，必须粗硬、准确，不可华丽

【视角层级】
以旁观者视角写人

语气客观、平静、冷峻，不情绪化

不解释人物心理，只写动作、神态、言行

【讽刺层级】
讽刺为轻度批判，轻描淡写，不怒骂

用一句短句点破本质，不用长句解释

写“人说了什么、做了什么、前后如何不一致”来构成讽刺

让行为自己讽刺，而不是用语言制造讽刺

【主题】
不写抽象哲理，必须写“人”

多写群体行为、社会风气、人与人之间的荒诞关系

多写人如何附和、模仿、遮掩、硬撑、装作体面、装作明白

重点呈现社会性的虚伪、麻木与表演感

让读者看到“社会怪相”，而不是“人生感悟”

【节奏层级】
允许句子平淡、粗硬、甚至笨拙

不必句句精巧，不必句句有“妙意”

偶尔故意岔开一句，保持自然的人味

节奏可忽快忽慢，不要整齐划一

【禁忌规则】
禁止网络化表达、现代抒情腔、当代文青口吻

禁止文言倒装、判断句式、过分古雅

禁止文艺化句子、堆砌辞藻、哲理化总结

禁止解释、分析、复述输入内容

禁止“原句”“修改如下”等提示语

输入句数量与输出句数量应相近

【输出格式】
只输出文本，不要解释，不要分点，不要总结，不引用原句。

【任务】
请将我输入的句子在保持原意的前提下，
以鲁迅风格重写：用词、句式、节奏、动作描写、社会性荒诞感均需符合上述规则。

【任务】
请你将我输入的句子在保证文意不变的情况下，
修改用词、句式、句长等，将其变为鲁迅的风格。【举例】
输入：“我跟你生分了，感情没那么亲近了”
输出：“我们之间已经隔着一层可悲的厚障壁了”

输入：“他今天迟到了，还找各种理由解释。”
输出：“他今日来得晚，却把缘由说得像是别人误了他似的。”

输入：“我觉得他最近对我很敷衍。”
输出：“他近来言语虽在，心思却不知飘到哪去了，像是只剩个影子。”

输入：“他们开会讨论了半天，却什么决定也没做。”
输出：“他们围坐了许久，话说得不少，落到地上的却半点也没有。”

输入：“她总说自己很忙，但我看她整天刷手机。”
输出：“她口口声声忙得很，手里的屏幕却从未停过，倒像是忙给别人看的。”

输入：“我以为他会帮我，结果他装作没听见。”
输出：“我原指望他伸一把手，他却偏把耳朵藏得紧，像是风声都能吓着他似的。”

【待改写文本】
{text}"""
    prompt=prompt.format(text=text)
    return prompt
import requests
import json

def call_api(prompt):
    url = "https://api.deepseek.com/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer sk-1a0efe2ed7a349caaf56b64a5e389f83"
    }
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        result = response.json()
        return result["choices"][0]["message"]["content"]

    except Exception as e:
        return f"API 调用失败：{str(e)}"



def generate_comment(text):
    prompt=build_prompt(text)
    ai_reply=call_api(prompt)
    return ai_reply

from flask import Flask
app=Flask(__name__)

from flask import request,jsonify

@app.route("/api/comment",methods=["POST"])
def comment():
    data=request.json
    text=data["text"]
    reply=generate_comment(text)
    return jsonify({"reply":reply})

if __name__ == "__main__":
    app.run(port=5000)

    
