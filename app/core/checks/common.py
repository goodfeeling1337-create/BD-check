"""Канонизация атрибутов и извлечение по словарю (без разбиения по пробелам)."""
import re
from datetime import datetime, timedelta
from typing import Any, Optional, Union

NBSP = "\u00a0"
SEPARATOR_ROW_RE = re.compile(r"^[\s.\-…]*$")


def canon_attr(
    raw: str,
    normalize_yo: bool = True,
    strip_trailing_markers: bool = True,
) -> str:
    """
    Одна каноническая форма для имён атрибутов:
    trim, collapse spaces, casefold, NBSP -> space,
    опционально ё->е, убрать хвостовые '*' и '.'.
    """
    if not raw:
        return ""
    s = str(raw).replace(NBSP, " ").strip()
    s = re.sub(r"\s+", " ", s)
    s = s.casefold()
    if normalize_yo:
        s = s.replace("ё", "е")
    if strip_trailing_markers:
        s = s.rstrip("*.").strip()
    return s


def canon_attr_for_compare(raw: str) -> str:
    """Канон для сравнения (label для отображения хранить отдельно)."""
    return canon_attr(raw, normalize_yo=True, strip_trailing_markers=True)


def build_attribute_dictionary(ref_attrs_canon: list[str]) -> dict[str, str]:
    """Словарь: canon -> canon (для проверки «из эталона»)."""
    return {c: c for c in ref_attrs_canon}


def build_label_canon_pairs(ref_headers: list[str]) -> list[tuple[str, str]]:
    """
    Список (label, canon) для атрибутов из задания №1 эталона.
    Сортировка по убыванию длины canon — для извлечения longest-first.
    """
    pairs: list[tuple[str, str]] = []
    seen: set[str] = set()
    for h in ref_headers:
        s = str(h).strip()
        if not s:
            continue
        canon = canon_attr_for_compare(s)
        if canon and canon not in seen:
            seen.add(canon)
            pairs.append((s, canon))
    pairs.sort(key=lambda x: -len(x[1]))
    return pairs


def extract_attrs_via_dictionary(
    text: str,
    dictionary: dict[str, str],
    label_canon_pairs: Optional[list[tuple[str, str]]] = None,
) -> tuple[list[str], list[str]]:
    """
    Извлечение атрибутов из текста по словарю. НЕ разбивать по пробелам.
    Longest-first: сначала ищем длинные названия (например «Код товара», «Адрес поставщика»).
    Возвращает (найденные canon, неизвестные токены для диагностики).
    """
    if not text or not dictionary:
        return [], []
    normalized = text.replace(NBSP, " ").strip()
    normalized = re.sub(r"\s+", " ", normalized)
    found: list[str] = []
    found_set: set[str] = set()
    used_positions: list[tuple[int, int]] = []

    if label_canon_pairs is None:
        label_canon_pairs = [(c, c) for c in dictionary]

    for label, canon in label_canon_pairs:
        if canon not in dictionary or canon in found_set:
            continue
        label_clean = canon_attr_for_compare(label)
        for pattern in (label_clean, label.strip().casefold(), canon):
            if not pattern:
                continue
            pos = 0
            while True:
                idx = normalized.casefold().find(pattern.casefold(), pos)
                if idx == -1:
                    break
                end = idx + len(pattern)
                overlap = any(
                    not (end <= a or b <= idx) for a, b in used_positions
                )
                if not overlap:
                    found.append(canon)
                    found_set.add(canon)
                    used_positions.append((idx, end))
                pos = idx + 1
                break

    unknown: list[str] = []
    for sep in [",", ";", "\n"]:
        parts = normalized.split(sep)
        for p in parts:
            p = p.strip().rstrip("*.")
            if not p:
                continue
            c = canon_attr_for_compare(p)
            if c and c not in dictionary and c not in found_set:
                if p not in unknown:
                    unknown.append(p)
    return (found, unknown)


def extract_attrs_via_dictionary_simple(
    text: str,
    dictionary: dict[str, str],
) -> list[str]:
    """Упрощённый вызов: только список найденных (обратная совместимость)."""
    pairs = build_label_canon_pairs(
        [k for k in dictionary]
    )
    found, _ = extract_attrs_via_dictionary(text, dictionary, pairs)
    return found


def lookup_in_dictionary(dictionary: dict[str, str], candidate: str) -> Optional[str]:
    """Вернуть canon, если candidate (после канона) есть в словаре."""
    c = canon_attr_for_compare(candidate)
    return dictionary.get(c)


# --- Парсинг ФЗ: стрелки, разбиение по ; и переводам строк, LHS/RHS по запятой/точке с запятой (не по пробелам) ---

ARROW_PATTERNS = ["→", "–", "—", "^->", "=>", "--", "->"]  # – en-dash U+2013


def normalize_fd_arrow(s: str) -> str:
    """Нормализация стрелки к '->'. Сначала длинные варианты."""
    s = s.strip()
    for arrow in ARROW_PATTERNS:
        if arrow in s:
            s = s.replace(arrow, "->")
    if "-" in s and "->" not in s:
        s = s.replace("-", "->", 1)
    return s


def _split_lhs_rhs_tokens(side: str) -> list[str]:
    """Разбить LHS или RHS только по ',' и ';' (не по пробелам). Токены могут быть многословными."""
    tokens: list[str] = []
    for part in re.split(r"[,;]", side):
        t = part.strip().rstrip("*.").strip()
        if t:
            tokens.append(t)
    return tokens


def parse_fd_string(
    s: str,
    dictionary: Optional[dict[str, str]] = None,
) -> list[tuple[list[str], list[str]]]:
    """
    Парсинг строки ФЗ.
    - Разбивать зависимости по ';' и переводам строк.
    - Стрелки: →, ^->, ->, -, --.
    - LHS/RHS разбивать только по ',' и ';' (не по пробелам).
    - Если передан dictionary, каждый токен приводится к canon и проверяется; неизвестные отбрасываются.
    Возвращает список (lhs_list, rhs_list); rhs потом разбить на одиночные атрибуты при необходимости.
    """
    s = normalize_fd_arrow(s)
    if "->" not in s:
        return []
    result: list[tuple[list[str], list[str]]] = []
    for chunk in re.split(r"[;\n]", s):
        chunk = chunk.strip()
        if "->" not in chunk:
            continue
        left, right = chunk.split("->", 1)
        lhs_tokens = _split_lhs_rhs_tokens(left.strip())
        rhs_tokens = _split_lhs_rhs_tokens(right.strip())
        rhs_tokens = [t for t in rhs_tokens if t != ">"]
        if not lhs_tokens or not rhs_tokens:
            continue
        if dictionary:
            lhs_c = []
            for t in lhs_tokens:
                c = dictionary.get(canon_attr_for_compare(t))
                if c is not None:
                    lhs_c.append(c)
            rhs_c = []
            for t in rhs_tokens:
                c = dictionary.get(canon_attr_for_compare(t))
                if c is not None:
                    rhs_c.append(c)
            if lhs_c and rhs_c:
                result.append((lhs_c, rhs_c))
        else:
            result.append(
                ([canon_attr_for_compare(t) for t in lhs_tokens], [canon_attr_for_compare(t) for t in rhs_tokens])
            )
    return result


def _excel_serial_to_ymd(serial: float) -> Optional[str]:
    """Число как дата: дни от 1900-01-01 (serial=1 -> 1900-01-01). Совпадает с интерпретацией многих экспортов."""
    try:
        if not (1 <= serial <= 2958465):  # разумный диапазон дат
            return None
        epoch = datetime(1900, 1, 1)
        d = epoch + timedelta(days=int(serial) - 1)
        return d.strftime("%Y-%m-%d")
    except (ValueError, OSError):
        return None


def _normalize_date_like(s: str) -> str:
    """Приводит дату/время к виду YYYY-MM-DD для сравнения строк таблицы."""
    s = s.strip()
    # Excel datetime "2022-03-15 00:00:00" -> "2022-03-15"
    m = re.match(r"^(\d{4})-(\d{1,2})-(\d{1,2})(?:\s+\d{1,2}:\d{1,2}(?::\d{1,2})?)?$", s)
    if m:
        y, mo, d = m.group(1), m.group(2).zfill(2), m.group(3).zfill(2)
        return f"{y}-{mo}-{d}"
    # "15.03.2022" или "15/03/2022"
    m = re.match(r"^(\d{1,2})[./](\d{1,2})[./](\d{4})$", s)
    if m:
        d, mo, y = m.group(1).zfill(2), m.group(2).zfill(2), m.group(3)
        return f"{y}-{mo}-{d}"
    # Excel serial number (например 44927)
    try:
        f = float(s)
        if f == int(f) and f >= 1:
            ymd = _excel_serial_to_ymd(f)
            if ymd:
                return ymd
    except ValueError:
        pass
    return s


def normalize_cell_value(val: Any) -> str:
    """Trim, число 1.0 -> 1, даты к YYYY-MM-DD для сравнения."""
    if val is None:
        return ""
    s = str(val).strip()
    try:
        f = float(s)
        if f == int(f):
            # Может быть Excel-дата (серийный номер)
            if f >= 1:
                ymd = _excel_serial_to_ymd(f)
                if ymd:
                    return ymd
            return str(int(f))
    except ValueError:
        pass
    return _normalize_date_like(s)


def is_separator_row(row: list[Any], max_col: Optional[int] = None) -> bool:
    """
    Строка считается разделителем, если в диапазоне все непустые значения —
    только точки/многоточие/«…..» (regex-тип с учётом Unicode).
    """
    r = row[:max_col] if max_col is not None else row
    for v in r:
        s = (str(v).strip() if v is not None else "")
        if not s:
            continue
        if not SEPARATOR_ROW_RE.match(s):
            return False
    return True
