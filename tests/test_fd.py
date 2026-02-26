"""Unit tests for closure and minimal_cover."""
import pytest
from app.core.algos.fd import closure, minimal_cover


def test_closure_trivial():
    F = []
    assert closure([], F) == set()
    assert closure(["A"], F) == {"A"}


def test_closure_simple():
    F = [(["A"], "B"), (["B"], "C")]
    assert closure(["A"], F) == {"A", "B", "C"}
    assert closure(["B"], F) == {"B", "C"}
    assert closure(["C"], F) == {"C"}


def test_closure_multiple_lhs():
    F = [(["A", "B"], "C"), (["A"], "B")]
    assert closure(["A"], F) == {"A", "B", "C"}


def test_minimal_cover_single_rhs():
    F = [(["A"], "B"), (["A"], "C")]
    G = minimal_cover(F)
    assert len(G) == 2
    got = set((tuple(lhs), rhs) for lhs, rhs in G)
    assert got == {(("A",), "B"), (("A",), "C")}


def test_minimal_cover_redundant():
    F = [(["A"], "B"), (["B"], "C"), (["A"], "C")]
    G = minimal_cover(F)
    # A->C is redundant (A+ = {A,B,C})
    assert len(G) == 2
    attrs = set()
    for lhs, rhs in G:
        attrs.add(rhs)
    assert attrs >= {"B", "C"}
