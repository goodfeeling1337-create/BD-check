"""Decomposition: coverage, lossless join, dependency preservation."""
from app.core.algos.fd import minimal_cover
from app.core.algos.keys import candidate_keys, is_superkey


def coverage_check(U_attrs: set[str], relations: list[tuple[str, set[str]]]) -> tuple[bool, set[str], set[str]]:
    """
    relations: list of (name, set(attrs)).
    Returns (ok, missing_from_U, extra_not_in_U).
    ok if union(attrs) == U_attrs.
    """
    union = set()
    for _, attrs in relations:
        union |= attrs
    missing = U_attrs - union
    extra = union - U_attrs
    return (len(missing) == 0 and len(extra) == 0, missing, extra)


def lossless_join_basic(
    U_attrs: set[str],
    F: list[tuple[list[str], str]],
    relations: list[tuple[str, set[str]]],
) -> bool:
    """
    PASS if some relation contains a candidate key of (U_attrs, F).
    """
    keys = candidate_keys(U_attrs, F)
    for _, attrs in relations:
        for k in keys:
            if k <= attrs:
                return True
    return False


def dependency_preservation_approx(
    F: list[tuple[list[str], str]],
    relations: list[tuple[str, set[str]]],
) -> bool:
    """
    True if every FD in minimal_cover(F) is entirely contained in some relation's attrs.
    """
    G = minimal_cover(F)
    for lhs, rhs in G:
        fd_attrs = set(lhs) | {rhs}
        found = False
        for _, attrs in relations:
            if fd_attrs <= attrs:
                found = True
                break
        if not found:
            return False
    return True
