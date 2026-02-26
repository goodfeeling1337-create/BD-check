"""Unit tests for candidate_keys and is_superkey."""
import pytest
from app.core.algos.fd import closure
from app.core.algos.keys import candidate_keys, is_superkey


def test_is_superkey():
    R = {"A", "B", "C"}
    F = [(["A"], "B"), (["B"], "C")]
    assert is_superkey(["A"], R, F) is True
    assert is_superkey(["B"], R, F) is False
    assert is_superkey(["A", "B"], R, F) is True


def test_candidate_keys_simple():
    R = {"A", "B", "C"}
    F = [(["A"], "B"), (["A"], "C")]
    keys = candidate_keys(R, F)
    assert len(keys) == 1
    assert set(keys[0]) == {"A"}


def test_candidate_keys_two():
    R = {"A", "B"}
    F = [(["A"], "B"), (["B"], "A")]
    keys = candidate_keys(R, F)
    assert len(keys) == 2
    keys_set = {frozenset(k) for k in keys}
    assert keys_set == {frozenset({"A"}), frozenset({"B"})}


def test_candidate_keys_composite():
    R = {"A", "B", "C"}
    F = [(["A", "B"], "C")]
    keys = candidate_keys(R, F)
    assert len(keys) == 1
    assert set(keys[0]) == {"A", "B"}


def test_candidate_keys_uses_max_optional():
    """candidate_keys with many optional attrs is bounded (no explosion)."""
    from app.core.settings import KEYS_MAX_OPTIONAL

    # R has 30 attrs, all in RHS of one FD -> one mandatory, 29 optional
    R = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcd")  # 30
    F = [(["A"], b) for b in R if b != "A"]
    keys = candidate_keys(R, F)
    assert len(keys) == 1
    assert keys[0] == frozenset({"A"})
    assert KEYS_MAX_OPTIONAL >= 1
