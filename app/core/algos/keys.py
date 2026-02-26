"""Candidate keys and superkey check."""
from app.core.algos.fd import closure


def is_superkey(X: list[str], R: set[str], F: list[tuple[list[str], str]]) -> bool:
    """True if X+ covers all attributes in R."""
    return closure(X, F) >= R


def candidate_keys(R: set[str], F: list[tuple[list[str], str]]) -> list[frozenset[str]]:
    """
    Find candidate keys. Mandatory part = attributes not in any RHS.
    Then search with DFS/BFS with pruning.
    """
    rhs_attrs = set()
    for lhs, rhs in F:
        rhs_attrs.add(rhs)
    mandatory = R - rhs_attrs
    optional = R & rhs_attrs
    if not optional:
        return [frozenset(mandatory)] if mandatory else [frozenset()]
    # Enumerate subsets of optional and check if mandatory ∪ subset is a key
    keys: list[frozenset[str]] = []
    opt_list = sorted(optional)

    def search(idx: int, current: set[str]) -> None:
        if is_superkey(list(current), R, F):
            # Check minimality: no proper subset of current is key
            cur_f = frozenset(current)
            for k in keys:
                if k < cur_f:
                    return  # not minimal
            keys[:] = [k for k in keys if not (cur_f < k)]
            keys.append(cur_f)
            return
        if idx >= len(opt_list):
            return
        # try without opt_list[idx]
        search(idx + 1, current)
        # try with opt_list[idx]
        search(idx + 1, current | {opt_list[idx]})

    search(0, set(mandatory))
    return keys


def prime_attributes(R: set[str], F: list[tuple[list[str], str]]) -> set[str]:
    """Attributes that appear in at least one candidate key."""
    keys = candidate_keys(R, F)
    return set().union(*keys)
