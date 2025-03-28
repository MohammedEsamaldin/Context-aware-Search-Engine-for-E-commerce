import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from src.modules.fusion.fuse import fuse_candidates

## Mock data
BM25_CANDIDATES = [
    {"productId": "prod001", "score": 25.4},
    {"productId": "prod002", "score": 22.1},
    {"productId": "prod003", "score": 19.7},
    {"productId": "prod004", "score": 17.3},
    {"productId": "prod005", "score": 0.82} #15.0
]

VECTOR_CANDIDATES = [
    {"productId": "prod003", "score": 0.95},
    {"productId": "prod004", "score": 0.89},
    {"productId": "prod005", "score": 0.82},
    {"productId": "prod006", "score": 0.75},
    {"productId": "prod007", "score": 0.68}
]

## =============================================================
#   CANDIDATE MERGING
## =============================================================
def test_full_overlap(beta=0.5):
    ## Same product (e.g. 'prod003') appearing in both lists

def test_partial_overlap(beta=0.5):
    ## Product appearing (e.g. 'prod001') appearing ONLY in BM25 but not Vector list

def test_full_overlap(beta=0.5):
    ## Two products having identical final scores (e.g. prod005: 0.82)
          

## =============================================================
#   EDGE CASES
## =============================================================
def test_beta_extremes():
    ## Beta=1 (Only BM25 score remains)
    result_beta1 = fuse_candidates(BM25_CANDIDATES, VECTOR_CANDIDATES, beta=1.0)
    assert [x["productId"] for x in result_beta1[:2]] == ["prod001", "prod002"]

    ## Beta=0 (Only Vector score remains)
    result_beta0 = fuse_candidates(BM25_CANDIDATES, VECTOR_CANDIDATES, beta=0.0)
    assert [x["productId"] for x in result_beta0[:2]] == ["prod003", "prod004"]

    ## Beta=0.5 (Average)
    result_beta05 = fuse_candidates(BM25_CANDIDATES, VECTOR_CANDIDATES, beta=0.5)
    assert 

## =============================================================
#   BUSINESS LOGIC
## =============================================================
def test_top_n_truncation():
    result = fuse_candidates(BM25_CANDIDATES, VECTOR_CANDIDATES, top_n=3)
    assert len(result) == 3
    assert result[0]["productId"] == "prod003"

def test_negative_top_n():
    with pytest.raises(ValueError):
        fuse_candidates(BM25_CANDIDATES, VECTOR_CANDIDATES, top_n=-1)

def test_invalid_inputs():
    ## Empty lists
    with pytest.raises(ValueError):
        fuse_candidates([], VECTOR_CANDIDATES)
    
    ## Missing score field
    bad_bm25 = [{"productId": "prod001"}]
    with pytest.raises(ValueError):
        fuse_candidates(bad_bm25, VECTOR_CANDIDATES)

#        

def test_successful_fusion():
    result = fuse_candidates(BM25_CANDIDATES, VECTOR_CANDIDATES, beta=0.6)
    
    # Verify ordering
    expected_order = ["prod003", "prod001", "prod004", "prod002", "prod005", "prod006", "prod007"]
    assert [x["productId"] for x in result] == expected_order
    
    # Verify score calculations
    prod003 = next(x for x in result if x["productId"] == "prod003")
    assert prod003["score"] == pytest.approx(0.67, 0.01)




def test_missing_scores():
    ## Test missing candidates get 0 for missing score type
    result = fuse_candidates(
        [{"productId": "prod999", "score": 10}],
        [{"productId": "prod888", "score": 0.5}],
        beta=0.5
    )
    
    prod999 = next(x for x in result if x["productId"] == "prod999")
    assert prod999["score"] == pytest.approx(0.5 * 1.0 + 0.5 * 0.0)  # BM25 only


