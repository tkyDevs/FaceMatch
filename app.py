from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout,
    QHBoxLayout, QSplitter, QFrame, QFileDialog, QLabel, QScrollArea
)
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
import sys
import os
import cv2
import numpy as np
from insightface.app import FaceAnalysis
from DLL import DoubleLinkedList
from clickLabel import ClickableLabel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.chosenFaces = []
        # INITIALIZING INSIGHTFACE APP
        self.app = FaceAnalysis(providers=['CPUExecutionProvider'])
        self.app.prepare(ctx_id=0)
        # WINDOW SETTINGS
        self.setWindowTitle("FaceMatch GUI - tkyDevs")
        self.setGeometry(100, 100, 1200, 800)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # BUTTONS
        btnImgFile = QPushButton('Choose Face')
        btnImgFile.setMinimumHeight(50)
        btnImgFile.setMaximumHeight(80)
        btnImgFile.clicked.connect(self.ChooseFace)
        btnFolder = QPushButton('Choose Folder')
        btnFolder.setMinimumHeight(50)
        btnFolder.setMaximumHeight(80)
        btnFolder.clicked.connect(self.ChooseFolder)

        # BUTTONS LAYOUT (Bottom)
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(btnImgFile)
        buttons_layout.addWidget(btnFolder)

        # SCROLL AREA
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)

        # Chosen Faces Frame inside Scroll Area
        self.chosenFacesWidget = QWidget()
        self.faces_layout = QVBoxLayout(self.chosenFacesWidget)
        self.scrollArea.setWidget(self.chosenFacesWidget)

        # RESULTS FRAME (For matched images)
        self.results = QFrame(self)
        self.results.setFrameShape(QFrame.StyledPanel)

        # SPLITTER (For Top Left & Top Right Frames)
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.scrollArea)
        splitter.addWidget(self.results)

        # MAIN LAYOUT
        main_layout = QVBoxLayout()
        main_layout.addWidget(splitter)
        main_layout.addLayout(buttons_layout)
        central_widget.setLayout(main_layout)

    def update(self):
        if self.faces_layout is None:
            self.faces_layout = QVBoxLayout()
            self.chosenFacesFrame.setLayout(self.faces_layout)
            
        while self.faces_layout.count():
            item = self.faces_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for index, img in enumerate(self.chosenFaces):
            if img is None:
                print("Error: Unable to load image.")
                continue

            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) # PyQt requires RGB format

            # Convert to QImage
            height, width, channel = img.shape
            bytes_per_line = 3 * width
            q_img = QImage(img.data, width, height, bytes_per_line, QImage.Format_RGB888)

            # Convert QImage to QPixmap
            pixmap = QPixmap.fromImage(q_img)

            # Resize image to fit the QLabel
            scaled_pixmap = pixmap.scaled(200, 200, aspectRatioMode=1)
            label = ClickableLabel(index)
            label.setPixmap(scaled_pixmap)
            label.clicked.connect(self.removeFace)

            self.faces_layout.addWidget(label)

    def removeFace(self, index):
        """Removes a face from chosenFaces and updates the UI."""
        if 0 <= index < len(self.chosenFaces):
            del self.chosenFaces[index]  # Remove the selected face
            self.update()  # Refresh the UI


    @pyqtSlot()
    def ChooseFolder(self):
        options = QFileDialog.Options()
        directory = QFileDialog.getExistingDirectory(self, "Select a Directory", "", options=options)

        if directory:  # Check if a directory was selected
            print(f"Selected Directory: {directory}")

            # Example: List all files in the directory
            files = os.listdir(directory)
            print("Files in the directory:", files)

    @pyqtSlot()
    def ChooseFace(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select an Image", "", "Images (*.png *.jpg *.jpeg *.bmp);;All Files (*)", options=options
        )
        if not file_path:
            print("No file selected.")
            return

        img = cv2.imread(file_path)
        if img is None:
            print("Error: Image could not be loaded.")
            return

        # Convert BGR to RGB for face detection
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        try:
            faces = self.app.get(img_rgb)
        except Exception as e:
            print(f"Error while detecting faces: {e}")
            return
        if not faces:
            print("No faces detected.")
            return

        for face in faces:
            x1, y1, x2, y2 = map(int, face.bbox)

            # Ensure bounding box is within image bounds
            h, w, _ = img_rgb.shape
            x1, y1, x2, y2 = max(0, x1), max(0, y1), min(w, x2), min(h, y2)

            cropped_face = img_rgb[y1:y2, x1:x2]
            self.chosenFaces.append(cropped_face)

        print(f"Stored {len(self.chosenFaces)} faces.")
        self.update()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
