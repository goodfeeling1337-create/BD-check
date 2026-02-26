"""Unit tests for 2NF/3NF checks."""
import pytest
from app.core.algos.keys import candidate_keys
from app.core.algos.normal_forms import check_2nf, check_3nf


def test_check_2nf_ok():
    attrs = {"A", "B", "C"}
    F = [(["A", "B"], "C")]
    keys = candidate_keys(attrs, F)
    ok, violations = check_2nf(attrs, F, keys)
    assert ok is True
    assert violations == []


def test_check_2nf_partial_violation():
    attrs = {"A", "B", "C"}
    F = [(["A", "B"], "C"), (["A"], "C")]
    keys = candidate_keys(attrs, F)
    assert len(keys) == 1
    ok, violations = check_2nf(attrs, F, keys)
    assert ok is False
    assert len(violations) >= 1


def test_check_3nf_ok():
    attrs = {"A", "B", "C"}
    F = [(["A"], "B"), (["A"], "C")]
    keys = candidate_keys(attrs, F)
    ok, violations = check_3nf(attrs, F, keys)
    assert ok is True


def test_check_3nf_violation():
    attrs = {"A", "B", "C"}
    F = [(["A"], "B"), (["B"], "C")]
    keys = candidate_keys(attrs, F)
    ok, violations = check_3nf(attrs, F, keys)
    assert ok is False
    assert len(violations) >= 1
