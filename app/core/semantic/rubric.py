"""Classify anomaly types (insert/update/delete) in text."""
import re
from typing import Literal, Optional

AnomalyType = Literal["insert", "update", "delete"]

INSERT_PATTERNS = [
    r"вставк", r"insert", r"добавл", r"добавить", r"новую запись", r"новой записи",
    r"дублир", r"повтор.*данн", r"нельзя вставить", r"невозможно вставить",
]
UPDATE_PATTERNS = [
    r"обновл", r"update", r"изменен", r"изменить", r"многократн.*изменен", r"частичн.*изменен",
    r"несогласован", r"противоречи", r"аномали.*обновл",
]
DELETE_PATTERNS = [
    r"удален", r"delete", r"удалить", r"потеря.*данн", r"потеря информац",
    r"каскадн.*удален", r"аномали.*удален",
]


def _match_any(text: str, patterns: list[str]) -> bool:
    t = text.lower()
    for p in patterns:
        if re.search(p, t, re.IGNORECASE):
            return True
    return False


def classify_anomaly_types(text: str) -> set[AnomalyType]:
    """Return set of anomaly types mentioned in text."""
    found: set[AnomalyType] = set()
    if _match_any(text, INSERT_PATTERNS):
        found.add("insert")
    if _match_any(text, UPDATE_PATTERNS):
        found.add("update")
    if _match_any(text, DELETE_PATTERNS):
        found.add("delete")
    return found


def has_variant_attachment(text: str, repeating_group_attrs: list[str]) -> bool:
    """
    True if text mentions at least one attr from repeating group or describes
    "list in one cell / repeating columns".
    """
    t = text.lower()
    for a in repeating_group_attrs:
        if a and a.lower() in t:
            return True
    if re.search(r"список\s+в\s+одной\s+ячейк", t) or re.search(r"повторяющ", t):
        return True
    if re.search(r"частичн.*зависим", t) or re.search(r"часть\s+ключ", t):
        return True
    return False


def mentions_partial_fd(text: str, partial_attrs: Optional[list[str]] = None) -> bool:
    """True if text mentions partial FD or attributes from partial."""
    t = text.lower()
    if re.search(r"частичн.*зависим", t) or re.search(r"часть\s+составного\s+ключ", t):
        return True
    if partial_attrs:
        for a in partial_attrs:
            if a and a.lower() in t:
                return True
    return False
