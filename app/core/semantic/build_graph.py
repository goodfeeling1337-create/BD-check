"""Build TripleStore graph from ParsedSolution; populates all task data used by checks."""
from typing import Optional

from app.core.checks import task2, task3, task4, task5, task6, task8, task11, task13
from app.core.checks.common import canon_attr_for_compare
from app.core.excel.importer import ParsedSolution
from app.core.semantic.triples import TripleStore


def _task_subject(role: str, task_num: int) -> str:
    return f"sol:{role}:task:{task_num}"


def _add_universal_relation(store: TripleStore, role: str, attrs: list[str]) -> None:
    subj = _task_subject(role, 1)
    store.add(subj, "has_task", 1)
    store.add(subj, "universal_relation", True)
    for a in attrs:
        store.add(subj, "has_attribute", a)


def _add_repeating_group(store: TripleStore, role: str, attrs: set[str]) -> None:
    subj = _task_subject(role, 2)
    store.add(subj, "has_task", 2)
    for a in attrs:
        store.add(subj, "repeating_group_contains", a)


def _add_table_1nf(store: TripleStore, role: str, headers: list[str], rows: list[list]) -> None:
    subj = _task_subject(role, 3)
    store.add(subj, "has_task", 3)
    canon_headers = [canon_attr_for_compare(h) for h in headers]
    for c in canon_headers:
        store.add(subj, "has_attribute", c)
    store.add(subj, "table_1nf_headers", canon_headers)
    store.add(subj, "table_1nf_rows", rows)
    pk_hint = [canon_attr_for_compare(h) for h in headers if h and ("*" in str(h).strip() or str(h).strip().endswith("*"))]
    if pk_hint:
        store.add(subj, "pk_hint_contains", pk_hint)
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


def build_graph(
    solution: ParsedSolution,
    role: str,
    dict_ref: dict[str, str],
    attr_canon_list: Optional[list[str]] = None,
) -> TripleStore:
    """
    Build graph from ParsedSolution; fills all task data used by checks.
    dict_ref is the attribute dictionary from ref task 1.
    """
    store = TripleStore()
    U = set(dict_ref.keys())

    # Task 1: universal relation headers
    t1 = solution.tasks.get(1)
    if t1 and t1.tables:
        headers = t1.tables[0].headers
        attrs = [canon_attr_for_compare(h) for h in headers if str(h).strip()]
        if attrs:
            _add_universal_relation(store, role, attrs)
    elif attr_canon_list:
        _add_universal_relation(store, role, attr_canon_list)

    # Task 2: repeating group
    rep = task2.extract_repeating_group_ref(solution, dict_ref)
    if rep:
        _add_repeating_group(store, role, rep)

    # Task 3: 1NF table (headers + rows for get_table_1nf)
    table_1nf = task3._get_table_1nf(solution)
    if table_1nf:
        _add_table_1nf(store, role, table_1nf[0], table_1nf[1])

    # Task 4: FDs
    F = task4.extract_fds_ref(solution, dict_ref) if role == "ref" else task4.extract_fds_student(solution, dict_ref)
    if F:
        _add_fds(store, role, 4, F)

    # Task 5: PK
    pk_list = task5.extract_pk_ref(solution, dict_ref) if role == "ref" else task5.extract_pk_student(solution, dict_ref)
    if pk_list:
        _add_pk(store, role, pk_list)

    # Task 6: partial FDs — ref derived from F+PK; stu extracted from task 6
    if role == "ref" and F and pk_list:
        P_ref = task6.compute_partial_ref(U, F, pk_list)
        if P_ref:
            _add_fds(store, role, 6, P_ref)
    elif role == "stu":
        P_stu = task6.extract_partial_student(solution, dict_ref)
        if P_stu:
            _add_fds(store, role, 6, P_stu)

    # Task 8: transitive FDs — ref derived; stu extracted from task 8
    if role == "ref" and F:
        T_ref = task8.compute_transitive_ref(U, F)
        if T_ref:
            _add_fds(store, role, 8, T_ref)
    elif role == "stu":
        T_stu = task8.extract_transitive_student(solution, dict_ref)
        if T_stu:
            _add_fds(store, role, 8, T_stu)

    # Tasks 7, 9: structure only (checks use task 6/8 results)
    for tn in [7, 9]:
        if solution.tasks.get(tn):
            store.add(_task_subject(role, tn), "has_task", tn)

    # Task 10, 12: text
    for tn in [10, 12]:
        t = solution.tasks.get(tn)
        if t and t.text_lines:
            _add_text_anomaly(store, role, tn, " ".join(t.text_lines))

    # Tasks 11, 13: relations
    for task_num, module in [(11, task11), (13, task13)]:
        rels = module.extract_relations(solution, task_num, dict_ref)
        if rels:
            _add_relations(store, role, task_num, rels)

    return store
