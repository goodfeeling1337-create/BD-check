"""Core task helpers and common tests."""
import pytest
from app.core.checks.common import (
    canon_attr_for_compare,
    parse_fd_string,
    normalize_fd_arrow,
    is_separator_row,
    build_attribute_dictionary,
    extract_attrs_via_dictionary,
)


def test_canon_attr():
    assert canon_attr_for_compare("  A  ") == "a"
    assert canon_attr_for_compare("A*") == "a"
    assert canon_attr_for_compare("A *") == "a"


def test_parse_fd_string():
    out = parse_fd_string("A, B -> C")
    assert len(out) == 1
    assert out[0][0] == ["A", "B"]
    assert out[0][1] == ["C"]
    out2 = parse_fd_string("A -> B, C")
    assert len(out2) == 1
    assert out2[0][1] == ["B", "C"]


def test_normalize_fd_arrow():
    assert "->" in normalize_fd_arrow("A → B")
    assert "->" in normalize_fd_arrow("A -> B")


def test_is_separator_row():
    assert is_separator_row(["", "", ""]) is True
    assert is_separator_row([".....", "…"]) is True
    assert is_separator_row(["a", "b"]) is False


def test_build_attribute_dictionary():
    d = build_attribute_dictionary(["a", "b", "c"])
    assert d["a"] == "a"
    assert canon_attr_for_compare("A") in d


def test_extract_attrs_via_dictionary():
    d = build_attribute_dictionary(["id", "name", "code"])
    found = extract_attrs_via_dictionary("id, name, code", d)
    assert set(found) <= set(d.keys())
    found2 = extract_attrs_via_dictionary("id name code", d)
    assert len(found2) >= 1
