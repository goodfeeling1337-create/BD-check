"""Task 1: Universal relation headers — strict match."""
from app.core.checks.common import canon_attr_for_compare
from app.core.excel.importer import ParsedSolution
from app.core.result import TaskResult


def extract_headers_ref(parsed: ParsedSolution) -> list[str]:
    """Extract header row of universal relation from task 1."""
    t = parsed.tasks.get(1)
    if not t or not t.tables:
        return []
    return [str(h).strip() for h in t.tables[0].headers if str(h).strip()]


def extract_headers_student(parsed: ParsedSolution) -> list[str]:
    """Extract header row from student task 1."""
    return extract_headers_ref(parsed)


def check(
    ref: ParsedSolution,
    stu: ParsedSolution,
    dict_ref: dict[str, str],
    strict_order: bool = False,
) -> TaskResult:
    ref_headers = extract_headers_ref(ref)
    stu_headers = extract_headers_student(stu)
    ref_canon = [canon_attr_for_compare(h) for h in ref_headers]
    stu_canon = [canon_attr_for_compare(h) for h in stu_headers]
    ref_set = set(ref_canon)
    stu_set = set(stu_canon)
    missing = ref_set - stu_set
    extra = stu_set - ref_set
    if missing or extra:
        return TaskResult(
            status="FAIL",
            expected=ref_canon,
            actual=stu_canon,
            missing=sorted(missing),
            extra=sorted(extra),
            details={"missing": list(missing), "extra": list(extra)},
        )
    if strict_order and ref_canon != stu_canon:
        return TaskResult(
            status="FAIL",
            expected=ref_canon,
            actual=stu_canon,
            details={"reason": "order_mismatch"},
        )
    if ref_canon != stu_canon:
        return TaskResult(
            status="WARN",
            expected=ref_canon,
            actual=stu_canon,
            details={"reason": "order differs"},
        )
    return TaskResult(status="PASS", expected=ref_canon, actual=stu_canon)
