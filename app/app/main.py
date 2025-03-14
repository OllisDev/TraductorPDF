import sys
from PyQt6.QtWidgets import QApplication
from app.ui import PDFToJPGTranslator

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PDFToJPGTranslator()
    window.show()
    sys.exit(app.exec())
