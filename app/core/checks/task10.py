"""Task 10: Anomalies 1NF — rubric (insert/update/delete) + variant attachment."""
from typing import Optional
from app.core.semantic.rubric import classify_anomaly_types, has_variant_attachment
from app.core.excel.importer import ParsedSolution
from app.core.result import TaskResult


def check(
    ref: ParsedSolution,
    stu: ParsedSolution,
    dict_ref: dict[str, str],
    repeating_group_attrs: Optional[list[str]],
) -> TaskResult:
    t = stu.tasks.get(10)
    text = " ".join(t.text_lines) if t and t.text_lines else ""
    if not text.strip():
        return TaskResult(status="FAIL", details={"reason": "empty"})
    types = classify_anomaly_types(text)
    attach = has_variant_attachment(text, repeating_group_attrs or [])
    if len(types) >= 2 and attach:
        return TaskResult(status="PASS", actual=list(types), details={"types": list(types)})
    if text.strip() and (len(types) < 2 or not attach):
        return TaskResult(status="WARN", actual=list(types), details={"types": list(types), "attach": attach})
    return TaskResult(status="FAIL", details={"reason": "off_topic", "types": list(types)})
