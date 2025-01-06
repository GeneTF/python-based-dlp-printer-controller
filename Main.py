import sys
from PyQt6.QtWidgets import QApplication
from MainWidgetGUI import MainWindow

import qdarktheme


def main():
    app = QApplication(sys.argv)
    qdarktheme.setup_theme()  # MAKE SURE TO CREDIT THIS PERSON https://pypi.org/project/pyqtdarktheme/
    main_window = MainWindow()
    main_window.showMaximized()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()