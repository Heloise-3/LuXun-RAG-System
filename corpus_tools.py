"""Offline corpus validation and index provenance. Never invokes a model."""
import hashlib
import json
import math
from pathlib import Path
from pydantic import BaseModel, Field
from typing import Literal

class Passage(BaseModel):
    id: int | str
    source: str = Field(min_length=1)
    text: str = Field(min_length=1, max_length=5000)
    tone: list[str]
    theme: list[str]
    device: list[str]
    narrative: str = Field(min_length=1)
    work: str = ''
    edition: str = ''
    location: str = ''
    source_url: str = ''
    provenance_status: Literal['unverified','verified'] = 'unverified'
    editorial_note: str = ''

def validate_rows(rows, require_verified=False):
    if not isinstance(rows, list) or not rows:
        raise ValueError('corpus must be a nonempty JSON array')
    clean=[]; ids=set(); texts=set()
    for row in rows:
        item=Passage.model_validate(row).model_dump()
        if str(item['id']) in ids or item['text'].strip() in texts:
            raise ValueError('duplicate id or passage')
        ids.add(str(item['id'])); texts.add(item['text'].strip())
        if require_verified or item['provenance_status'] == 'verified':
            if item['provenance_status'] != 'verified' or not item['work'].strip() or not (item['source_url'].strip() or (item['edition'].strip() and item['location'].strip())):
                raise ValueError('verified passages need work and source URL or edition plus location')
        clean.append(item)
    return clean

def corpus_hash(rows):
    return hashlib.sha256(json.dumps(rows,sort_keys=True,ensure_ascii=False).encode()).hexdigest()

def load_index_file(path):
    from embedding import embedding_model
    path=Path(path)
    data=json.loads(path.read_text(encoding='utf-8'))
    # Legacy index is retained for demonstration; its model identity was not recorded.
    if isinstance(data, list):
        rows=data
        corpus=json.loads((path.parent/'corpus.json').read_text(encoding='utf-8'))
        canonical=validate_rows(corpus)
        indexed=validate_rows(rows)
        texts=lambda items: {str(r['id']):r['text'] for r in items}
        if texts(canonical) != texts(indexed):
            raise ValueError('legacy corpus changed; rebuild index')
        vectors={str(r['id']):r['embedding'] for r in rows}
        rows=[dict(r,embedding=vectors[str(r['id'])]) for r in canonical]
    else:
        if data['model'] != embedding_model():
            raise ValueError('embedding model changed; rebuild index')
        rows=data['passages']
        corpus=json.loads((path.parent/'corpus.json').read_text(encoding='utf-8'))
        if data['corpus_sha256'] != corpus_hash(corpus):
            raise ValueError('corpus changed; rebuild index')
    clean=validate_rows(rows)
    dimensions=set()
    for row,item in zip(rows,clean):
        vector=row['embedding']
        if not isinstance(vector,list) or not vector or not all(isinstance(v,(int,float)) and math.isfinite(v) for v in vector):
            raise ValueError('invalid embedding')
        dimensions.add(len(vector));item['embedding']=vector
    if len(dimensions)!=1:
        raise ValueError('inconsistent embedding dimension')
    return clean

if __name__ == '__main__':
    import argparse
    parser=argparse.ArgumentParser(description='Validate corpus offline; does not verify quotations against sources.')
    parser.add_argument('path', nargs='?', default=str(Path(__file__).parent/'corpus.json'))
    parser.add_argument('--require-verified',action='store_true')
    args=parser.parse_args()
    rows=validate_rows(json.loads(Path(args.path).read_text(encoding='utf-8')),args.require_verified)
    print(f'Validated {len(rows)} passages; {sum(r["provenance_status"] == "unverified" for r in rows)} unverified. Source accuracy still requires human review.')
