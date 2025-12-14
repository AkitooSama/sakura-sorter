from PyQt6.QtCore import QTimer
from typing import List
import traceback


class Notifier:
    def __init__(self, tray_icon, batch_seconds: int = 30):
        self.tray = tray_icon
        self.batch_seconds = batch_seconds
        self._queue: List[dict] = []
        self._timer = QTimer()
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.flush)

    def add_event(self, event: dict):
        try:
            self._queue.append(event)
            if not self._timer.isActive():
                self._timer.start(self.batch_seconds * 1000)
        except Exception:
            traceback.print_exc()

    def flush(self):
        if not self._queue:
            return
        try:
            count = len(self._queue)
            moved = sum(1 for e in self._queue if e.get("success"))
            failed = count - moved
            titles = []
            for e in self._queue:
                src = e.get("src", "")
                titles.append(src)
            body = f"{moved} succeeded, {failed} failed. Files:\n" + "\n".join(titles[:10])
            if self.tray and hasattr(self.tray, "showMessage"):
                try:
                    self.tray.showMessage("Sakura Sorter", body)
                except Exception:
                    pass
        except Exception:
            traceback.print_exc()
        finally:
            self._queue.clear()