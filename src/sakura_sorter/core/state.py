import json
from sakura_sorter.core.config import SETTINGS_FILE

class AppState:
    def __init__(self):
        self.watch_dir = ""
        self.rules: dict[str, str] = {}
        self.strip_tags = True
        self.notifications = True
        self._notifier = None
        self.theme = "pink"
        self.load()

    def load(self):
        if SETTINGS_FILE.exists():
            data = json.loads(SETTINGS_FILE.read_text())
            self.__dict__.update(data)

    def save(self):
        SETTINGS_FILE.write_text(json.dumps(self.__dict__, indent=4))

    @property
    def notifier(self):
        return self._notifier

    @notifier.setter
    def notifier(self, n):
        self._notifier = n
