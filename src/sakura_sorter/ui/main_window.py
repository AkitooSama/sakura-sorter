from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QListWidget, QFileDialog, QMessageBox, QDialog, QTextEdit, QComboBox,
    QSystemTrayIcon, QMenu, QStyle, QCheckBox, QApplication
)
from PyQt6.QtGui import QIcon, QAction
from watchdog.observers import Observer
from sakura_sorter.core.config import ICON, THEME_DIR
from sakura_sorter.core.history import delete_all_history, delete_entry_by_id, search_history
from sakura_sorter.core.watcher import SortHandler
from pathlib import Path
from typing import Optional
from sakura_sorter.ui.notifier import Notifier
from sakura_sorter.ui.theme import Theme
import json


class MainWindow(QMainWindow):
    def __init__(self, state):
        super().__init__()
        self.state = state
        self.setWindowTitle("Sakura Sorter")
        self.setWindowIcon(QIcon(str(ICON)))
        self.current_theme = self.state.theme
        self.theme = Theme(self.current_theme)
        self.setStyleSheet(self.theme.qss())
        self.observer: Optional[Observer] = None
        self.handler: Optional[SortHandler] = None
        self.tray: Optional[QSystemTrayIcon] = None
        self.notifier: Optional[Notifier] = None
        self._build_ui()
        self._apply_theme()
        self._create_tray()
        self.refresh_rules()

    def _apply_theme(self):
        for btn in self.findChildren(QPushButton):
            self.theme.apply_glow(btn)
            self.theme.set_cursor(btn)
        for lst in self.findChildren(QListWidget):
            self.theme.set_cursor(lst)
        for inp in self.findChildren(QLineEdit):
            self.theme.set_cursor(inp)

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout()
        central.setLayout(root)

        theme_row = QHBoxLayout()
        theme_row.addWidget(QLabel("Theme:"))
        self.theme_dropdown = QComboBox()
        self.theme_names = [f.stem for f in THEME_DIR.glob("*.yaml")]
        self.theme_dropdown.addItems(self.theme_names)
        self.theme_dropdown.setCurrentText(self.current_theme)
        self.theme_dropdown.currentTextChanged.connect(self.load_theme)
        theme_row.addWidget(self.theme_dropdown)
        root.addLayout(theme_row)

        row_watch = QHBoxLayout()
        row_watch.addWidget(QLabel("Watch Directory:"))
        self.watch_edit = QLineEdit(self.state.watch_dir)
        row_watch.addWidget(self.watch_edit)
        b = QPushButton("Browse")
        b.clicked.connect(self.browse_watch)
        row_watch.addWidget(b)
        root.addLayout(row_watch)

        opts_row = QHBoxLayout()
        self.strip_cb = QCheckBox("Strip tag prefix on save")
        self.strip_cb.setChecked(bool(self.state.strip_tags))
        self.strip_cb.stateChanged.connect(self._on_strip_changed)
        opts_row.addWidget(self.strip_cb)
        self.notify_cb = QCheckBox("Enable notifications")
        self.notify_cb.setChecked(bool(getattr(self.state, "notifications", True)))
        self.notify_cb.stateChanged.connect(self._on_notify_changed)
        opts_row.addWidget(self.notify_cb)
        root.addLayout(opts_row)

        row_rule = QHBoxLayout()
        row_rule.addWidget(QLabel("Tag (comma-separated):"))
        self.tag_edit = QLineEdit()
        self.tag_edit.setPlaceholderText("e.g. w for wallpapers")
        row_rule.addWidget(self.tag_edit)
        row_rule.addWidget(QLabel("Target Folder:"))
        self.target_edit = QLineEdit()
        row_rule.addWidget(self.target_edit)
        tb = QPushButton("Browse")
        tb.clicked.connect(self.browse_target)
        row_rule.addWidget(tb)
        addb = QPushButton("Add Rule")
        addb.clicked.connect(self.add_rule)
        row_rule.addWidget(addb)
        root.addLayout(row_rule)

        self.rules_list = QListWidget()
        root.addWidget(self.rules_list)

        row_actions = QHBoxLayout()
        self.remove_btn = QPushButton("Remove Selected")
        self.remove_btn.clicked.connect(self.remove_selected)
        row_actions.addWidget(self.remove_btn)
        self.delete_all_rules_btn = QPushButton("Delete All Rules")
        self.delete_all_rules_btn.clicked.connect(self.delete_all_rules)
        row_actions.addWidget(self.delete_all_rules_btn)
        self.reset_settings_btn = QPushButton("Reset Settings")
        self.reset_settings_btn.clicked.connect(self.reset_settings)
        row_actions.addWidget(self.reset_settings_btn)
        self.toggle_btn = QPushButton("Start")
        self.toggle_btn.clicked.connect(self.toggle_watcher)
        row_actions.addWidget(self.toggle_btn)
        self.history_btn = QPushButton("History")
        self.history_btn.clicked.connect(self.show_history)
        row_actions.addWidget(self.history_btn)
        root.addLayout(row_actions)

    def load_theme(self, theme_name: str):
        self.current_theme = theme_name
        self.state.theme = theme_name
        self.state.save()
        self.theme = Theme(theme_name)
        self.setStyleSheet(self.theme.qss())
        self._apply_theme()

    def browse_watch(self):
        d = QFileDialog.getExistingDirectory(self, "Select watch directory")
        if d:
            self.watch_edit.setText(d)
            self.state.watch_dir = d
            self.state.save()

    def browse_target(self):
        d = QFileDialog.getExistingDirectory(self, "Select target directory")
        if d:
            self.target_edit.setText(d)

    def add_rule(self):
        tag_text = self.tag_edit.text().strip()
        target = self.target_edit.text().strip()
        if not tag_text or not target:
            QMessageBox.warning(self, "Invalid", "Tag and target folder are required")
            return
        tags = [t.strip().lower() for t in tag_text.split(",") if t.strip()]
        for t in tags:
            self.state.rules[t] = str(Path(target))
        self.refresh_rules()
        self.tag_edit.clear()
        self.target_edit.clear()
        self.state.save()

    def remove_selected(self):
        items = self.rules_list.selectedItems()
        if not items:
            return
        for it in items:
            tag = it.text().split("->", 1)[0].strip()
            self.state.rules.pop(tag, None)
        self.refresh_rules()
        self.state.save()

    def delete_all_rules(self):
        self.state.rules.clear()
        self.refresh_rules()
        self.state.save()

    def reset_settings(self):
        self.state.watch_dir = ""
        self.state.rules.clear()
        self.state.strip_tags = True
        self.state.notifications = True
        self.state.theme = "pink"
        self.state.save()
        self.watch_edit.setText("")
        self.refresh_rules()
        self.theme_dropdown.setCurrentText("pink")
        self.load_theme("pink")
        self.strip_cb.setChecked(True)
        self.notify_cb.setChecked(True)

    def refresh_rules(self):
        self.rules_list.clear()
        for tag, path in sorted(self.state.rules.items()):
            self.rules_list.addItem(f"{tag} -> {path}")

    def toggle_watcher(self):
        if self.observer is None:
            watch_dir = self.watch_edit.text().strip()
            if not watch_dir:
                QMessageBox.warning(self, "No directory", "Please select a watch directory first")
                return
            p = Path(watch_dir)
            if not p.exists() or not p.is_dir():
                QMessageBox.warning(self, "Invalid", "Selected watch directory does not exist or is not a directory")
                return
            self.state.watch_dir = str(p)
            self.state.save()
            self.observer = Observer()
            self.handler = SortHandler(self.state)
            self.observer.schedule(self.handler, str(p), recursive=False)
            self.observer.start()
            self.toggle_btn.setText("Stop")
            if self.notifier and getattr(self.state, "notifications", False):
                self.state.notifier = self.notifier
        else:
            try:
                self.observer.stop()
                self.observer.join(timeout=1)
            except Exception:
                pass
            self.observer = None
            self.handler = None
            self.toggle_btn.setText("Start")
            self.state.notifier = None

    def _on_strip_changed(self, st):
        self.state.strip_tags = bool(st)
        self.state.save()

    def _on_notify_changed(self, st):
        self.state.notifications = bool(st)
        self.state.save()

    def show_history(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("History")
        layout = QVBoxLayout()
        dlg.setLayout(layout)

        filter_row = QHBoxLayout()
        filter_row.addWidget(QLabel("Filter:"))
        search = QLineEdit()
        filter_row.addWidget(search)
        filter_row.addWidget(QLabel("Status:"))
        status = QComboBox()
        status.addItems(["All", "Only OK", "Only Failed"])
        filter_row.addWidget(status)
        clear_btn = QPushButton("Clear")
        filter_row.addWidget(clear_btn)
        layout.addLayout(filter_row)

        list_widget = QListWidget()
        detail = QTextEdit()
        detail.setReadOnly(True)
        layout.addWidget(list_widget)
        layout.addWidget(detail)

        entry_ids = []

        def format_entry(e):
            ts = e.get("ts", "")
            src = e.get("src", "")
            dests = ", ".join(e.get("destinations", []))
            ok = "OK" if e.get("success") else "FAILED"
            msg = e.get("message", "")
            return f"[{ts}] {ok}: {src} -> {dests} {msg}"

        def refresh_list():
            list_widget.clear()
            entry_ids.clear()
            q = search.text().strip()
            st = status.currentText()
            entries = search_history(q, st)
            for e in entries[:200]:
                list_widget.addItem(format_entry(e))
                entry_ids.append(e["id"])

        def on_select():
            idx = list_widget.currentRow()
            if 0 <= idx < len(entry_ids):
                eid = entry_ids[idx]
                entry = next((e for e in search_history("", "All") if e["id"] == eid), None)
                if entry:
                    detail.setPlainText(json.dumps(entry, indent=2, ensure_ascii=False))
                else:
                    detail.clear()
            else:
                detail.clear()

        bottom = QHBoxLayout()
        delete_selected_btn = QPushButton("Delete Selected")
        delete_all_btn = QPushButton("Delete All")
        close_btn = QPushButton("Close")
        bottom.addWidget(delete_selected_btn)
        bottom.addWidget(delete_all_btn)
        bottom.addStretch(1)
        bottom.addWidget(close_btn)
        layout.addLayout(bottom)

        search.textChanged.connect(refresh_list)
        status.currentIndexChanged.connect(refresh_list)
        list_widget.itemSelectionChanged.connect(on_select)
        clear_btn.clicked.connect(lambda: (search.clear(), status.setCurrentIndex(0), refresh_list()))

        delete_selected_btn.clicked.connect(
            lambda: (
                delete_entry_by_id(entry_ids[list_widget.currentRow()])
                if 0 <= list_widget.currentRow() < len(entry_ids)
                else None,
                refresh_list()
            )
        )

        delete_all_btn.clicked.connect(lambda: (delete_all_history(), refresh_list()))
        close_btn.clicked.connect(dlg.reject)

        refresh_list()
        dlg.resize(900, 500)
        dlg.exec()

    def _create_tray(self):
        style = QApplication.instance().style()
        icon = style.standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
        self.tray = QSystemTrayIcon(icon, self)
        menu = QMenu()
        act_restore = QAction("Restore")
        act_quit = QAction("Quit")
        menu.addAction(act_restore)
        menu.addAction(act_quit)
        act_restore.triggered.connect(self._restore_from_tray)
        act_quit.triggered.connect(self._quit_app)
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(lambda reason: self._restore_from_tray() if reason else None)
        self.tray.show()
        self.notifier = Notifier(self.tray)

    def _restore_from_tray(self):
        self.show()
        self.raise_()
        self.activateWindow()

    def _quit_app(self):
        try:
            if self.observer:
                self.observer.stop()
                self.observer.join(timeout=1)
        except Exception:
            pass
        QApplication.quit()

    def closeEvent(self, event):
        if self.tray:
            self.hide()
            try:
                self.tray.showMessage("Sakura Sorter", "Running in background. Use tray to Quit or Restore.")
            except Exception:
                pass
            event.ignore()
        else:
            event.accept()
