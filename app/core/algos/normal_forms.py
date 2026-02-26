"""2NF and 3NF checks for a relation."""
from app.core.algos.fd import closure
from app.core.algos.keys import candidate_keys, is_superkey


def _F_local(attrs: set[str], F: list[tuple[list[str], str]]) -> list[tuple[list[str], str]]:
    """Project F onto relation: only FDs with both sides in attrs."""
    return [(lhs, rhs) for lhs, rhs in F if set(lhs) <= attrs and rhs in attrs]


def check_2nf(
    relation_attrs: set[str],
    F_local: list[tuple[list[str], str]],
    keys_local: list[frozenset[str]],
) -> tuple[bool, list[tuple[list[str], str]]]:
    """
    Returns (ok, list of violating partial FDs).
    Partial: X -> A where X is proper subset of some key, A not in X, A non-prime.
    """
    prime = set().union(*keys_local) if keys_local else set()
    violations: list[tuple[list[str], str]] = []
    for lhs, rhs in F_local:
        if set(lhs) >= {rhs}:
            continue
        if rhs in lhs:
            continue
        for key in keys_local:
            if set(lhs) < key and rhs not in key and rhs not in prime:
                violations.append((lhs, rhs))
                break
    return (len(violations) == 0, violations)


def check_3nf(
    relation_attrs: set[str],
    F_local: list[tuple[list[str], str]],
    keys_local: list[frozenset[str]],
) -> tuple[bool, list[tuple[list[str], str]]]:
    """
    Returns (ok, list of violating FDs).
    3NF: for every non-trivial X->A, either X is superkey or A is prime.
    """
    prime = set().union(*keys_local) if keys_local else set()
    violations: list[tuple[list[str], str]] = []
    for lhs, rhs in F_local:
        if rhs in lhs:
            continue
        if is_superkey(lhs, relation_attrs, F_local):
            continue
        if rhs in prime:
            continue
        violations.append((lhs, rhs))
    return (len(violations) == 0, violations)
