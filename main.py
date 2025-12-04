"""Main entry point for Character Card Viewer."""

import sys
from PySide6.QtWidgets import QApplication

from app.gui.main_window import MainWindow


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("Character Card Viewer")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

