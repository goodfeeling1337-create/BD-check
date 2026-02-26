# Проверка заданий по нормализации БД до 3НФ

Десктопное приложение (macOS first) для автоматизированной проверки заданий по методике «универсального отношения». Сравнивает ответ студента с эталоном преподавателя по семантике, а не по ячейкам.

## Требования

- Python 3.11+
- macOS (основная платформа), кроссплатформенно по возможности

## Установка

```bash
pip install -e ".[dev]"
# или
pip install PySide6 openpyxl pytest pyinstaller
```

## Запуск

Из корня репозитория:

```bash
python -m app
```

Либо:

```bash
cd app && python main.py
```

## Сборка .app для macOS (PyInstaller)

Из корня репозитория:

```bash
pip install pyinstaller
pyinstaller --name "DB-Norm-Checker" \
  --windowed \
  --onefile \
  --paths . \
  app/main.py
```

Либо с указанием скрытых импортов (если появятся ошибки при запуске .app):

```bash
pyinstaller --name "DB-Norm-Checker" --windowed --onefile \
  --hidden-import=openpyxl --hidden-import=PySide6 \
  --paths . \
  app/main.py
```

Собранное приложение: `dist/DB-Norm-Checker.app`.

## Структура

- `app/` — приложение: `main.py`, `storage.py`, `ui/`, `core/`
- `app/core/excel/` — парсинг Excel (блоки «Задание №N», таблицы, импорт)
- `app/core/semantic/` — граф фактов (TripleStore), рубрикатор аномалий, объяснения
- `app/core/algos/` — ФЗ (closure, minimal cover), ключи, 2НФ/3НФ, декомпозиция
- `app/core/checks/` — проверки заданий №1–№13, сравнение, оценка #4
- `tests/` — pytest (fd, keys, nf, scoring, excel smoke, tasks)

## Использование

1. Выберите эталон (`reference.xlsx`) и файл студента (`student.xlsx`).
2. Нажмите «Проверить».
3. Просмотрите сводку и детали по заданиям, при необходимости экспортируйте отчёт в HTML.

## Тесты

```bash
# из корня репозитория
pip install -e ".[dev]"
pytest
# или с путём
PYTHONPATH=. pytest tests/ -v
```

Проверка компиляции: `python -m compileall -q app`

## Форматирование и линтер

```bash
pip install black ruff isort pre-commit
pre-commit install
black app tests
ruff check app tests
isort app tests
```

## Сборка .app (macOS)

```bash
pip install pyinstaller
pyinstaller --name "DB-Norm-Checker" --windowed --onefile --paths . app/main.py
# при необходимости:
pyinstaller --name "DB-Norm-Checker" --windowed --onefile \
  --hidden-import=openpyxl --hidden-import=PySide6 --paths . app/main.py
```

Собранное приложение: `dist/DB-Norm-Checker.app`.
