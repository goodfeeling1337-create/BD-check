"""Simple queries over the graph."""
from __future__ import annotations

from typing import Optional

from app.core.semantic.triples import TripleStore, Triple


def get_task_subject(role: str, task_num: int) -> str:
    return f"sol:{role}:task:{task_num}"


def get_repeating_group(store: TripleStore, role: str) -> set[str]:
    """Get repeating group attributes (task 2)."""
    subj = get_task_subject(role, 2)
    triples = store.find(s=subj, p="repeating_group_contains")
    return {t.o for t in triples if isinstance(t.o, str)}


def get_table_1nf(store: TripleStore, role: str) -> Optional[tuple[list[str], list[list]]]:
    """Get (canon_headers, rows) for task 3; None if not present."""
    subj = get_task_subject(role, 3)
    h = store.find_one(s=subj, p="table_1nf_headers")
    r = store.find_one(s=subj, p="table_1nf_rows")
    if h is not None and isinstance(h.o, list) and r is not None and isinstance(r.o, list):
        return (list(h.o), list(r.o))
    return None


def get_pk_hint(store: TripleStore, role: str) -> list[str]:
    """Get PK hint from task 3 (headers with *)."""
    subj = get_task_subject(role, 3)
    t = store.find_one(s=subj, p="pk_hint_contains")
    if t and isinstance(t.o, list):
        return list(t.o)
    return []


def get_text(store: TripleStore, role: str, task_num: int) -> str:
    """Get text content for task 10 or 12."""
    subj = get_task_subject(role, task_num)
    t = store.find_one(s=subj, p="text_content")
    return t.o if t and isinstance(t.o, str) else ""


def get_attributes(store: TripleStore, role: str, task_num: int = 1) -> list[str]:
    """Get canon attribute names for universal relation from task 1."""
    subj = get_task_subject(role, task_num)
    triples = store.find(s=subj, p="has_attribute")
    return [t.o for t in triples if isinstance(t.o, str)]


def get_fds(store: TripleStore, role: str, task_num: int = 4) -> list[tuple[list[str], str]]:
    """Get (lhs_list, rhs) FDs for a task."""
    subj = get_task_subject(role, task_num)
    fd_ids = [t.o for t in store.find(s=subj, p="has_fd") if isinstance(t.o, str)]
    result = []
    for fid in fd_ids:
        lhs = []
        for t in store.find(s=fid, p="lhs_contains"):
            lhs.append(t.o)
        rhs_t = store.find_one(s=fid, p="rhs_is")
        rhs = rhs_t.o if rhs_t and isinstance(rhs_t.o, str) else ""
        if rhs:
            result.append((lhs, rhs))
    return result


def get_pk(store: TripleStore, role: str, task_num: int = 5) -> list[str]:
    """Get primary key attributes."""
    subj = get_task_subject(role, task_num)
    t = store.find_one(s=subj, p="primary_key_contains")
    if t and isinstance(t.o, list):
        return list(t.o)
    # fallback: collect all primary_key_contains
    out = []
    for t in store.find(s=subj, p="primary_key_contains"):
        if isinstance(t.o, str):
            out.append(t.o)
    return out


def get_relations(store: TripleStore, role: str, task_num: int) -> list[tuple[str, set[str]]]:
    """Get (name, set(attrs)) for task 11 or 13."""
    subj = get_task_subject(role, task_num)
    rel_ids = [t.o for t in store.find(s=subj, p="contains_relation") if isinstance(t.o, str)]
    result = []
    for rid in rel_ids:
        name_t = store.find_one(s=rid, p="label")
        name = name_t.o if name_t and isinstance(name_t.o, str) else rid
        attrs = set()
        for t in store.find(s=rid, p="has_attribute"):
            if isinstance(t.o, str):
                attrs.add(t.o)
        result.append((name, attrs))
    return result
