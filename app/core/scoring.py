"""Scoring for task #4: ++ / +- / -+ / -- by coverage of F_ref."""
from app.core.algos.fd import closure


def score_fd_coverage(
    F_ref: list[tuple[list[str], str]],
    F_stu: list[tuple[list[str], str]],
) -> tuple[float, str]:
    """
    F_ref, F_stu: list of (lhs, rhs) single RHS.
    covered = count of X->A in F_ref such that A in closure(X, F_stu).
    Returns (score_ratio, label).
    """
    if not F_ref:
        return (0.0, "—")
    covered = 0
    for lhs, rhs in F_ref:
        if rhs in closure(lhs, F_stu):
            covered += 1
    ratio = covered / len(F_ref)
    if ratio >= 1.0:
        return (ratio, "++")
    if ratio >= 0.5:
        return (ratio, "+-")
    if ratio >= 0.25:
        return (ratio, "-+")
    return (ratio, "--")
