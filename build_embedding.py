"""Build a validated, model-labelled index only after explicit cost acknowledgement."""
import argparse
import json
import os
import tempfile
from config import ROOT
from corpus_tools import validate_rows, corpus_hash
from embedding import embed_text, embedding_model

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--confirm-cost',action='store_true',help='Acknowledge paid embedding requests')
    parser.add_argument('--allow-unverified',action='store_true',help='Allow demonstration passages with unverified provenance')
    args=parser.parse_args()
    if not args.confirm_cost:
        parser.error('This sends paid API requests. Review corpus, then pass --confirm-cost.')
    corpus=json.loads((ROOT/'corpus.json').read_text(encoding='utf-8'))
    rows=validate_rows(corpus,require_verified=not args.allow_unverified)
    output=[dict(row,embedding=embed_text(row['text'])) for row in rows]
    payload={'model':embedding_model(),'corpus_sha256':corpus_hash(corpus),'passages':output}
    # Replace only when every request succeeds; preserve the previous index on failure.
    temp_path=None
    try:
        with tempfile.NamedTemporaryFile(mode='w',encoding='utf-8',dir=ROOT,suffix='.json',delete=False) as handle:
            temp_path=handle.name
            json.dump(payload,handle,ensure_ascii=False)
        os.replace(temp_path,ROOT/'corpus_embeddings.json')
    finally:
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)
    print(f'Built {len(output)} passages with {embedding_model()}.')

if __name__ == '__main__':
    main()
