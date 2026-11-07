import pytest
from search_score import cosine, search_similar

META = {'tone':['cold'], 'theme':['crowd'], 'device':['irony'], 'narrative':'observer'}

def test_zero_vectors_have_no_similarity():
    assert cosine([0, 0], [1, 0]) == 0

def test_dimension_mismatch_is_actionable():
    with pytest.raises(ValueError, match='dimension'):
        cosine([1, 0], [1, 0, 0])

def test_ranking_selects_subset_and_does_not_reanalyze(monkeypatch):
    import search_score
    monkeypatch.setattr(search_score, 'embed_text', lambda q: [1,0])
    monkeypatch.setattr(search_score, 'analyze_query', lambda q: pytest.fail('duplicate analysis'))
    rows = [dict(META, id=i, source='test', text=str(i), embedding=v) for i,v in [(1,[0,1]),(2,[1,0]),(3,[-1,0])]]
    monkeypatch.setattr(search_score, 'load_index', lambda: rows)
    results = search_similar('request', top_k=1, query_meta=META)
    assert [r['item']['id'] for r in results] == [2]
    assert results[0]['final_score'] == pytest.approx(1)
