"""Build TripleStore graph from ParsedSolution."""
from typing import Optional
from app.core.checks.common import canon_attr_for_compare
from app.core.excel.importer import ParsedSolution, ExtractedTable
from app.core.semantic.triples import TripleStore


def _task_subject(role: str, task_num: int) -> str:
    return f"sol:{role}:task:{task_num}"


def _add_universal_relation(store: TripleStore, role: str, attrs: list[str]) -> None:
    subj = _task_subject(role, 1)
    store.add(subj, "has_task", 1)
    store.add(subj, "universal_relation", True)
    for a in attrs:
        store.add(subj, "has_attribute", a)


def _add_table_1nf(store: TripleStore, role: str, headers: list[str], rows: list[list]) -> None:
    subj = _task_subject(role, 3)
    store.add(subj, "has_task", 3)
    canon_headers = [canon_attr_for_compare(h) for h in headers]
    for c in canon_headers:
        store.add(subj, "has_attribute", c)
    pk_hint = [canon_attr_for_compare(h) for h in headers if h and ("*" in str(h).strip() or str(h).strip().endswith("*"))]
    if pk_hint:
        store.add(subj, "pk_hint_contains", pk_hint)
    # Store row count for checks
    store.add(subj, "row_count", len(rows))


def _add_fds(store: TripleStore, role: str, task_num: int, fd_list: list[tuple[list[str], str]]) -> None:
    subj = _task_subject(role, task_num)
    store.add(subj, "has_task", task_num)
    for i, (lhs, rhs) in enumerate(fd_list):
        fid = f"fd:{role}:{task_num}:{i}"
        store.add(subj, "has_fd", fid)
        for a in lhs:
            store.add(fid, "lhs_contains", canon_attr_for_compare(a) if isinstance(a, str) else a)
        store.add(fid, "rhs_is", canon_attr_for_compare(rhs) if isinstance(rhs, str) else rhs)


def _add_pk(store: TripleStore, role: str, pk_list: list[str]) -> None:
    subj = _task_subject(role, 5)
    store.add(subj, "has_task", 5)
    store.add(subj, "primary_key_contains", [canon_attr_for_compare(a) for a in pk_list])


def _add_relations(store: TripleStore, role: str, task_num: int, relations: list[tuple[str, set[str]]]) -> None:
    subj = _task_subject(role, task_num)
    store.add(subj, "has_task", task_num)
    for name, attrs in relations:
        rid = f"rel:{role}:{task_num}:{name}"
        store.add(subj, "contains_relation", rid)
        store.add(rid, "label", name)
        for a in attrs:
            store.add(rid, "has_attribute", a)


def _add_text_anomaly(store: TripleStore, role: str, task_num: int, text: str) -> None:
    subj = _task_subject(role, task_num)
    store.add(subj, "has_task", task_num)
    store.add(subj, "text_content", text)


def build_graph(solution: ParsedSolution, role: str, attr_canon_list: Optional[list[str]] = None) -> TripleStore:
    """
    Build graph from ParsedSolution. If attr_canon_list is None, task 1 is used to build it.
    """
    store = TripleStore()
    # Task 1: universal relation headers
    t1 = solution.tasks.get(1)
    if t1 and t1.tables:
        headers = t1.tables[0].headers
        attrs = [canon_attr_for_compare(h) for h in headers if str(h).strip()]
        if attrs:
            _add_universal_relation(store, role, attrs)
    elif attr_canon_list:
        _add_universal_relation(store, role, attr_canon_list)

    # Task 3: 1NF table
    t3 = solution.tasks.get(3)
    if t3 and t3.tables:
        tbl = t3.tables[0]
        _add_table_1nf(store, role, tbl.headers, tbl.rows)

    # Tasks 4,6,7,8,9: FDs are added by check modules after parsing; we only add structure here
    for tn in [4, 6, 7, 8, 9]:
        t = solution.tasks.get(tn)
        if t:
            store.add(_task_subject(role, tn), "has_task", tn)

    # Task 5: PK
    t5 = solution.tasks.get(5)
    if t5:
        store.add(_task_subject(role, 5), "has_task", 5)

    # Task 10, 12: text
    for tn in [10, 12]:
        t = solution.tasks.get(tn)
        if t and t.text_lines:
            _add_text_anomaly(store, role, tn, " ".join(t.text_lines))

    # Tasks 11, 13: relations are added by check modules after extraction
    for tn in [11, 13]:
        t = solution.tasks.get(tn)
        if t:
            store.add(_task_subject(role, tn), "has_task", tn)

    return store
