import torch
import numpy as np
from PIL import Image

# Define a global variable to store the model
global_model = None

def load_model():
    global global_model
    if global_model is None:
        global_model = torch.hub.load('./yolov9', 'custom', path='yolov9_face_detection.pt', force_reload=True, source='local')
    return global_model

def detect_faces(image):
    # Load the YOLOv9 model for face detection
    model = load_model()

    # Set confidence threshold for detection
    model.conf = 0.5

    # Convert the image to numpy array
    image_np = np.array(image, dtype=np.uint8)

    # Convert numpy array back to PIL Image
    image_from_array = Image.fromarray(image_np)

    # Perform face detection
    results = model(image_from_array)

    # Get the bounding boxes of detected faces
    boxes = results.xyxy[0]

    # List to store cropped faces as numpy arrays
    cropped_faces = []

    # Crop and convert each detected face into numpy array
    for box in boxes:
        # Get coordinates of the bounding box
        x1, y1, x2, y2 = box[:4].tolist()

        # Crop the face region
        face_region = image_np[int(y1):int(y2), int(x1):int(x2)]

        # Append the cropped face to the list
        cropped_faces.append(face_region)

    return cropped_faces

# Load the model when the script is executed
load_model()
