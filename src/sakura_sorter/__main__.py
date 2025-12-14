from PyQt6.QtWidgets import QApplication
import sys
from ui.app import SakuraApp

def main():
    app = QApplication(sys.argv)
    
    sakura = SakuraApp()
    sakura.run()
    
    sys.exit(app.exec())