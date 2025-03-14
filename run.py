import sys
from PyQt6.QtWidgets import QApplication
from app.ui import PDFToJPGTranslator

def main():
    app = QApplication(sys.argv)
    window = PDFToJPGTranslator()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
