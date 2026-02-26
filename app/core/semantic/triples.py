"""TripleStore: subject, predicate, object facts."""
from dataclasses import dataclass, field
from typing import Any, Iterator, Optional


@dataclass(frozen=True)
class Triple:
    s: str
    p: str
    o: Any  # str | bool | list (for multi-value)

    def __iter__(self) -> Iterator[Any]:
        return iter((self.s, self.p, self.o))


class TripleStore:
    """In-memory store of (s, p, o) facts."""

    def __init__(self) -> None:
        self._triples: list[Triple] = []

    def add(self, s: str, p: str, o: Any) -> None:
        self._triples.append(Triple(s=s, p=p, o=o))

    def find(
        self,
        s: Optional[str] = None,
        p: Optional[str] = None,
        o: Any = None,
    ) -> list[Triple]:
        out = []
        for t in self._triples:
            if s is not None and t.s != s:
                continue
            if p is not None and t.p != p:
                continue
            if o is not None and t.o != o:
                continue
            out.append(t)
        return out

    def find_one(self, s: Optional[str] = None, p: Optional[str] = None, o: Any = None) -> Optional[Triple]:
        lst = self.find(s=s, p=p, o=o)
        return lst[0] if lst else None

    def clear(self) -> None:
        self._triples.clear()

    def all_triples(self) -> list[Triple]:
        return list(self._triples)
