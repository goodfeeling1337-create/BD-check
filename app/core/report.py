"""HTML report builder. Все подписи и форматирование — по-русски."""
import html
from typing import Any, List, Tuple

# Русские подписи статусов
STATUS_RU = {
    "PASS": "Зачёт",
    "WARN": "Предупреждение",
    "FAIL": "Не зачёт",
    "INSF": "Нет данных",
}

# Краткие названия заданий для отчёта
TASK_TITLES = {
    1: "Заголовки универсального отношения",
    2: "Повторяющаяся группа (множество атрибутов)",
    3: "Таблица в 1НФ",
    4: "Функциональные зависимости",
    5: "Первичный ключ в 1НФ",
    6: "Частичные ФЗ",
    7: "Вложенные частичные ФЗ (цепочки)",
    8: "Транзитивные ФЗ",
    9: "Вложенные транзитивные ФЗ",
    10: "Аномалии в 1НФ",
    11: "Схемы отношений во 2НФ",
    12: "Аномалии во 2НФ",
    13: "Схемы отношений в 3НФ",
}


def _escape(s: str) -> str:
    return html.escape(str(s))


def _row_to_html(row: List[Any]) -> str:
    return "".join(f"<td>{_escape(str(c))}</td>" for c in row)


def _format_value(val: Any, max_items: int = 50) -> str:
    """Форматирует значение для читаемого вывода (русский текст, без repr)."""
    if val is None:
        return "—"
    if isinstance(val, (list, tuple)):
        if not val:
            return "—"
        # Список пар (lhs, rhs) — ФЗ: ([A,B], "C")
        if (val and isinstance(val[0], (list, tuple)) and len(val[0]) == 2
                and isinstance(val[0][1], str)):
            parts = []
            for item in val[:max_items]:
                lhs, rhs = item[0], item[1]
                lhs_str = ", ".join(str(x) for x in lhs) if isinstance(lhs, (list, tuple)) else str(lhs)
                parts.append(f"{lhs_str} → {rhs}")
            tail = " …" if len(val) > max_items else ""
            return "; ".join(parts) + tail
        # Список строк (атрибуты, ключ)
        if val and isinstance(val[0], str):
            return ", ".join(str(x) for x in val[:max_items]) + (" …" if len(val) > max_items else "")
        # Список списков (строки таблицы)
        if val and isinstance(val[0], (list, tuple)):
            lines = []
            for row in val[:15]:
                lines.append(" | ".join(str(c) for c in row))
            return "\n".join(lines) + ("\n…" if len(val) > 15 else "")
    if isinstance(val, set):
        return ", ".join(str(x) for x in sorted(val)[:max_items]) + (" …" if len(val) > max_items else "")
    if isinstance(val, dict):
        return "; ".join(f"{k}: {v}" for k, v in list(val.items())[:20])
    return str(val)


def _format_value_html(val: Any) -> str:
    """То же, но с переносами и экранированием для HTML."""
    raw = _format_value(val)
    return _escape(raw).replace("\n", "<br>\n")


def build_html_report(compare_result: dict) -> str:
    """
    Build structured HTML report from compare() result.
    """
    task_results = compare_result.get("task_results", {})
    score_4 = compare_result.get("score_4", "")
    fp_match = compare_result.get("fingerprint_match", True)
    fp_warn = compare_result.get("fingerprint_warn", "")

    fp_label = "Совпадение варианта: да" if fp_match else "Совпадение варианта: нет (возможно другой вариант или не тот файл)"
    score_label = {"++": "отлично", "+-": "хорошо", "-+": "удовлетворительно", "--": "неудовлетворительно"}.get(score_4, score_4)

    parts = [
        "<!DOCTYPE html><html><head><meta charset='utf-8'><title>Отчёт проверки</title>",
        "<style>",
        "body{font-family:system-ui,'Segoe UI',sans-serif;margin:1.5rem;max-width:900px;}",
        "h1{font-size:1.4rem;border-bottom:1px solid #ccc;padding-bottom:0.5rem;}",
        "h2{font-size:1.15rem;margin-top:1.5rem;}",
        "table{border-collapse:collapse;margin:0.75rem 0;width:100%;}",
        "th,td{border:1px solid #ccc;padding:6px 10px;text-align:left;vertical-align:top;}",
        "th{background:#f5f5f5;}",
        ".pass{color:#0a0;} .warn{color:#c60;} .fail{color:#c00;} .insf{color:#666;}",
        "summary{cursor:pointer;padding:4px 0;}",
        ".details{margin:0.5rem 0 1rem 1rem;}",
        ".compare-table{margin:0.5rem 0;}",
        ".expected{background:#f8f8f8;}",
        ".cell-label{font-weight:bold;color:#444;}",
        "pre, .code{font-family:ui-monospace,monospace;font-size:0.9em;white-space:pre-wrap;}",
        "</style></head><body>",
        "<h1>Отчёт проверки заданий по нормализации БД до 3НФ</h1>",
        "<p><b>Эталон:</b> " + _escape(compare_result.get("ref_path", "")) + "</p>",
        "<p><b>Файл студента:</b> " + _escape(compare_result.get("stu_path", "")) + "</p>",
        f"<p><b>{fp_label}</b></p>",
        f"<p><b>Оценка по заданию №4 (функциональные зависимости):</b> {_escape(score_4)} ({score_label})</p>",
        "<h2>Сводка по заданиям</h2>",
        "<table><tr><th>№</th><th>Задание</th><th>Результат</th></tr>",
    ]

    for i in range(1, 14):
        r = task_results.get(i)
        status_en = r.status if r else "INSF"
        status_ru = STATUS_RU.get(status_en, status_en)
        cls = status_en.lower()
        title = TASK_TITLES.get(i, f"Задание {i}")
        parts.append(f"<tr><td>{i}</td><td>{_escape(title)}</td><td class='{cls}'><b>{status_ru}</b></td></tr>")

    parts.append("</table><h2>Детали: сравнение «Ожидалось» и «Получено»</h2>")

    for i in range(1, 14):
        r = task_results.get(i)
        if not r:
            continue
        status_ru = STATUS_RU.get(r.status, r.status)
        title = TASK_TITLES.get(i, f"Задание {i}")
        parts.append(f"<details open><summary><b>Задание №{i}. {_escape(title)}</b> — {status_ru}</summary><div class='details'>")

        # Таблица сравнения: Ожидалось | Получено
        parts.append("<table class='compare-table'><tr><th>Ожидалось (эталон)</th><th>Получено (ответ студента)</th></tr><tr>")
        expected_cell = _format_value_html(r.expected) if r.expected is not None else "—"
        actual_cell = _format_value_html(r.actual) if r.actual is not None else "—"
        parts.append(f"<td class='expected'>{expected_cell}</td><td>{actual_cell}</td></tr></table>")

        if r.missing:
            parts.append("<p><b>Отсутствует в ответе студента:</b></p>")
            if i == 3 and isinstance(r.missing, list) and r.missing and isinstance(r.missing[0], (list, tuple)):
                parts.append("<table><tr><th>№</th><th>Строка данных</th></tr>")
                for j, row in enumerate(r.missing[:10]):
                    parts.append(f"<tr><td>{j+1}</td><td>{_row_to_html(list(row))}</td></tr>")
                if len(r.missing) > 10:
                    parts.append(f"<tr><td colspan='2'>… и ещё {len(r.missing) - 10} строк</td></tr>")
                parts.append("</table>")
            else:
                parts.append(f"<p class='code'>{_format_value_html(r.missing)}</p>")
        if r.extra:
            parts.append("<p><b>Лишнее в ответе студента:</b></p>")
            if i == 3 and isinstance(r.extra, list) and r.extra and isinstance(r.extra[0], (list, tuple)):
                parts.append("<table><tr><th>№</th><th>Строка данных</th></tr>")
                for j, row in enumerate(r.extra[:10]):
                    parts.append(f"<tr><td>{j+1}</td><td>{_row_to_html(list(row))}</td></tr>")
                if len(r.extra) > 10:
                    parts.append(f"<tr><td colspan='2'>… и ещё {len(r.extra) - 10} строк</td></tr>")
                parts.append("</table>")
            else:
                parts.append(f"<p class='code'>{_format_value_html(r.extra)}</p>")
        if r.details and not (r.missing or r.extra):
            details_ru = _details_ru(r.details, i)
            if details_ru:
                parts.append(f"<p><b>Пояснение:</b> {_escape(details_ru)}</p>")
        if r.explanation:
            parts.append(f"<p>{_escape(r.explanation)}</p>")
        parts.append("</div></details>")

    parts.append("</body></html>")
    return "\n".join(parts)


def _details_ru(details: dict, task_num: int) -> str:
    """Переводит ключи details на русский для пояснения."""
    if not details:
        return ""
    parts = []
    for k, v in details.items():
        k_ru = {
            "score": "оценка",
            "missing_count": "количество отсутствующих",
            "extra_count": "количество лишних",
            "reason": "причина",
            "order_warn": "порядок элементов",
            "coverage": "покрытие атрибутов",
            "relation": "отношение",
            "violations": "нарушения",
            "lossless": "беспотерьность",
            "dep_pres": "сохранение зависимостей",
            "error": "ошибка",
            "lossless_warn": "предупреждение о беспотерьности",
            "dep_pres_warn": "предупреждение о сохранении зависимостей",
        }.get(k, k)
        if k == "reason":
            v_ru = {
                "header_mismatch": "не совпадают заголовки таблицы",
                "order_mismatch": "не совпадает порядок атрибутов",
                "empty": "пустой ответ",
                "off_topic": "ответ не по теме",
                "not_superkey": "набор не является суперключом",
                "not_minimal": "ключ не минимален",
                "pk_hint_empty_cell": "в ключевом столбце пустая ячейка",
                "pk_hint_duplicate": "дубликат по ключу",
            }.get(str(v), str(v))
        elif k == "error":
            v_ru = str(v)
        else:
            v_ru = str(v)
        if v_ru:
            parts.append(f"{k_ru}: {v_ru}")
    return ". ".join(parts)
