"""Closure and minimal cover for FDs."""
from typing import Iterable


def closure(X: Iterable[str], F: list[tuple[list[str], str]]) -> set[str]:
    """
    Compute closure X+ under F.
    F: list of (lhs_list, rhs) where rhs is single attribute.
    """
    Xset = set(X)
    result = set(Xset)
    F_single = [(list(lhs), r) for lhs, r in F]
    changed = True
    while changed:
        changed = False
        for lhs, rhs in F_single:
            if rhs in result:
                continue
            if set(lhs) <= result:
                result.add(rhs)
                changed = True
    return result


def _single_rhs(F: list[tuple[list[str], str]]) -> list[tuple[list[str], str]]:
    """Split RHS so each FD has single attribute on RHS."""
    out = []
    for lhs, rhs in F:
        for a in rhs if isinstance(rhs, (list, tuple)) else [rhs]:
            out.append((list(lhs), a if isinstance(a, str) else str(a)))
    return out


def _minimize_lhs(lhs: list[str], rhs: str, F: list[tuple[list[str], str]]) -> list[str]:
    """Minimize LHS: remove A from LHS if (LHS\\{A})+ contains rhs under F."""
    current = list(lhs)
    for a in list(current):
        without = [x for x in current if x != a]
        if not without:
            continue
        if rhs in closure(without, F):
            current = without
    return current


def minimal_cover(F: list[tuple[list[str], str]]) -> list[tuple[list[str], str]]:
    """
    Compute minimal cover: RHS single attr, no redundant LHS attributes, no redundant FDs.
    """
    G = _single_rhs(F)
    # Minimize LHS for each FD
    G = [(_minimize_lhs(lhs, rhs, G), rhs) for lhs, rhs in G]
    G = [(sorted(lhs), rhs) for lhs, rhs in G]
    # Remove redundant FDs: FD is redundant if closure without it still gives same result
    result = []
    for i, (lhs, rhs) in enumerate(G):
        rest = [g for j, g in enumerate(G) if j != i]
        if rhs not in closure(lhs, rest):
            result.append((lhs, rhs))
    return result
