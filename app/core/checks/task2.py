"""Task 2: Repeating group as set of attributes — strict set match."""
from app.core.checks.common import extract_attrs_via_dictionary_simple
from app.core.excel.importer import ParsedSolution
from app.core.result import TaskResult
from app.core.semantic.query import get_repeating_group
from app.core.semantic.triples import TripleStore


def extract_repeating_group_ref(parsed: ParsedSolution, dict_ref: dict[str, str]) -> set[str]:
    """Извлечение атрибутов повторяющейся группы по словарю (без разбиения по пробелам)."""
    t = parsed.tasks.get(2)
    if not t:
        return set()
    text = " ".join(t.text_lines)
    for tbl in t.tables:
        for row in tbl.rows:
            text += " " + " ".join(str(c) for c in row)
        text += " " + " ".join(tbl.headers)
    return set(extract_attrs_via_dictionary_simple(text, dict_ref))


def extract_repeating_group_student(parsed: ParsedSolution, dict_ref: dict[str, str]) -> set[str]:
    return extract_repeating_group_ref(parsed, dict_ref)


def check(ref_graph: TripleStore, stu_graph: TripleStore, dict_ref: dict[str, str]) -> TaskResult:
    ref_set = get_repeating_group(ref_graph, "ref")
    stu_set = get_repeating_group(stu_graph, "stu")
    missing = ref_set - stu_set
    extra = stu_set - ref_set
    if missing or extra:
        return TaskResult(
            status="FAIL",
            expected=sorted(ref_set),
            actual=sorted(stu_set),
            missing=sorted(missing),
            extra=sorted(extra),
        )
    return TaskResult(status="PASS", expected=sorted(ref_set), actual=sorted(stu_set))
