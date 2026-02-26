"""Compare ref vs student: fingerprint, run all checks, diff."""
import hashlib
from pathlib import Path
from typing import Any, Union

from app.core.excel.importer import parse_workbook, ParsedSolution
from app.core.checks.common import canon_attr_for_compare
from app.core.result import TaskResult
from app.core.checks import task1, task2, task3, task4, task5, task6, task7, task8, task9, task10, task11, task12, task13
from app.core.scoring import score_fd_coverage


def fingerprint(attrs_canon: list[str]) -> str:
    """SHA256 of sorted canonical attributes (task 1 ref)."""
    return hashlib.sha256("|".join(sorted(attrs_canon)).encode()).hexdigest()


def run_checks(
    ref: ParsedSolution,
    stu: ParsedSolution,
    strict_order_task1: bool = False,
    strict_nested_order: bool = False,
) -> tuple[dict[int, TaskResult], str, str]:
    """
    Run all task checks. Returns (task_results, score_4_label, fingerprint_warn).
    """
    results: dict[int, TaskResult] = {}
    # Build attribute dictionary from ref task 1
    ref_attrs = task1.extract_headers_ref(ref)
    if not ref_attrs:
        for i in range(1, 14):
            results[i] = TaskResult(status="FAIL", details={"error": "No ref task 1 headers"})
        return results, "--", "No reference attributes"
    dict_ref = {canon_attr_for_compare(a): canon_attr_for_compare(a) for a in ref_attrs}
    U_attrs = set(dict_ref.keys())
    fp_ref = fingerprint(list(U_attrs))
    stu_attrs_t1 = task1.extract_headers_student(stu)
    fp_stu = fingerprint([canon_attr_for_compare(a) for a in stu_attrs_t1]) if stu_attrs_t1 else ""
    fingerprint_ok = fp_ref == fp_stu
    fingerprint_warn = "" if fingerprint_ok else "Fingerprint mismatch: possibly different variant or wrong file."

    # Task 1
    results[1] = task1.check(ref, stu, dict_ref, strict_order=strict_order_task1)

    # Task 2
    results[2] = task2.check(ref, stu, dict_ref)

    # Task 3
    results[3] = task3.check(ref, stu, dict_ref)

    # Task 4: F_ref, F_stu, scoring
    F_ref = task4.extract_fds_ref(ref, dict_ref)
    F_stu = task4.extract_fds_student(stu, dict_ref)
    score_ratio, score_4_label = score_fd_coverage(F_ref, F_stu)
    results[4] = task4.check(ref, stu, dict_ref, F_ref, F_stu, score_4_label)

    # Task 5
    results[5] = task5.check(ref, stu, dict_ref, F_ref)

    # Task 6: partial FDs (PK_ref from ref)
    results[6] = task6.check(ref, stu, dict_ref, F_ref, results[5].expected)

    # Task 7: nested partial chains
    results[7] = task7.check(ref, stu, dict_ref, results[6].expected)

    # Task 8: transitive
    results[8] = task8.check(ref, stu, dict_ref, F_ref)

    # Task 9: nested transitive
    results[9] = task9.check(ref, stu, dict_ref, F_ref, results[8].expected)

    # Task 10: anomalies 1NF
    results[10] = task10.check(ref, stu, dict_ref, results[2].expected)

    # Task 11: 2NF schemas
    results[11] = task11.check(ref, stu, dict_ref, F_ref, results[6].expected)

    # Task 12: anomalies 2NF
    results[12] = task12.check(ref, stu, dict_ref, results[6].expected)

    # Task 13: 3NF schemas
    results[13] = task13.check(ref, stu, dict_ref, F_ref)

    return results, score_4_label, fingerprint_warn


def compare(ref_path: Union[str, Path], stu_path: Union[str, Path], **kwargs: Any) -> dict[str, Any]:
    """
    Load both files, run checks, return full result dict for UI/report.
    """
    ref = parse_workbook(ref_path)
    stu = parse_workbook(stu_path)
    results, score_4, fp_warn = run_checks(ref, stu, **kwargs)
    ref_attrs = task1.extract_headers_ref(ref)
    fp_ref = fingerprint([canon_attr_for_compare(a) for a in ref_attrs]) if ref_attrs else ""
    stu_attrs = task1.extract_headers_student(stu)
    fp_stu = fingerprint([canon_attr_for_compare(a) for a in stu_attrs]) if stu_attrs else ""
    return {
        "ref_path": str(ref_path),
        "stu_path": str(stu_path),
        "fingerprint_ref": fp_ref,
        "fingerprint_stu": fp_stu,
        "fingerprint_match": fp_ref == fp_stu,
        "fingerprint_warn": fp_warn,
        "score_4": score_4,
        "task_results": results,
        "ref_parsed": ref,
        "stu_parsed": stu,
    }
