import httpx
import pytest
from fastapi.testclient import TestClient
from openai import APITimeoutError, APIStatusError
import main
import rag

client = TestClient(main.app)
META = {'tone':['cold'], 'theme':['crowd'], 'device':['irony'], 'narrative':'observer'}

def test_web_assets_are_served():
    assert client.get('/').status_code == 200
    assert '/static/app.js' in client.get('/').text
    assert client.get('/static/app.js').status_code == 200

@pytest.mark.parametrize('payload', [{'query':''}, {'query':'   '}, {'query':'x'*1001}, {'query':'x','top_k':0}, {'query':'x','top_k':6}, {}])
def test_invalid_input_does_not_call_pipeline(payload, monkeypatch):
    monkeypatch.setattr(main, 'generate_with_rag', lambda *a: pytest.fail('provider called'))
    assert client.post('/api/generate', json=payload).status_code == 422

def test_http_runs_real_pipeline_with_mocked_provider_boundaries(monkeypatch):
    import search_score
    calls=[]
    monkeypatch.setattr(rag, 'analyze_query', lambda q: calls.append(q) or META)
    monkeypatch.setattr(search_score, 'embed_text', lambda q: [1,0])
    rows=[dict(META,id=i,source='Test fixture',text='fixture passage',embedding=v) for i,v in [(1,[0,1]),(2,[1,0]),(3,[-1,0])]]
    monkeypatch.setattr(search_score, 'load_index', lambda: rows)
    monkeypatch.setattr(rag, 'call_model', lambda prompt: 'MOCK output')
    response=client.post('/api/generate',json={'query':' crowd ', 'top_k':1})
    assert response.status_code == 200
    data=response.json()
    assert data['query'] == 'crowd'
    assert data['output'] == 'MOCK output'
    assert len(calls) == 1
    assert data['retrieval'][0]['item']['id'] == 2
    assert 'embedding' not in data['retrieval'][0]['item']
    assert 'fixture passage' in data['context']

def test_missing_key_is_safe_and_server_starts_without_keys(monkeypatch):
    monkeypatch.delenv('DEEPSEEK_API_KEY',raising=False)
    response=client.post('/api/generate',json={'query':'test'})
    assert response.status_code == 503
    assert 'DEEPSEEK_API_KEY' in response.json()['detail']

def test_provider_timeout_and_error_are_sanitized(monkeypatch):
    def fail(*args):
        raise APITimeoutError(request=httpx.Request('POST','https://example.com'))
    monkeypatch.setattr(main,'generate_with_rag',fail)
    assert client.post('/api/generate',json={'query':'test'}).status_code == 504
    def leak(*args):
        raise APIStatusError('SECRET_PROVIDER_BODY',response=httpx.Response(401,request=httpx.Request('POST','https://example.com')),body=None)
    monkeypatch.setattr(main,'generate_with_rag',leak)
    response=client.post('/api/generate',json={'query':'test'})
    assert response.status_code == 502
    assert 'SECRET' not in response.text

def test_context_keeps_source_when_work_title_is_missing():
    row=dict(META,id=1,source='LuXun',work='',text='test passage')
    assert 'source:LuXun' in rag.format_context([{'item':row}])
