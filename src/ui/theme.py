import yaml
from pathlib import Path
from core.config import THEME_DIR
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFontDatabase, QColor, QCursor
from PyQt6.QtWidgets import QGraphicsDropShadowEffect, QPushButton, QListWidget, QLineEdit

class Theme:
    def __init__(self, name: str):
        path = THEME_DIR / f"{name}.yaml"
        self.data = yaml.safe_load(path.read_text())
        font_dir = Path(__file__).parent.parent.parent / "assets/fonts"
        for font_file in font_dir.glob("*.ttf"):
            QFontDatabase.addApplicationFont(str(font_file))

    def qss(self) -> str:
        c = self.data["colors"]
        r = self.data["radius"]
        e = self.data.get("effects", {})

        glow_qss = ""
        if e.get("glow", False):
            glow_qss = f"""
            QPushButton:hover {{
                background: {c['button_hover']};
            }}
            """

        return f"""
        QWidget {{
            background: qlineargradient(x1:0 y1:0 x2:0 y2:1, stop:0 {c['bg_start']}, stop:1 {c['bg_end']});
            color: {c['text']};
            font-family: {self.data['fonts']['main']};
        }}
        QPushButton {{
            background: {c['button']};
            color: {c['text']};
            border: 2px solid {c['border']};
            border-radius: {r['button']}px;
            padding: 6px 12px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background: {c['button_hover']};
        }}
        QLineEdit {{
            background: {c.get('input_bg', c['bg_start'])};
            color: {c.get('input_text', c['text'])};
            border: 2px solid {c['border']};
            border-radius: {r.get('input', 4)}px;
            padding: 4px;
        }}
        QListWidget {{
            background: {c.get('list_bg', c['bg_start'])};
            color: {c.get('list_text', c['text'])};
            border: 2px solid {c['border']};
            border-radius: {r.get('list', 4)}px;
        }}
        {glow_qss}
        """

    def apply_glow(self, widget):
        if self.data.get("effects", {}).get("glow", False) and isinstance(widget, QPushButton):
            effect = QGraphicsDropShadowEffect()
            effect.setBlurRadius(12)
            effect.setColor(QColor(self.data["colors"]["button_hover"]))
            effect.setOffset(0)
            widget.setGraphicsEffect(effect)
        else:
            widget.setGraphicsEffect(None)

    def set_cursor(self, widget):
        cursor_cfg = self.data.get("cursor", {})
        if cursor_cfg.get("pointer_on_buttons", False) and isinstance(widget, QPushButton):
            widget.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        elif cursor_cfg.get("pointer_on_list", False) and isinstance(widget, (QListWidget, QLineEdit)):
            widget.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        else:
            widget.unsetCursor()
