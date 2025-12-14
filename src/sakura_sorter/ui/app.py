from sakura_sorter.ui.main_window import MainWindow
from sakura_sorter.core.state import AppState


class SakuraApp:
    def __init__(self):
        self.state = AppState()
        self.win = None

    def run(self):
        self.win = MainWindow(self.state)
        self.win.show()
        return self.win
