import sys
from tkinter import Image
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, QFileDialog, QVBoxLayout, QWidget, QStatusBar, QMessageBox, QProgressBar
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
import fitz
from app.pdf_converter import convert_pdf_to_images
from app.translation_thread import TranslationThread
import os
import zipfile

class PDFToJPGTranslator(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PDF a JPG y Traductor")
        self.setGeometry(100, 100, 400, 300)
        self.setStyleSheet("background-color: #f0f0f0;")

        self.pdf_path = None
        self.jpg_path = None

        main_layout = QVBoxLayout()

        self.label = QLabel("Seleccione un archivo PDF:", self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.btn_select_pdf = QPushButton("Seleccionar Archivo PDF", self)
        self.btn_select_pdf.setIcon(QIcon("icons/select_pdf.png"))
        self.btn_select_pdf.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px;")
        self.btn_select_pdf.clicked.connect(self.select_pdf)

        self.btn_export = QPushButton("Exportar Archivo", self)
        self.btn_export.setIcon(QIcon("icons/translate.png"))
        self.btn_export.setStyleSheet("background-color: #FF5722; color: white; padding: 10px;")
        self.btn_export.clicked.connect(self.export_file)

        # Barra de progreso
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_bar.hide()  # Ocultar inicialmente

        # Etiqueta de tiempo estimado
        self.time_label = QLabel("Tiempo estimado: --", self)
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.hide()  # Ocultar inicialmente

        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)

        main_layout.addWidget(self.label)
        main_layout.addWidget(self.btn_select_pdf)
        main_layout.addWidget(self.btn_export)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.time_label)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def select_pdf(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Seleccionar PDF", "", "Archivos PDF (*.pdf)")
        if file_name:
            self.pdf_path = file_name
            self.label.setText(f"PDF seleccionado: {file_name}")
            self.show_progress("Convirtiendo PDF a JPG...")
            self.convert_pdf_to_jpg()

    def convert_pdf_to_jpg(self):
        if not self.pdf_path:
            return

        doc = fitz.open(self.pdf_path)
        total_pages = len(doc)
        self.progress_bar.setMaximum(total_pages)
        self.progress_bar.setValue(0)

        # Estimar tiempo (1 segundo por página como ejemplo)
        estimated_time = total_pages * 1
        self.time_label.setText(f"Tiempo estimado: {estimated_time} segundos")
        self.time_label.show()

        temp_dir = "temp_images"
        os.makedirs(temp_dir, exist_ok=True)
        image_paths = []

        for page_num, page in enumerate(doc):
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            image_path = os.path.join(temp_dir, f"page_{page_num + 1}.jpg")
            img.save(image_path, "JPEG")
            image_paths.append(image_path)

            # Actualizar progreso
            self.progress_bar.setValue(page_num + 1)
            QApplication.processEvents()  # Actualizar la interfaz

        zip_path, _ = QFileDialog.getSaveFileName(self, "Guardar como ZIP", "", "Archivos ZIP (*.zip)")
        if zip_path:
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for image_path in image_paths:
                    zipf.write(image_path, os.path.basename(image_path))
            self.status_bar.showMessage(f"Archivo ZIP guardado en {zip_path}", 5000)

        # Limpiar archivos temporales
        for image_path in image_paths:
            os.remove(image_path)
        os.rmdir(temp_dir)

        self.hide_progress()

    def export_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Seleccionar Imagen JPG", "", "Archivos JPG (*.jpg)")
        if not file_name:
            self.status_bar.showMessage("Debe seleccionar un archivo JPG", 5000)
            return

        # Obtener la ruta de guardado en el hilo principal
        save_path, _ = QFileDialog.getSaveFileName(self, "Guardar imagen traducida como", "", "Archivos JPG (*.jpg)")
        if not save_path:
            self.status_bar.showMessage("Guardado cancelado", 5000)
            return

        # Mostrar barra de progreso y tiempo estimado
        self.show_progress("Traduciendo y guardando imagen...")
        self.time_label.setText("Tiempo estimado: 5-10 segundos")  # Estimación aproximada
        self.time_label.show()

        # Crear y ejecutar el hilo de traducción
        self.translation_thread = TranslationThread(file_name, save_path)
        self.translation_thread.finished.connect(self.on_translation_finished)
        self.translation_thread.error.connect(self.on_translation_error)
        self.translation_thread.progress.connect(self.progress_bar.setValue)
        self.translation_thread.start()

    def on_translation_finished(self, message):
        self.status_bar.showMessage(message, 5000)
        self.hide_progress()

    def on_translation_error(self, error_message):
        QMessageBox.critical(self, "Error", error_message)
        self.hide_progress()

    def show_progress(self, message):
        """Muestra la barra de progreso y el mensaje."""
        self.status_bar.showMessage(message)
        self.progress_bar.show()
        self.time_label.show()
        self.btn_select_pdf.setEnabled(False)
        self.btn_export.setEnabled(False)

    def hide_progress(self):
        """Oculta la barra de progreso y restaura la interfaz."""
        self.progress_bar.hide()
        self.time_label.hide()
        self.btn_select_pdf.setEnabled(True)
        self.btn_export.setEnabled(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PDFToJPGTranslator()
    window.show()
    sys.exit(app.exec())
