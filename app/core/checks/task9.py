"""Task 9: Nested transitive chains."""
from typing import Optional
from app.core.checks.task8 import compute_transitive_ref
from app.core.checks.common import canon_attr_for_compare, parse_fd_string, normalize_fd_arrow
from app.core.excel.importer import ParsedSolution
from app.core.result import TaskResult


def build_chains_transitive(T_ref: list[tuple[list[str], str]]) -> list[list[tuple[list[str], str]]]:
    """By RHS, order by LHS inclusion (larger first)."""
    by_rhs: dict[str, list[tuple[list[str], str]]] = {}
    for lhs, rhs in T_ref:
        by_rhs.setdefault(rhs, []).append((lhs, rhs))
    return [sorted(fds, key=lambda x: -len(x[0])) for fds in by_rhs.values()]


def _collect_fd_strings(parsed: ParsedSolution, task_num: int) -> list[str]:
    out = []
    t = parsed.tasks.get(task_num)
    if not t:
        return out
    for line in t.text_lines:
        if "->" in normalize_fd_arrow(line):
            out.append(normalize_fd_arrow(line))
    for tbl in t.tables:
        for row in tbl.rows:
            if len(row) >= 2:
                out.append(normalize_fd_arrow(str(row[0]) + "->" + str(row[1])))
    return out


def extract_chains_student(parsed: ParsedSolution, dict_ref: dict[str, str]) -> list[list[tuple[list[str], str]]]:
    out = []
    for s in _collect_fd_strings(parsed, 9):
        for lhs, rhs_list in parse_fd_string(s):
            lhs_c = [dict_ref.get(canon_attr_for_compare(x)) for x in lhs]
            for r in rhs_list:
                r_c = dict_ref.get(canon_attr_for_compare(r))
                if None not in lhs_c and r_c:
                    out.append((lhs_c, r_c))
    return build_chains_transitive(out)


def check(
    ref: ParsedSolution,
    stu: ParsedSolution,
    dict_ref: dict[str, str],
    F_ref: list[tuple[list[str], str]],
    T_ref: Optional[list[tuple[list[str], str]]],
) -> TaskResult:
    if not T_ref:
        return TaskResult(status="PASS", expected=[], actual=[])
    U = set(dict_ref.keys())
    if T_ref is None:
        T_ref = compute_transitive_ref(U, F_ref)
    expected_chains = build_chains_transitive(T_ref)
    actual_chains = extract_chains_student(stu, dict_ref)
    ref_fd_set = set((tuple(sorted(l)), r) for l, r in T_ref)
    stu_fd_set = set()
    for chain in actual_chains:
        for l, r in chain:
            stu_fd_set.add((tuple(sorted(l)), r))
    if ref_fd_set != stu_fd_set:
        return TaskResult(status="FAIL", expected=expected_chains, actual=actual_chains)
    return TaskResult(status="PASS", expected=expected_chains, actual=actual_chains, details={"order_warn": True})
