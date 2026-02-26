"""Candidate keys and superkey check. Uses closure cache for performance."""
from app.core.algos.fd import closure
from app.core.settings import KEYS_MAX_OPTIONAL


def _closure_cached(
    X: list[str],
    F: list[tuple[list[str], str]],
    cache: dict[frozenset[str], set[str]],
) -> set[str]:
    """Closure with cache to avoid repeated work during key search."""
    key = frozenset(X)
    if key in cache:
        return cache[key]
    result = closure(X, F)
    cache[key] = result
    return result


def is_superkey(X: list[str], R: set[str], F: list[tuple[list[str], str]]) -> bool:
    """True if X+ covers all attributes in R."""
    return closure(X, F) >= R


def candidate_keys(
    R: set[str],
    F: list[tuple[list[str], str]],
    max_optional: int = KEYS_MAX_OPTIONAL,
) -> list[frozenset[str]]:
    """
    Поиск кандидатных ключей. Обязательная часть = атрибуты не из RHS.
    Перебор подмножеств optional с отсечением по уже найденным ключам.
    max_optional: ограничение размера optional для перебора (защита от взрыва при 30+ атрибутах).
    """
    rhs_attrs = set()
    for lhs, rhs in F:
        rhs_attrs.add(rhs)
    mandatory = R - rhs_attrs
    optional = R & rhs_attrs
    if not optional:
        return [frozenset(mandatory)] if mandatory else [frozenset()]
    opt_list = sorted(optional)
    if len(opt_list) > max_optional:
        opt_list = opt_list[:max_optional]
    keys: list[frozenset[str]] = []
    _closure_cache: dict[frozenset[str], set[str]] = {}

    def _is_superkey_cached(current: set[str]) -> bool:
        return _closure_cached(list(current), F, _closure_cache) >= R

    def search(idx: int, current: set[str]) -> None:
        if _is_superkey_cached(current):
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
