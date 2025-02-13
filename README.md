# FaceMatch

## Overview
FaceMatch is a PyQt5-based desktop application that allows users to:
- Select a face from an image
- Choose a folder containing images
- Find and display photos that contain the selected face(s) using InsightFace's deep learning models.

The project uses InsightFace for face detection and similarity comparison, OpenCV for image processing, and a double-linked list (DLL) for efficient image navigation.

---

## Features
✅ **Face Selection** – Users can choose a face from an image to use for comparison.  
✅ **Folder Selection** – Users select a folder containing images to search through.  
✅ **Face Matching** – Uses InsightFace embeddings to find similar faces in the selected folder.  
✅ **Results Navigation** – View matched images with previous/next navigation buttons.  
✅ **Interactive UI** – PyQt5-based graphical interface with a scrollable area for selected faces.

---

## Installation
### 1. Clone the Repository
```sh
git clone https://github.com/tkyDevs/FaceMatch.git
cd FaceMatch
```

### 2. Create and Activate a Virtual Environment
```sh
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

### 3. Install Dependencies
```sh
pip install -r requirements.txt
```

### 4. Run the Application
```sh
python main.py
```

---

## Dependencies
- Python 3.8+
- PyQt5
- OpenCV
- NumPy
- InsightFace
- PIL (Pillow)

To install dependencies manually:
```sh
pip install PyQt5 opencv-python numpy insightface pillow
```

---

## Usage Guide
### **Step 1: Choose a Face**
- Click the "1. Choose Face" button.
- Select an image containing a face.
- The detected faces will be stored for comparison.
- You can click on the faces to remove them from the face matching process.

### **Step 2: Select a Folder**
- Click the "2. Choose Folder" button.
- Select a directory containing images to search.

### **Step 3: Find Matching Photos**
- Click the "3. Find Photos" button.
- The application will process images and find matching faces.
- Results will be displayed in the right panel.

### **Step 4: Navigate Through Matches**
- Use "Previous Image" and "Next Image" buttons to cycle through results.

---

## Troubleshooting
### **Face Not Detected?**
- Ensure the selected image has a clear, visible face.
- Try a higher resolution image for better detection.

### **No Matches Found?**
- Check if the folder contains images with faces.
- Adjust the similarity threshold in `findPhotos()`.

---

## Future Improvements
- Add GPU support for faster face recognition.
- Implement parallel processing for faster image search.
- Save and load previous face selections.
- Improve design elements.

---

## Contributing
Pull requests are welcome! If you find a bug or have a feature request, feel free to open an issue.

---

## License
MIT License. See [LICENSE](LICENSE) for details.

---

## Credits
Developed by **tkyDevs** using PyQt5, OpenCV, and InsightFace.
