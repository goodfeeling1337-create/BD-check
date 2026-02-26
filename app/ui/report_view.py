"""Report view: summary, task statuses, expandable details, export HTML."""
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QScrollArea,
    QFrame,
    QFileDialog,
)
from PySide6.QtCore import Signal
from typing import Optional


class ReportView(QWidget):
    export_requested = Signal(str)  # path
    back_requested = Signal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self._summary = QLabel("Результаты проверки появятся здесь.")
        self._summary.setWordWrap(True)
        layout.addWidget(self._summary)

        self._details = QTextEdit()
        self._details.setReadOnly(True)
        self._details.setPlaceholderText("Детали по заданиям...")
        layout.addWidget(self._details)

        row = QHBoxLayout()
        self._back_btn = QPushButton("Новая проверка")
        self._back_btn.clicked.connect(lambda: self.back_requested.emit())
        row.addWidget(self._back_btn)
        self._export_btn = QPushButton("Экспорт в HTML")
        self._export_btn.clicked.connect(self._on_export)
        row.addWidget(self._export_btn)
        row.addStretch()
        layout.addLayout(row)
        self._last_html = ""
        self._last_result = None

    def set_result(self, compare_result: dict) -> None:
        from app.core.report import (
            build_html_report,
            STATUS_RU,
            TASK_TITLES,
        )
        task_results = compare_result.get("task_results", {})
        score_4 = compare_result.get("score_4", "")
        fp_ok = compare_result.get("fingerprint_match", True)
        score_label = {"++": "отлично", "+-": "хорошо", "-+": "удовлетворительно", "--": "неудовлетворительно"}.get(
            score_4, score_4
        )

        lines = [
            "Совпадение варианта: да" if fp_ok else "Совпадение варианта: нет (возможно другой вариант или не тот файл).",
            "",
            f"Оценка по заданию №4 (ФЗ): {score_4} ({score_label}).",
            "",
            "Результаты по заданиям:",
        ]
        for i in range(1, 14):
            r = task_results.get(i)
            status_ru = STATUS_RU.get(r.status, r.status) if r else "Нет данных"
            title = TASK_TITLES.get(i, f"Задание {i}")
            lines.append(f"  №{i}. {title} — {status_ru}")
        lines.append("")
        lines.append("Ниже: по каждому заданию приведены «Ожидалось» (эталон) и «Получено» (ответ студента).")
        self._summary.setText("\n".join(lines))

        html = build_html_report(compare_result)
        self._details.setHtml(html)
        self._last_html = html
        self._last_result = compare_result

    def _on_export(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить отчёт",
            str(Path.home()),
            "HTML (*.html);;All (*)",
        )
        if path:
            if not path.endswith(".html"):
                path += ".html"
            with open(path, "w", encoding="utf-8") as f:
                f.write(getattr(self, "_last_html", "<p>No report</p>"))
            self.export_requested.emit(path)
