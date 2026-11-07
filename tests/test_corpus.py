import json
import pytest
from corpus_tools import validate_rows, corpus_hash, load_index_file

ROW={'id':1,'source':'LuXun','text':'test only','tone':[], 'theme':[], 'device':[], 'narrative':'observer'}

def test_verified_requires_traceable_source():
    with pytest.raises(ValueError,match='verified'):
        validate_rows([ROW],require_verified=True)
    row=dict(ROW,work='test',source_url='https://example.org/source',provenance_status='verified')
    assert validate_rows([row],require_verified=True)[0]['work'] == 'test'

def test_duplicate_passages_rejected():
    with pytest.raises(ValueError,match='duplicate'):
        validate_rows([ROW,dict(ROW,id=2)])

def test_stale_index_rejected_before_embedding_call(tmp_path):
    (tmp_path/'corpus.json').write_text(json.dumps([ROW]))
    envelope={'model':'Qwen/Qwen3-Embedding-8B','corpus_sha256':corpus_hash([ROW]),'passages':[dict(ROW,embedding=[1,0])]}
    path=tmp_path/'corpus_embeddings.json';path.write_text(json.dumps(envelope))
    assert len(load_index_file(path)) == 1
    (tmp_path/'corpus.json').write_text(json.dumps([dict(ROW,text='changed')]))
    with pytest.raises(ValueError,match='rebuild'):
        load_index_file(path)

def test_legacy_index_rejects_edited_corpus(tmp_path):
    path=tmp_path/'corpus_embeddings.json'
    path.write_text(json.dumps([dict(ROW,embedding=[1,0])]))
    (tmp_path/'corpus.json').write_text(json.dumps([dict(ROW,text='changed')]))
    with pytest.raises(ValueError,match='rebuild'):
        load_index_file(path)

def test_legacy_index_uses_current_tags_when_text_matches(tmp_path):
    path=tmp_path/'corpus_embeddings.json'
    path.write_text(json.dumps([dict(ROW,embedding=[1,0])]))
    (tmp_path/'corpus.json').write_text(json.dumps([dict(ROW,tone=['cold'])]))
    assert load_index_file(path)[0]['tone'] == ['cold']
