"""Unit tests for task #4 scoring ++/+-/-+/--."""
import pytest
from app.core.scoring import score_fd_coverage


def test_score_full():
    F_ref = [(["A"], "B"), (["B"], "C")]
    F_stu = [(["A"], "B"), (["B"], "C")]
    ratio, label = score_fd_coverage(F_ref, F_stu)
    assert ratio == 1.0
    assert label == "++"


def test_score_half():
    F_ref = [(["A"], "B"), (["B"], "C")]
    F_stu = [(["A"], "B")]
    ratio, label = score_fd_coverage(F_ref, F_stu)
    assert ratio == 0.5
    assert label == "+-"


def test_score_quarter():
    F_ref = [(["A"], "B"), (["B"], "C"), (["A"], "C"), (["C"], "D")]
    F_stu = [(["A"], "B")]
    ratio, label = score_fd_coverage(F_ref, F_stu)
    assert ratio >= 0.25
    assert label in ("+-", "-+")


def test_score_low():
    F_ref = [(["A"], "B"), (["B"], "C"), (["C"], "D"), (["D"], "E")]
    F_stu = []
    ratio, label = score_fd_coverage(F_ref, F_stu)
    assert ratio == 0.0
    assert label == "--"
