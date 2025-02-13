from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout,
    QHBoxLayout, QSplitter, QFrame, QFileDialog, QLabel, QScrollArea, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
import sys
import os
import glob
import cv2
import numpy as np
from pathlib import Path
from PIL import Image
from insightface.app import FaceAnalysis
from DLL import DoubleLinkedList
from clickLabel import ClickableLabel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.DLL = DoubleLinkedList()
        self.current = None
        self.chosenFaces = []
        self.chosenFacesEmbedding = []
        self.chosenFolderPath = None
        # INITIALIZING INSIGHTFACE APP
        self.app = FaceAnalysis(providers=['CPUExecutionProvider'])
        self.app.prepare(ctx_id=0)
        
        # WINDOW SETTINGS
        self.setWindowTitle("FaceMatch GUI - tkyDevs")
        self.setGeometry(100, 100, 1200, 800)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.pixmap = QPixmap("empty.jpg")
        
        def btnCustomize(btn, function, minHeight=50, maxHeight=80):
            btn.setCursor(Qt.PointingHandCursor)
            btn.setMinimumHeight(minHeight)
            btn.setMaximumHeight(maxHeight)
            btn.clicked.connect(function)

        # BUTTONS
        btnImgFile = QPushButton('1. Choose Face')
        btnCustomize(btnImgFile, self.ChooseFace)
        btnFolder = QPushButton('2. Choose Folder')
        btnCustomize(btnFolder, self.ChooseFolder)
        
        btnFindPhotos = QPushButton('3. Find Photos')
        btnCustomize(btnFindPhotos, self.findPhotos)
        
        # PREVIOUS/NEXT BUTTONS
        btnPrevPhoto = QPushButton('Previous Image')
        btnCustomize(btnPrevPhoto, self.prevImg)
        btnNextPhoto = QPushButton('Next Image')
        btnCustomize(btnNextPhoto, self.nextImg)
        prevNext_layout = QHBoxLayout()
        prevNext_layout.addWidget(btnPrevPhoto)
        prevNext_layout.addWidget(btnNextPhoto)

        # BUTTONS LAYOUT (Bottom)
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(btnImgFile)
        buttons_layout.addWidget(btnFolder)
        buttons_layout.addWidget(btnFindPhotos)

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
        self.results.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.test = QLabel(self.results)
        self.test.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.test.setAlignment(Qt.AlignCenter)
        scaled_pixmap = self.pixmap.scaled(500, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.test.setPixmap(scaled_pixmap)
        self.test.setScaledContents(True)
        layout = QVBoxLayout(self.results)
        layout.addWidget(self.test)
        self.results.setLayout(layout)

        # RESULTS LAYOUT (Frame + Prev/Next Buttons)
        results_layout = QVBoxLayout()
        results_layout.addWidget(self.results)
        results_layout.addLayout(prevNext_layout)
        # WRAP `results_layout` IN A QWidget
        results_widget = QWidget()
        results_widget.setLayout(results_layout)

        # SPLITTER (For Top Left & Top Right Frames)
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.scrollArea)
        splitter.addWidget(results_widget)

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

            height, width, channel = img.shape
            bytes_per_line = 3 * width
            q_img = QImage(img.data, width, height, bytes_per_line, QImage.Format_RGB888)

            pixmap = QPixmap.fromImage(q_img)

            scaled_pixmap = pixmap.scaled(200, 200, aspectRatioMode=1)
            label = ClickableLabel(index)
            label.setPixmap(scaled_pixmap)
            label.clicked.connect(self.removeFace)

            self.faces_layout.addWidget(label)

    def removeFace(self, index):
        if 0 <= index < len(self.chosenFaces):
            del self.chosenFaces[index]
            del self.chosenFacesEmbedding[index]
            self.update()
            
    def get_faces(self, image):
        faces = self.app.get(image)
        return faces
    
    @pyqtSlot()
    def findPhotos(self):
        if not self.chosenFacesEmbedding:
            print('No face embedding to compare. Try using the "Choose Face" button.')
            return
        elif not self.chosenFolderPath:
            print('No directory selected to compare. Try using the "Choose Folder" button.')
            return

        directory_path = Path(self.chosenFolderPath).resolve()
        allowed_extensions = {".jpg", ".jpeg", ".png"}

        if not directory_path.exists() or not directory_path.is_dir():
            print(f"Error: Directory '{directory_path}' does not exist or is not a folder.")
            return

        for file_path in directory_path.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in allowed_extensions:
                print(f"Processing: {file_path}")
                image = cv2.imread(str(file_path))
                if image is not None:
                    print("Loaded image successfully.")
                else:
                    print(f"Error: Failed to load image {file_path}")

                faces_in_image = self.get_faces(image)
                if not faces_in_image:
                    print(f"No faces detected in {file_path}. Skipping...")
                    continue
                print('Face embeddings loaded.')
                counter = 0
                for index in range(len(self.chosenFacesEmbedding)):
                    if counter < index: # 1 of the faces was not found so go to next image.
                        break
                    for foundFace in faces_in_image:
                        embedding1 = self.chosenFacesEmbedding[index].normed_embedding
                        embedding2 = foundFace.normed_embedding
                        similarity = np.dot(embedding1, embedding2)
                        threshold = 0.5
                        if similarity > threshold:
                            counter += 1
                            break
                        else:
                            pass
                if counter == len(self.chosenFacesEmbedding):
                    self.DLL.append(str(file_path))
                    print("Face added to DLL.")
        
        if self.DLL.head:
            self.current = self.DLL.head
            self.pixmap = QPixmap(self.current.path)
            self.update()
        else:
            print("Error: No images added to the DLL.")


    @pyqtSlot()
    def ChooseFolder(self):
        options = QFileDialog.Options()
        directory = QFileDialog.getExistingDirectory(self, "Select a Directory", "", options=options)

        if directory:
            print(f"Selected Directory: {directory}")
            image_extensions = ["*.png", "*.jpg", "*.jpeg", "*.bmp", "*.gif", "*.tiff"]

            image_found = any(glob.glob(os.path.join(directory, ext)) for ext in image_extensions)
            if image_found:
                self.chosenFolderPath = directory
                return
            else:
                return

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

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        try:
            faces = self.get_faces(img_rgb)
            if faces:
                for i in faces:
                    self.chosenFacesEmbedding.append(i)
        except Exception as e:
            print(f"Error while detecting faces: {e}")
            return
        if not faces:
            print("No faces detected.")
            return

        for face in faces:
            x1, y1, x2, y2 = map(int, face.bbox)
            h, w, _ = img_rgb.shape
            cropped_face = img_rgb[y1:y2, x1:x2]
            self.chosenFaces.append(cropped_face)

        print(f"Stored {len(self.chosenFaces)} faces.")
        self.update()
        
    def prevImg(self):
        if self.current and self.current.prev:
            print('prev btn')
            self.current = self.current.prev
            print(f"Prev image: {self.current.path}")
            new_pixmap = QPixmap(self.current.path)
            if new_pixmap.isNull():
                print("Failed to load image:", self.current.path)
            else:
                print("Loaded image:", self.current.path)
                self.test.setPixmap(new_pixmap.scaled(500, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                self.test.repaint()

    
    def nextImg(self):
        if self.current and self.current.next:
            print('next btn')
            self.current = self.current.next
            print(f"Next image: {self.current.path}")
            new_pixmap = QPixmap(self.current.path)
            if new_pixmap.isNull():
                print("Failed to load image:", self.current.path)
            else:
                print("Loaded image:", self.current.path)
                self.test.setPixmap(new_pixmap.scaled(500, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                self.test.repaint()



def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
