"""Task 8: Transitive FDs — strict set match."""
from app.core.algos.keys import candidate_keys, is_superkey
from app.core.checks.common import canon_attr_for_compare, parse_fd_string, normalize_fd_arrow
from app.core.excel.importer import ParsedSolution
from app.core.result import TaskResult


def compute_transitive_ref(
    U_attrs: set[str],
    F_ref: list[tuple[list[str], str]],
) -> list[tuple[list[str], str]]:
    keys = candidate_keys(U_attrs, F_ref)
    prime = set().union(*keys)
    transitive = []
    for lhs, rhs in F_ref:
        if rhs in lhs:
            continue
        if rhs in prime:
            continue
        if is_superkey(lhs, U_attrs, F_ref):
            continue
        transitive.append((lhs, rhs))
    return transitive


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


def extract_transitive_student(parsed: ParsedSolution, dict_ref: dict[str, str]) -> list[tuple[list[str], str]]:
    out = []
    for s in _collect_fd_strings(parsed, 8):
        for lhs, rhs_list in parse_fd_string(s):
            lhs_c = [dict_ref.get(canon_attr_for_compare(x)) for x in lhs]
            for r in rhs_list:
                r_c = dict_ref.get(canon_attr_for_compare(r))
                if None not in lhs_c and r_c:
                    out.append((lhs_c, r_c))
    return out


def check(
    ref: ParsedSolution,
    stu: ParsedSolution,
    dict_ref: dict[str, str],
    F_ref: list[tuple[list[str], str]],
) -> TaskResult:
    U = set(dict_ref.keys())
    T_ref = compute_transitive_ref(U, F_ref)
    T_stu = extract_transitive_student(stu, dict_ref)
    ref_set = set((tuple(sorted(l)), r) for l, r in T_ref)
    stu_set = set((tuple(sorted(l)), r) for l, r in T_stu)
    if ref_set != stu_set:
        return TaskResult(
            status="FAIL",
            expected=T_ref,
            actual=T_stu,
            missing=[x for x in T_ref if (tuple(sorted(x[0])), x[1]) not in stu_set],
            extra=[x for x in T_stu if (tuple(sorted(x[0])), x[1]) not in ref_set],
        )
    return TaskResult(status="PASS", expected=T_ref, actual=T_stu)
