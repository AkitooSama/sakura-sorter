from PyQt6.QtWidgets import QApplication
import sys
from sakura_sorter.ui.app import SakuraApp

def main():
    app = QApplication(sys.argv)
    
    sakura = SakuraApp()
    sakura.run()
    
    sys.exit(app.exec())
    
if __name__ == "__main__":
    main()