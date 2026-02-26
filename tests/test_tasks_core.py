"""Core task helpers and common tests."""
import pytest
from app.core.checks.common import (
    canon_attr_for_compare,
    parse_fd_string,
    normalize_fd_arrow,
    is_separator_row,
    build_attribute_dictionary,
    extract_attrs_via_dictionary_simple,
    SEPARATOR_ROW_RE,
)


def test_canon_attr():
    assert canon_attr_for_compare("  A  ") == "a"
    assert canon_attr_for_compare("A*") == "a"
    assert canon_attr_for_compare("A *") == "a"


def test_parse_fd_string():
    out = parse_fd_string("A, B -> C")
    assert len(out) == 1
    assert out[0][0] == ["a", "b"]
    assert out[0][1] == ["c"]
    out2 = parse_fd_string("A -> B, C")
    assert len(out2) == 1
    assert out2[0][1] == ["b", "c"]


def test_parse_fd_string_multiword():
    d = build_attribute_dictionary(["код товара", "адрес поставщика", "наименование"])
    out = parse_fd_string("Код товара, Адрес поставщика -> Наименование", dictionary=d)
    assert len(out) == 1
    assert set(out[0][0]) == {"код товара", "адрес поставщика"}
    assert out[0][1] == ["наименование"]


def test_normalize_fd_arrow():
    assert "->" in normalize_fd_arrow("A → B")
    assert "->" in normalize_fd_arrow("A -> B")
    assert "->" in normalize_fd_arrow("A -- B")
    assert "->" in normalize_fd_arrow("A => B")


def test_parse_fd_semicolon_and_newline():
    """FD split by ; and newline; LHS/RHS by comma/semicolon only."""
    out = parse_fd_string("A,B -> C; D,E -> F")
    assert len(out) == 2
    assert out[0][0] == ["a", "b"] and out[0][1] == ["c"]
    assert out[1][0] == ["d", "e"] and out[1][1] == ["f"]
    out2 = parse_fd_string("A -> B\nC -> D")
    assert len(out2) == 2
    assert out2[0][1] == ["b"] and out2[1][0] == ["c"] and out2[1][1] == ["d"]


def test_is_separator_row():
    assert is_separator_row(["", "", ""]) is True
    assert is_separator_row([".....", "…"]) is True
    assert is_separator_row(["a", "b"]) is False


def test_separator_regex():
    assert SEPARATOR_ROW_RE.match(".....")
    assert SEPARATOR_ROW_RE.match("…")
    assert not SEPARATOR_ROW_RE.match("a")


def test_build_attribute_dictionary():
    d = build_attribute_dictionary(["a", "b", "c"])
    assert d["a"] == "a"
    assert canon_attr_for_compare("A") in d


def test_extract_attrs_via_dictionary_simple():
    d = build_attribute_dictionary(["id", "name", "code"])
    found = extract_attrs_via_dictionary_simple("id, name, code", d)
    assert set(found) <= set(d.keys())
    found2 = extract_attrs_via_dictionary_simple("id name code", d)
    assert len(found2) >= 1


def test_extract_multiword_attrs():
    d = build_attribute_dictionary(["код товара", "адрес поставщика"])
    found = extract_attrs_via_dictionary_simple("код товара и адрес поставщика", d)
    assert set(found) <= {"код товара", "адрес поставщика"}
    assert len(found) >= 1
