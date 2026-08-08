import json
from embedding import embed_text

with open("corpus.json","r",encoding="utf8")as f:
    corpus:list[dict]=json.load(f)

output=[]
for item in corpus:
    emb=embed_text(item["text"])
    output.append({"id":item["id"],
                   "source":item["source"],
                   "text":item["text"],
                   "tone":item["tone"],
                   "theme":item["theme"],
                   "narrative":item["narrative"],
                   "device":item["device"],
                   "embedding":emb})
print(output[0])
with open("corpus_embeddings.json","w",encoding="utf8") as f:
    json.dump(output,f,ensure_ascii=False)