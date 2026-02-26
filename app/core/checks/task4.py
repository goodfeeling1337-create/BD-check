"""Task 4: FDs — извлечение по словарю, сравнение по выводимости, оценка ++/+-/-+/--."""
from typing import TYPE_CHECKING

from app.core.checks.common import normalize_fd_arrow, parse_fd_string
from app.core.algos.fd import closure, minimal_cover
from app.core.excel.importer import ParsedSolution
from app.core.result import TaskResult
from app.core.semantic.explain import explain_missing_fd

if TYPE_CHECKING:
    from app.core.semantic.triples import TripleStore


def _collect_fd_strings(parsed: ParsedSolution, task_num: int) -> list[str]:
    out = []
    t = parsed.tasks.get(task_num)
    if not t:
        return out
    for line in t.text_lines:
        line = normalize_fd_arrow(line)
        if "->" in line:
            out.append(line)
    for tbl in t.tables:
        for row in tbl.rows:
            if len(row) >= 2:
                out.append(normalize_fd_arrow(str(row[0]) + "->" + str(row[1])))
        for h in tbl.headers:
            if "->" in str(h):
                out.append(normalize_fd_arrow(str(h)))
    return out


def extract_fds_ref(parsed: ParsedSolution, dict_ref: dict[str, str]) -> list[tuple[list[str], str]]:
    """Извлечение ФЗ эталона; только атрибуты из словаря #1."""
    raw = []
    for s in _collect_fd_strings(parsed, 4):
        raw.extend(parse_fd_string(s, dictionary=dict_ref))
    single = []
    for lhs, rhs_list in raw:
        for r in rhs_list:
            single.append((lhs, r))
    return minimal_cover(single)


def extract_fds_student(parsed: ParsedSolution, dict_ref: dict[str, str]) -> list[tuple[list[str], str]]:
    """Извлечение ФЗ студента; только атрибуты из словаря #1."""
    raw = []
    for s in _collect_fd_strings(parsed, 4):
        raw.extend(parse_fd_string(s, dictionary=dict_ref))
    single = []
    for lhs, rhs_list in raw:
        for r in rhs_list:
            single.append((lhs, r))
    return minimal_cover(single)


def check(
    ref_graph: "TripleStore",
    stu_graph: "TripleStore",
    dict_ref: dict[str, str],
    F_ref: list[tuple[list[str], str]],
    F_stu: list[tuple[list[str], str]],
    score_label: str,
) -> TaskResult:
    missing_fds = []
    for lhs, rhs in F_ref:
        if rhs not in closure(lhs, F_stu):
            missing_fds.append((lhs, rhs))
    extra_fds = []
    for lhs, rhs in F_stu:
        if rhs not in closure(lhs, F_ref):
            extra_fds.append((lhs, rhs))
    status = "PASS" if not missing_fds else "FAIL"
    explanation = ""
    if missing_fds:
        lhs, rhs = missing_fds[0]
        cl = closure(lhs, F_stu)
        explanation = explain_missing_fd(lhs, rhs, cl)
    return TaskResult(
        status=status,
        expected=F_ref,
        actual=F_stu,
        missing=missing_fds,
        extra=extra_fds,
        details={"score": score_label, "missing_count": len(missing_fds)},
        explanation=explanation,
    )
