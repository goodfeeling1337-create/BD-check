"""Task 6: Partial FDs — X ⊂ PK, A non-prime, coverage 100%."""
from typing import Optional

from app.core.algos.fd import closure
from app.core.algos.keys import candidate_keys
from app.core.checks.common import parse_fd_string, normalize_fd_arrow
from app.core.excel.importer import ParsedSolution
from app.core.result import TaskResult
from app.core.semantic.query import get_fds
from app.core.semantic.triples import TripleStore


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


def compute_partial_ref(
    U_attrs: set[str],
    F_ref: list[tuple[list[str], str]],
    PK_ref: list[str],
) -> list[tuple[list[str], str]]:
    keys = candidate_keys(U_attrs, F_ref)
    prime = set().union(*keys)
    pk_set = set(PK_ref)
    partial = []
    for lhs, rhs in F_ref:
        if set(lhs) < pk_set and rhs not in prime and rhs not in lhs:
            partial.append((lhs, rhs))
    return partial


def extract_partial_student(parsed: ParsedSolution, dict_ref: dict[str, str]) -> list[tuple[list[str], str]]:
    out = []
    for s in _collect_fd_strings(parsed, 6):
        for lhs, rhs_list in parse_fd_string(s, dictionary=dict_ref):
            for r in rhs_list:
                out.append((lhs, r))
    return out


def check(
    ref_graph: TripleStore,
    stu_graph: TripleStore,
    dict_ref: dict[str, str],
    F_ref: list[tuple[list[str], str]],
    PK_ref: Optional[list[str]],
) -> TaskResult:
    if not PK_ref:
        return TaskResult(status="INSF", details={"error": "No PK"})
    U = set(dict_ref.keys())
    P_ref = get_fds(ref_graph, "ref", 6) or compute_partial_ref(U, F_ref, PK_ref)
    P_stu = get_fds(stu_graph, "stu", 6)
    missing = []
    for lhs, rhs in P_ref:
        if rhs not in closure(lhs, P_stu):
            missing.append((lhs, rhs))
    prime = set().union(*candidate_keys(U, F_ref))
    pk_set = set(PK_ref)
    extra = []
    for lhs, rhs in P_stu:
        if (tuple(sorted(lhs)), rhs) in set((tuple(sorted(l)), r) for l, r in P_ref):
            continue
        if set(lhs) < pk_set and rhs not in prime:
            continue  # could be equivalent
        extra.append((lhs, rhs))
    if missing:
        return TaskResult(status="FAIL", expected=P_ref, actual=P_stu, missing=missing, extra=extra)
    return TaskResult(status="PASS", expected=P_ref, actual=P_stu, extra=extra, details={"extra_partial": extra})
