"""Task 3: 1NF table — strict headers and multiset of rows."""
from app.core.checks.common import canon_attr_for_compare, normalize_cell_value, is_separator_row
from app.core.excel.importer import ParsedSolution
from app.core.result import TaskResult


def _get_table_1nf(parsed: ParsedSolution):
    t = parsed.tasks.get(3)
    if not t or not t.tables:
        return None
    tbl = t.tables[0]
    headers = [str(h).strip() for h in tbl.headers]
    max_col = len(headers)
    rows = []
    for row in tbl.rows:
        if is_separator_row(row, max_col):
            continue
        cells = [normalize_cell_value(row[i]) if i < len(row) else "" for i in range(max_col)]
        rows.append(cells)
    return (headers, rows)


def check(ref: ParsedSolution, stu: ParsedSolution, dict_ref: dict[str, str]) -> TaskResult:
    ref_t = _get_table_1nf(ref)
    stu_t = _get_table_1nf(stu)
    if not ref_t:
        return TaskResult(status="INSF", details={"error": "No ref 1NF table"})
    ref_h, ref_rows = ref_t
    ref_h_canon = [canon_attr_for_compare(h) for h in ref_h]
    if not stu_t:
        return TaskResult(status="FAIL", expected=ref_h_canon, actual=[], details={"error": "No student 1NF table"})
    stu_h, stu_rows = stu_t
    stu_h_canon = [canon_attr_for_compare(h.rstrip("*.")) for h in stu_h]
    if ref_h_canon != stu_h_canon:
        return TaskResult(
            status="FAIL",
            expected=ref_h_canon,
            actual=stu_h_canon,
            missing=[],
            extra=[],
            details={"reason": "header_mismatch"},
        )
    ref_multiset = [tuple(r) for r in ref_rows]
    stu_multiset = [tuple(r) for r in stu_rows]
    ref_counts: dict[tuple, int] = {}
    for r in ref_multiset:
        ref_counts[r] = ref_counts.get(r, 0) + 1
    stu_counts: dict[tuple, int] = {}
    for r in stu_multiset:
        stu_counts[r] = stu_counts.get(r, 0) + 1
    missing_rows = []
    for r, c in ref_counts.items():
        for _ in range(c - stu_counts.get(r, 0)):
            missing_rows.append(list(r))
    extra_rows = []
    for r, c in stu_counts.items():
        for _ in range(c - ref_counts.get(r, 0)):
            extra_rows.append(list(r))
    if missing_rows or extra_rows:
        return TaskResult(
            status="FAIL",
            expected=ref_h_canon,
            actual=stu_h_canon,
            missing=missing_rows[:20],
            extra=extra_rows[:20],
            details={"missing_count": len(missing_rows), "extra_count": len(extra_rows)},
        )
    # PK hint from * in headers
    pk_hint = [canon_attr_for_compare(h) for h in stu_h if h and "*" in str(h)]
    if pk_hint:
        key_cols = [ref_h_canon.index(a) for a in pk_hint if a in ref_h_canon]
        for row in stu_rows:
            if any((row[i] if i < len(row) else "").strip() == "" for i in key_cols):
                return TaskResult(status="FAIL", details={"reason": "pk_hint_empty_cell"})
        seen = set()
        for row in stu_rows:
            key = tuple(row[i] if i < len(row) else "" for i in key_cols)
            if key in seen:
                return TaskResult(status="FAIL", details={"reason": "pk_hint_duplicate", "example": list(key)})
            seen.add(key)
    return TaskResult(status="PASS", expected=ref_h_canon, actual=stu_h_canon)
