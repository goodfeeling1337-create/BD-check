"""Canonical attribute names and helpers."""
import re
from typing import Any, Optional, Union

# NBSP and similar
NBSP = "\u00a0"


def canon_attr(raw: str, normalize_yo: bool = True, strip_trailing_markers: bool = True) -> str:
    """
    Single canonical form for attribute names:
    - trim, collapse spaces, casefold, NBSP -> space
    - optional ё->е
    - optional strip trailing * and .
    """
    if not raw:
        return ""
    s = str(raw).replace(NBSP, " ").strip()
    s = re.sub(r"\s+", " ", s)
    s = s.casefold()
    if normalize_yo:
        s = s.replace("ё", "е")
    if strip_trailing_markers:
        s = s.rstrip("*.").strip()
    return s


def canon_attr_for_compare(raw: str) -> str:
    """Canon for comparison only (keep label for display)."""
    return canon_attr(raw, normalize_yo=True, strip_trailing_markers=True)


def build_attribute_dictionary(ref_attrs_canon: list[str]) -> dict[str, str]:
    """Map canon -> canon (identity); used to validate that names are from ref."""
    return {c: c for c in ref_attrs_canon}


def lookup_in_dictionary(dictionary: dict[str, str], candidate: str) -> Optional[str]:
    """Return canon form if candidate (after canon) is in dictionary."""
    c = canon_attr_for_compare(candidate)
    return dictionary.get(c)


def extract_attrs_via_dictionary(text: str, dictionary: dict[str, str]) -> list[str]:
    """
    Extract attribute names from text by matching against dictionary (ref task 1).
    Order of first occurrence preserved.
    """
    found: list[str] = []
    seen: set[str] = set()
    # Split by comma, semicolon, space, newline
    parts = re.split(r"[\s,;]+", text)
    for p in parts:
        p = p.strip()
        if not p:
            continue
        canon = canon_attr_for_compare(p)
        if canon in dictionary and canon not in seen:
            seen.add(canon)
            found.append(canon)
    # Also try whole text as one token
    whole = canon_attr_for_compare(text.strip())
    if whole in dictionary and whole not in seen:
        found.insert(0, whole)
    return found


def normalize_fd_arrow(s: str) -> str:
    """Normalize arrow to '->'. Replace longer sequences first to avoid breaking '->'."""
    s = s.strip()
    for arrow in ["→", "—", "^->", "=>", "--", "->"]:
        if arrow in s:
            s = s.replace(arrow, "->")
    if "-" in s and "->" not in s:
        s = s.replace("-", "->", 1)
    return s


def parse_fd_string(s: str) -> list[tuple[list[str], list[str]]]:
    """
    Parse FD string like 'A, B -> C, D' into [(['A','B'], ['C','D'])].
    RHS can be split into single attributes.
    """
    s = normalize_fd_arrow(s)
    if "->" not in s:
        return []
    left, right = s.split("->", 1)
    lhs = [x.strip() for x in re.split(r"[\s,;]+", left.strip()) if x.strip()]
    rhs = [x.strip() for x in re.split(r"[\s,;]+", right.strip()) if x.strip() and x.strip() != ">"]
    if not lhs or not rhs:
        return []
    return [(lhs, rhs)]


def normalize_cell_value(val: Any) -> str:
    """Trim, number 1.0 -> 1 for comparison."""
    if val is None:
        return ""
    s = str(val).strip()
    try:
        f = float(s)
        if f == int(f):
            return str(int(f))
    except ValueError:
        pass
    return s


def is_separator_row(row: list[Any], max_col: Optional[int] = None) -> bool:
    """Row is only dots/dashes/empty in range."""
    r = row[:max_col] if max_col is not None else row
    for v in r:
        s = (str(v).strip() if v is not None else "")
        if not s:
            continue
        if all(ch in ".- \t…" for ch in s) or s.replace(".", "").replace("…", "") == "":
            continue
        return False
    return True
