from watchdog.events import FileSystemEventHandler
from pathlib import Path
from core.tags import parse
from core.file_ops import distribute

class SortHandler(FileSystemEventHandler):
    def __init__(self, state):
        self.state = state

    def on_created(self, event):
        if event.is_directory:
            return

        path = Path(event.src_path)
        tags = parse(path.name)

        targets = [
            Path(self.state.rules[t])
            for t in tags
            if t in self.state.rules
        ]

        if targets:
            result = distribute(path, targets, self.state.strip_tags)
            try:
                notifier = getattr(self.state, "notifier", None)
                if notifier:
                    notifier.add_event(result)
            except Exception:
                pass
