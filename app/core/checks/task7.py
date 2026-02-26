"""Task 7: Nested partial (chains) — by LHS inclusion."""
from typing import Optional

from app.core.result import TaskResult
from app.core.semantic.query import get_fds
from app.core.semantic.triples import TripleStore


def build_chains_partial(P_ref: list[tuple[list[str], str]]) -> list[list[tuple[list[str], str]]]:
    """Group by RHS A, order by LHS inclusion (larger first)."""
    by_rhs: dict[str, list[tuple[list[str], str]]] = {}
    for lhs, rhs in P_ref:
        by_rhs.setdefault(rhs, []).append((lhs, rhs))
    chains = []
    for rhs, fds in by_rhs.items():
        sorted_fds = sorted(fds, key=lambda x: -len(x[0]))
        chains.append(sorted_fds)
    return chains


def extract_chains_student(parsed, dict_ref: dict) -> list[list[tuple[list[str], str]]]:
    from app.core.checks.task6 import _collect_fd_strings
    from app.core.checks.common import parse_fd_string
    t = parsed.tasks.get(7)
    if not t:
        return []
    P_stu = []
    for s in _collect_fd_strings(parsed, 7):
        for lhs, rhs_list in parse_fd_string(s, dictionary=dict_ref):
            for r in rhs_list:
                P_stu.append((lhs, r))
    return build_chains_partial(P_stu)


def check(
    ref_graph: TripleStore,
    stu_graph: TripleStore,
    dict_ref: dict[str, str],
    P_ref: Optional[list[tuple[list[str], str]]],
    strict_nested_order: bool = False,
) -> TaskResult:
    if not P_ref:
        return TaskResult(status="PASS", expected=[], actual=[])
    expected_chains = build_chains_partial(P_ref)
    P_stu = get_fds(stu_graph, "stu", 6) or []
    actual_chains = build_chains_partial(P_stu)
    ref_fd_set = set((tuple(sorted(l)), r) for l, r in P_ref)
    stu_fd_set = set()
    for chain in actual_chains:
        for l, r in chain:
            stu_fd_set.add((tuple(sorted(l)), r))
    if ref_fd_set != stu_fd_set:
        return TaskResult(status="FAIL", expected=expected_chains, actual=actual_chains, details={"reason": "set_mismatch"})
    if strict_nested_order:
        if expected_chains != actual_chains:
            return TaskResult(status="FAIL", expected=expected_chains, actual=actual_chains, details={"reason": "order"})
    return TaskResult(status="PASS", expected=expected_chains, actual=actual_chains, details={"order_warn": True})
