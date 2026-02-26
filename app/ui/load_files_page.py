"""Page: select reference and student Excel files."""
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QFileDialog,
    QGroupBox,
)
from PySide6.QtCore import Signal
from typing import Optional


class LoadFilesPage(QWidget):
    ref_selected = Signal(str)
    stu_selected = Signal(str)
    run_check = Signal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._ref_path = ""
        self._stu_path = ""
        layout = QVBoxLayout(self)

        g1 = QGroupBox("Файлы")
        g1_layout = QVBoxLayout(g1)
        row1 = QHBoxLayout()
        self._ref_label = QLabel("Эталон (reference.xlsx): не выбран")
        self._ref_btn = QPushButton("Выбрать эталон")
        self._ref_btn.clicked.connect(self._on_select_ref)
        row1.addWidget(self._ref_label)
        row1.addWidget(self._ref_btn)
        g1_layout.addLayout(row1)
        row2 = QHBoxLayout()
        self._stu_label = QLabel("Студент (student.xlsx): не выбран")
        self._stu_btn = QPushButton("Выбрать файл студента")
        self._stu_btn.clicked.connect(self._on_select_stu)
        row2.addWidget(self._stu_label)
        row2.addWidget(self._stu_btn)
        g1_layout.addLayout(row2)
        layout.addWidget(g1)

        self._check_btn = QPushButton("Проверить")
        self._check_btn.clicked.connect(lambda: self.run_check.emit())
        self._check_btn.setEnabled(False)
        layout.addWidget(self._check_btn)
        layout.addStretch()

    def _on_select_ref(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите эталон",
            str(Path.home()),
            "Excel (*.xlsx *.xls);;All (*)",
        )
        if path:
            self._ref_path = path
            self._ref_label.setText(f"Эталон: {Path(path).name}")
            self.ref_selected.emit(path)
            self._update_check_btn()

    def _on_select_stu(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите файл студента",
            str(Path.home()),
            "Excel (*.xlsx *.xls);;All (*)",
        )
        if path:
            self._stu_path = path
            self._stu_label.setText(f"Студент: {Path(path).name}")
            self.stu_selected.emit(path)
            self._update_check_btn()

    def _update_check_btn(self) -> None:
        self._check_btn.setEnabled(bool(self._ref_path and self._stu_path))

    def get_paths(self) -> tuple[str, str]:
        return (self._ref_path, self._stu_path)
