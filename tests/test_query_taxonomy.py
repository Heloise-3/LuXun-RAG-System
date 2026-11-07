"""Query metadata must use the same vocabulary as indexed passages."""
import pytest
from query_analyzer import QueryMetadata

VALID={'tone':['cold','restrained'],'theme':['apathy','spectatorship'],'device':['action','contrast'],'narrative':'observer'}

def test_existing_corpus_vocabulary_is_accepted():
    assert QueryMetadata.model_validate(VALID).model_dump()==VALID

@pytest.mark.parametrize('field,value',[('tone',['icy']),('theme',['bystander']),('device',['white-drawing']),('narrative','third_person_camera')])
def test_out_of_vocabulary_tags_cannot_reach_ranking(field,value):
    with pytest.raises(ValueError):
        QueryMetadata.model_validate(dict(VALID,**{field:value}))
