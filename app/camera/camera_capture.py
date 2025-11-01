import cv2
import os

CAPTURE_DIR = "captures"
LAST_IMAGE = "last_capture.jpg"

class CameraCapture:
    def __init__(self):
        os.makedirs(CAPTURE_DIR, exist_ok=True)
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise RuntimeError("Caméra non détectée")

    def capture_image(self):
        ret, frame = self.cap.read()
        if not ret:
            raise RuntimeError("Impossible de lire la caméra")

        filepath = os.path.join(CAPTURE_DIR, LAST_IMAGE)
        cv2.imwrite(filepath, frame)
        print(f"Image enregistrée : {filepath}")
        return filepath

    def release(self):
        self.cap.release()

    def delete_last_image(self):
        filepath = os.path.join(CAPTURE_DIR, LAST_IMAGE)
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                print(f"Dernière image supprimée : {filepath}")
            except Exception as e:
                print(f"Erreur lors de la suppression de l'image : {e}")
