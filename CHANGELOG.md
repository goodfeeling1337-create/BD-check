# Changelog

## Ключевые правки по модулям

### P0 — Запуск и формат
- **pyproject.toml**: `requires-python = ">=3.11"`, black/ruff target `py311`.
- **CI** (`.github/workflows/ci.yml`): `python -m compileall -q app`, `pytest tests/ -v`.
- **pre-commit**: black, ruff, isort.

### P0 — Парсинг атрибутов
- **app/core/checks/common.py**: Извлечение атрибутов по словарю (dictionary-based), без разбиения по пробелам; longest-first; канонизация (trim, casefold, ё→е, хвостовые `*`/`.`). `extract_attrs_via_dictionary` / `extract_attrs_via_dictionary_simple`.

### P0 — Парсинг ФЗ и скоринг
- **common.py**: `parse_fd_string` — стрелки (→, —, ^->, =>, --, ->), разбиение по `;` и `\n`, LHS/RHS только по `,` и `;`; валидация по словарю #1.
- **compare.py**: При пустом F_ref и непустом блоке #4 эталона — FAIL с текстом «не удалось распознать ФЗ из эталона», без ложного «++».
- **scoring.py**: Оценка ++/+-/-+/-- по доле покрытых ФЗ (closure); при пустом F_ref возврат (0.0, "—").

### P1 — Excel
- **table_detect.py**: `TableInBlock` с `min_col`/`max_col`; разделительные строки через `SEPARATOR_ROW_RE` из common; пропуск якоря и инструкций («ответ:», «Задание №N»).
- **importer.py**: Извлечение данных в диапазоне `min_col`..`max_col`; фильтр строк-инструкций в text_lines.

### P1 — Проверки #1–#13
- Проверки переведены на чтение из семантического графа (ref_graph/stu_graph); эталон и студент согласованы с методикой (заголовки, повторяющаяся группа, 1НФ+PK-hint, ФЗ, partial/transitive, 2НФ/3НФ, аномалии).
- **task4/task5**: При FAIL в отчёт добавляется поле `explanation` (explain_missing_fd, пояснения по суперключу/минимальности).

### P1 — Семантическое ядро
- **build_graph.py**: Заполнение графа по всем заданиям (атрибуты, ФЗ, PK, частичные/транзитивные, отношения 11/13, текст 10/12).
- **query.py**: `get_attributes`, `get_fds`, `get_pk`, `get_repeating_group`, `get_table_1nf`, `get_pk_hint`, `get_text`, `get_relations`.
- **explain.py**: Объяснения для missing FD, partial/transitive, 2НФ/3НФ, coverage.

### P1 — Отчёт и UI
- **report.py**: HTML с `html.escape`; секции по #1–#13 (ожидалось/получено, missing/extra); для #3 — до 10 строк; для #4 — оценка и missing FD; для #11/#13 — coverage, lossless, dep_pres; перевод reason/error в _details_ru.
- **report_view.py**: QTextEdit.setHtml для отчёта; кнопка «Экспорт в HTML» сохраняет файл.

### P2 — Производительность ключей
- **app/core/settings.py**: `KEYS_MAX_OPTIONAL`, `KEYS_TIMEOUT_SEC`.
- **keys.py**: Кэш замыкания при поиске кандидатных ключей (`_closure_cached`), использование `KEYS_MAX_OPTIONAL` для ограничения перебора.

### Тесты
- **test_tasks_core.py**: canon, parse_fd (в т.ч. многословные атрибуты), стрелки, разбиение по `;` и `\n`, separator row, dictionary extraction.
- **test_scoring.py**: Полное покрытие, пустой F_ref (без ложного ++).
- **test_keys.py**: superkey, candidate_keys, ограничение max_optional.
- **test_excel_smoke.py**: Блоки «Задание №1»…«№13», parse_workbook, separator row.
