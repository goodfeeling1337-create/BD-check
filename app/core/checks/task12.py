"""Task 12: Anomalies 2NF — rubric + attachment to partial FD."""
from typing import Optional
from app.core.semantic.rubric import classify_anomaly_types, mentions_partial_fd
from app.core.excel.importer import ParsedSolution
from app.core.result import TaskResult


def check(
    ref: ParsedSolution,
    stu: ParsedSolution,
    dict_ref: dict[str, str],
    P_ref: Optional[list[tuple[list[str], str]]],
) -> TaskResult:
    t = stu.tasks.get(12)
    text = " ".join(t.text_lines) if t and t.text_lines else ""
    if not text.strip():
        return TaskResult(status="FAIL", details={"reason": "empty"})
    types = classify_anomaly_types(text)
    partial_attrs = []
    if P_ref:
        for lhs, rhs in P_ref:
            partial_attrs.extend(lhs)
            partial_attrs.append(rhs)
    attach = mentions_partial_fd(text, partial_attrs)
    if len(types) >= 2 and attach:
        return TaskResult(status="PASS", actual=list(types), details={"types": list(types)})
    if text.strip():
        return TaskResult(status="WARN", actual=list(types), details={"types": list(types), "attach": attach})
    return TaskResult(status="FAIL", details={"reason": "off_topic"})
