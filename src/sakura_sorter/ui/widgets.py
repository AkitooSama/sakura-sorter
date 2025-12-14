from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog


class FilePicker(QWidget):
    def __init__(self, label: str = "", parent=None):
        super().__init__(parent)
        layout = QHBoxLayout()
        if label:
            layout.addWidget(QLabel(label))
        self.edit = QLineEdit()
        layout.addWidget(self.edit)
        b = QPushButton("Browse")
        b.clicked.connect(self._browse)
        layout.addWidget(b)
        self.setLayout(layout)

    def _browse(self):
        d = QFileDialog.getExistingDirectory(self, "Select directory")
        if d:
            self.edit.setText(d)

    def text(self) -> str:
        return self.edit.text()

    def setText(self, s: str):
        self.edit.setText(s)
