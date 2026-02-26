"""Generate human-readable explanations for checks."""
from typing import Any


def explain_closure(X: list[str], closure_result: set[str], F: list[tuple[list[str], str]]) -> str:
    """Short explanation: X+ = {...} (which FDs were used)."""
    parts = [f"closure({', '.join(sorted(X))}) = {{ {', '.join(sorted(closure_result))} }}"]
    if F:
        parts.append("FDs used: " + "; ".join(f"{','.join(l)}→{r}" for l, r in F))
    return " ".join(parts)


def explain_missing_fd(lhs: list[str], rhs: str, closure_result: set[str]) -> str:
    """Why X->A is not implied: A not in closure(X)."""
    return f"'{','.join(lhs)}→{rhs}': {rhs} ∉ closure({{{','.join(lhs)}}}) = {{{', '.join(sorted(closure_result))}}}"


def explain_partial_fd(X: list[str], rhs: str, pk: list[str]) -> str:
    """Partial FD: X ⊂ PK, A non-prime."""
    return f"Partial: {{{', '.join(X)}}} ⊂ PK, determines {rhs}."


def explain_transitive_fd(X: list[str], rhs: str) -> str:
    """Transitive FD: A non-prime, X not superkey."""
    return f"Transitive: {{{', '.join(X)}}} → {rhs} (non-prime)."


def explain_2nf_violation(rel_name: str, partial_fd: tuple[list[str], str]) -> str:
    lhs, rhs = partial_fd
    return f"Relation {rel_name}: partial FD {{{', '.join(lhs)}}} → {rhs} violates 2NF."


def explain_3nf_violation(rel_name: str, fd: tuple[list[str], str]) -> str:
    lhs, rhs = fd
    return f"Relation {rel_name}: {{{', '.join(lhs)}}} → {rhs} violates 3NF (non-prime determined by non-key)."


def explain_coverage_missing(missing: set[str]) -> str:
    return f"Coverage: missing attributes: {{{', '.join(sorted(missing))}}}"


def explain_coverage_extra(extra: set[str]) -> str:
    return f"Coverage: extra attributes not in U: {{{', '.join(sorted(extra))}}}"
