import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.normalization import normalize_scores
import pytest
import math

def test_min_max_normalization_basic():
    ## Basic case
    scores = [10.0, 20.0]
    normalized = normalize_scores(scores, mode='min-max')
    assert normalized == [0.0, 1.0]

def test_min_max_zero_range():
    ## All scores identical
    scores = [5.0, 5.0, 5.0]
    normalized = normalize_scores(scores, mode='min-max')
    assert normalized == [0.5, 0.5, 0.5]

def test_min_max_negative_scores():
    ## Negative values/zero scores
    scores = [-0.5, 0.0, 0.5]
    normalized = normalize_scores(scores, mode='min-max')
    assert normalized == [0.0, 0.5, 1.0]

def test_z_score_normalization_basic():
    ## Basic case
    scores = [1.0, 2.0, 3.0]
    normalized = normalize_scores(scores, mode='z-score')
    mean = 2.0
    std_dev = math.sqrt(( (1-2)**2 + (2-2)**2 + (3-2)**2 ) / 3 )
    expected = [(x - mean)/std_dev for x in scores]
    assert normalized == pytest.approx(expected, rel=1e-3)

def test_z_score_zero_variance():
    ## All scores identical
    scores = [4.0, 4.0, 4.0]
    normalized = normalize_scores(scores, mode='z-score')
    assert normalized == [0.0, 0.0, 0.0]

def test_empty_input():
    assert normalize_scores([]) == []

def test_invalid_mode():
    with pytest.raises(ValueError):
        normalize_scores([1,2,3], mode='invalid')