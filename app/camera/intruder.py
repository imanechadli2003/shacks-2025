import cv2
import face_recognition

class Intruder:
    def __init__(self, path_reference: str):
        self._reference_encoding = self.encode_reference(path_reference)

    def encode_reference(self, path_reference: str):
        reference_image = face_recognition.load_image_file(path_reference)
        ref_encodings = face_recognition.face_encodings(reference_image)
        if not ref_encodings:
            raise ValueError("Aucun visage détecté dans l’image de référence.")
        return ref_encodings[0]

    def is_intruder(self, path_frame: str, tolerance: float = 0.6) -> bool:
        """
        Path_frame: chemin vers l'image capturée.
        Tolerance: seuil de tolérance pour la comparaison des visages.
        Retourne True si c’est un intrus (autre personne ou aucun visage reconnu).
        """
        # Charger l'image capturée
        frame_image = cv2.imread(path_frame)
        if frame_image is None:
            raise FileNotFoundError(f"Impossible de charger l'image {path_frame}")
        rgb_frame = cv2.cvtColor(frame_image, cv2.COLOR_BGR2RGB)

        # Extraire les visages détectés dans la frame
        face_encodings = face_recognition.face_encodings(rgb_frame)
        if not face_encodings:
            print ("Pas de visage détecté.")
            return False  # aucun visage => pas considéré comme intrus

        # Comparer le premier visage détecté
        match = face_recognition.compare_faces([self._reference_encoding], face_encodings[0], tolerance)[0]
        return not match  # True si c’est un intrus