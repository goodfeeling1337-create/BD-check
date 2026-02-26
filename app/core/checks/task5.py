"""Task 5: PK in 1NF — strict equality + validation (superkey, minimality, uniqueness)."""
from app.core.checks.common import extract_attrs_via_dictionary, canon_attr_for_compare
from app.core.algos.keys import is_superkey
from app.core.excel.importer import ParsedSolution
from app.core.result import TaskResult


def extract_pk_ref(parsed: ParsedSolution, dict_ref: dict[str, str]) -> list[str]:
    t = parsed.tasks.get(5)
    if not t:
        return []
    text = " ".join(t.text_lines)
    for tbl in t.tables:
        for row in tbl.rows:
            text += " " + " ".join(str(c) for c in row)
        text += " " + " ".join(tbl.headers)
    return extract_attrs_via_dictionary(text, dict_ref)


def extract_pk_student(parsed: ParsedSolution, dict_ref: dict[str, str]) -> list[str]:
    return extract_pk_ref(parsed, dict_ref)


def check(
    ref: ParsedSolution,
    stu: ParsedSolution,
    dict_ref: dict[str, str],
    F_ref: list[tuple[list[str], str]],
) -> TaskResult:
    ref_pk = extract_pk_ref(ref, dict_ref)
    stu_pk = extract_pk_student(stu, dict_ref)
    U = set(dict_ref.keys())
    ref_set = set(ref_pk)
    stu_set = set(stu_pk)
    if ref_set != stu_set:
        return TaskResult(
            status="FAIL",
            expected=ref_pk,
            actual=stu_pk,
            missing=sorted(ref_set - stu_set),
            extra=sorted(stu_set - ref_set),
        )
    if not is_superkey(stu_pk, U, F_ref):
        return TaskResult(status="FAIL", expected=ref_pk, actual=stu_pk, details={"reason": "not_superkey"})
    # Minimality: removing any attribute from PK should not be superkey
    for a in stu_pk:
        if is_superkey([x for x in stu_pk if x != a], U, F_ref):
            return TaskResult(status="FAIL", expected=ref_pk, actual=stu_pk, details={"reason": "not_minimal"})
    return TaskResult(status="PASS", expected=ref_pk, actual=stu_pk)
