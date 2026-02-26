"""Main window: load files page + report view, run check."""
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QStackedWidget,
    QVBoxLayout,
    QMessageBox,
    QApplication,
)
from PySide6.QtCore import Qt

from app.ui.load_files_page import LoadFilesPage
from app.ui.report_view import ReportView
from app.core.compare import compare
from app.storage import save_session


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Проверка заданий по нормализации БД до 3НФ")
        self.setMinimumSize(700, 500)
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        self._stack = QStackedWidget()
        self._load_page = LoadFilesPage()
        self._report_view = ReportView()
        self._stack.addWidget(self._load_page)
        self._stack.addWidget(self._report_view)
        layout.addWidget(self._stack)

        self._load_page.run_check.connect(self._run_check)
        self._report_view.export_requested.connect(self._on_export_done)
        self._report_view.back_requested.connect(lambda: self._stack.setCurrentWidget(self._load_page))
        self._load_page.ref_selected.connect(lambda _: None)
        self._load_page.stu_selected.connect(lambda _: None)

    def _run_check(self) -> None:
        ref_path, stu_path = self._load_page.get_paths()
        if not ref_path or not stu_path:
            QMessageBox.warning(self, "Ошибка", "Выберите оба файла.")
            return
        try:
            result = compare(ref_path, stu_path)
            self._report_view.set_result(result)
            self._stack.setCurrentWidget(self._report_view)
            save_session(
                ref_path=ref_path,
                stu_path=stu_path,
                fingerprint_ref=result.get("fingerprint_ref", ""),
                fingerprint_stu=result.get("fingerprint_stu", ""),
                fingerprint_match=result.get("fingerprint_match", False),
                score_4=result.get("score_4", ""),
                report_html=self._report_view._last_html,
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Проверка завершилась с ошибкой:\n{e!s}",
            )

    def _on_export_done(self, path: str) -> None:
        QMessageBox.information(self, "Экспорт", f"Отчёт сохранён: {path}")
