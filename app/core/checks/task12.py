"""Task 12: Anomalies 2NF — rubric + attachment to partial FD."""
from typing import Optional

from app.core.result import TaskResult
from app.core.semantic.query import get_text
from app.core.semantic.rubric import classify_anomaly_types, mentions_partial_fd
from app.core.semantic.triples import TripleStore


def check(
    ref_graph: TripleStore,
    stu_graph: TripleStore,
    dict_ref: dict[str, str],
    P_ref: Optional[list[tuple[list[str], str]]],
) -> TaskResult:
    text = get_text(stu_graph, "stu", 12)
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
