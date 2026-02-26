"""Task 13: 3NF schemas — coverage, 3NF, lossless, dep-pres."""
import re
from app.core.checks.common import canon_attr_for_compare
from app.core.algos.keys import candidate_keys
from app.core.algos.normal_forms import check_3nf
from app.core.algos.decomposition import coverage_check, lossless_join_basic, dependency_preservation_approx
from app.core.excel.importer import ParsedSolution
from app.core.result import TaskResult


def _F_local(attrs: set[str], F: list[tuple[list[str], str]]) -> list[tuple[list[str], str]]:
    return [(lhs, rhs) for lhs, rhs in F if set(lhs) <= attrs and rhs in attrs]


def extract_relations(parsed: ParsedSolution, task_num: int, dict_ref: dict[str, str]) -> list[tuple[str, set[str]]]:
    t = parsed.tasks.get(task_num)
    if not t:
        return []
    relations = []
    for tbl in t.tables:
        for row in tbl.rows:
            if not row:
                continue
            name = str(row[0]).strip() if row else "R"
            attrs = set()
            for cell in row[1:]:
                c = dict_ref.get(canon_attr_for_compare(str(cell).strip()))
                if c:
                    attrs.add(c)
            if name or attrs:
                relations.append((name or "R", attrs))
        if not tbl.rows and tbl.headers:
            name = str(tbl.headers[0]).strip() or "R"
            attrs = set()
            for h in tbl.headers[1:]:
                c = dict_ref.get(canon_attr_for_compare(str(h).strip()))
                if c:
                    attrs.add(c)
            if name or attrs:
                relations.append((name, attrs))
    for line in t.text_lines:
        m = re.search(r"(\w+)\s*\(\s*([^)]+)\)", line)
        if m:
            name, attrs_str = m.group(1), m.group(2)
            attrs = set()
            for a in re.split(r"[\s,;]+", attrs_str):
                c = dict_ref.get(canon_attr_for_compare(a.strip()))
                if c:
                    attrs.add(c)
            if attrs:
                relations.append((name, attrs))
    return relations


def check(
    ref: ParsedSolution,
    stu: ParsedSolution,
    dict_ref: dict[str, str],
    F_ref: list[tuple[list[str], str]],
) -> TaskResult:
    U = set(dict_ref.keys())
    relations = extract_relations(stu, 13, dict_ref)
    ok_cov, missing, extra = coverage_check(U, relations)
    if not ok_cov:
        return TaskResult(
            status="FAIL",
            details={"coverage": False, "missing": list(missing), "extra": list(extra)},
            missing=list(missing),
            extra=list(extra),
        )
    for name, attrs in relations:
        F_local = _F_local(attrs, F_ref)
        keys = candidate_keys(attrs, F_local) if F_local else []
        nf_ok, violations = check_3nf(attrs, F_local, keys)
        if not nf_ok:
            return TaskResult(status="FAIL", details={"relation": name, "violations": violations})
    lossless = lossless_join_basic(U, F_ref, relations)
    dep_pres = dependency_preservation_approx(F_ref, relations)
    details = {"coverage": True, "lossless": lossless, "dep_pres": dep_pres}
    if not lossless:
        details["lossless_warn"] = True
    if not dep_pres:
        details["dep_pres_warn"] = True
    return TaskResult(status="PASS", actual=relations, details=details)
