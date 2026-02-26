"""Task 4: FDs — extract, validate by dictionary, compare by closure, score ++/+-/-+/--."""
from app.core.checks.common import (
    canon_attr_for_compare,
    parse_fd_string,
    normalize_fd_arrow,
)
from app.core.algos.fd import closure, minimal_cover
from app.core.excel.importer import ParsedSolution
from app.core.result import TaskResult


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


def _to_single_rhs(fd_list: list[tuple[list[str], list[str]]]) -> list[tuple[list[str], str]]:
    result = []
    for lhs, rhs_list in fd_list:
        for r in rhs_list:
            result.append(([canon_attr_for_compare(x) for x in lhs], canon_attr_for_compare(r)))
    return result


def extract_fds_ref(parsed: ParsedSolution, dict_ref: dict[str, str]) -> list[tuple[list[str], str]]:
    raw = []
    for s in _collect_fd_strings(parsed, 4):
        raw.extend(parse_fd_string(s))
    single = []
    for lhs, rhs_list in raw:
        lhs_c = [dict_ref.get(canon_attr_for_compare(x)) for x in lhs]
        rhs_c = [dict_ref.get(canon_attr_for_compare(x)) for x in rhs_list]
        if None in lhs_c or None in rhs_c:
            continue
        for r in rhs_c:
            single.append((lhs_c, r))
    return minimal_cover(single)


def extract_fds_student(parsed: ParsedSolution, dict_ref: dict[str, str]) -> list[tuple[list[str], str]]:
    raw = []
    for s in _collect_fd_strings(parsed, 4):
        raw.extend(parse_fd_string(s))
    single = []
    for lhs, rhs_list in raw:
        lhs_c = [dict_ref.get(canon_attr_for_compare(x)) for x in lhs]
        rhs_c = [dict_ref.get(canon_attr_for_compare(x)) for x in rhs_list]
        if None in lhs_c or None in rhs_c:
            continue
        for r in rhs_c:
            single.append((lhs_c, r))
    return minimal_cover(single)


def check(
    ref: ParsedSolution,
    stu: ParsedSolution,
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
    return TaskResult(
        status=status,
        expected=F_ref,
        actual=F_stu,
        missing=missing_fds,
        extra=extra_fds,
        details={"score": score_label, "missing_count": len(missing_fds)},
    )
