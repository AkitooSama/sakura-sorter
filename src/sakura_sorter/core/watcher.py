from watchdog.events import FileSystemEventHandler
from pathlib import Path
from sakura_sorter.core.tags import parse
from sakura_sorter.core.file_ops import distribute
import time

class SortHandler(FileSystemEventHandler):
    def __init__(self, state):
        self.state = state

    def _process_file(self, path: Path):
        retries = 5
        while retries > 0:
            if path.exists() and path.stat().st_size > 0:
                try:
                    with path.open("rb"):
                        break
                except Exception:
                    pass
            time.sleep(0.2)
            retries -= 1
        else:
            return

        tags = parse(path.name)
        targets = [
            Path(self.state.rules[t])
            for t in tags
            if t in self.state.rules
        ]
        if targets:
            result = distribute(path, targets, self.state.strip_tags)
            notifier = getattr(self.state, "notifier", None)
            if notifier:
                notifier.add_event(result)

    def on_created(self, event):
        if not event.is_directory:
            self._process_file(Path(event.src_path))

    def on_moved(self, event):
        if not event.is_directory:
            self._process_file(Path(event.dest_path))
