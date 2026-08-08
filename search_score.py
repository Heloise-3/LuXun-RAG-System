import json
import numpy as np
from embedding import embed_text
from query_analyzer import analyze_query

def cosine(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def compute_overlap(list1,list2):
    if len(list1)==0 or len(list2)==0:
        return 0
    set1=set(list1)
    set2=set(list2)
    overlap=set1&set2
    union=set1 | set2
    return len(overlap)/len(union)

def compute_metadata_score(
        query_meta,
        item
):
    tone_score=compute_overlap(query_meta['tone'],item['tone'])
    theme_score=compute_overlap(query_meta['theme'],item['theme'])
    device_score=compute_overlap(query_meta['device'],item['device'])

    if query_meta['narrative']==item['narrative']:
        narrative_score=1
    else:
        narrative_score=0

    metadata_score=(tone_score*0.25)+(theme_score*0.25)+(device_score*0.15)+(narrative_score*0.35)
    return metadata_score

def search_similar(query, top_k=3):
    query_emb = embed_text(query)
    query_meta = analyze_query(query)

    with open("corpus_embeddings.json", "r", encoding="utf8") as f:
        data = json.load(f)

    scored = []
    for item in data:
        semantic_score = cosine(query_emb, item['embedding'])
        metadata_score = compute_metadata_score(query_meta, item)
        final_score = 0.6 * semantic_score + 0.4 * metadata_score
        scored.append({"item": item, 
                       "semantic_score":semantic_score,
                       "metadata_score":metadata_score,
                       "final_score":final_score,
                       } )

    scored.sort(reverse=True, key=lambda x: x['final_score'])
    return scored[:top_k]

if __name__ == "__main__":
    print(search_similar("写一段关于看客心理和群体麻木的场景", top_k=1))