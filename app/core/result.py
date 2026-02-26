"""Task result and comparison types."""
from dataclasses import dataclass, field
from typing import Any, List, Optional


@dataclass
class TaskResult:
    status: str  # PASS, WARN, FAIL, INSF
    details: dict = field(default_factory=dict)
    expected: Any = None
    actual: Any = None
    missing: List[Any] = field(default_factory=list)
    extra: List[Any] = field(default_factory=list)
    explanation: str = ""
