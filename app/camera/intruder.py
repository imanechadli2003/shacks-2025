import cv2
import face_recognition

class Intruder:
    def __init__(self, reference_paths: list[str]):
        """
        Initialise le détecteur avec une liste de chemins d'images de référence.
        Chaque image doit contenir un visage autorisé.
        """
        self._reference_encodings = self.encode_references(reference_paths)

    def encode_references(self, reference_paths: list[str]):
        encodings = []
        for path in reference_paths:
            image = face_recognition.load_image_file(path)
            ref_encodings = face_recognition.face_encodings(image)
            if not ref_encodings:
                print(f"Aucun visage détecté dans l'image de référence : {path}")
                continue
            encodings.append(ref_encodings[0])
        if not encodings:
            raise ValueError("Aucun visage valide trouvé parmi les images de référence.")
        return encodings

    def is_intruder(self, path_frame: str, tolerance: float = 0.6) -> bool:
        """
        Path_frame : chemin vers l'image capturée.
        Tolerance : seuil de tolérance pour la comparaison des visages.
        Retourne True si c’est un intrus (aucune correspondance trouvée).
        """
        frame_image = cv2.imread(path_frame)
        if frame_image is None:
            raise FileNotFoundError(f"Impossible de charger l'image {path_frame}")
        rgb_frame = cv2.cvtColor(frame_image, cv2.COLOR_BGR2RGB)

        # Extraire les visages détectés dans la frame
        face_encodings = face_recognition.face_encodings(rgb_frame)
        if not face_encodings:
            print("⚠️ Aucun visage détecté dans l'image capturée.")
            return None  # pas de visage => pas considéré comme intrus

        # Vérifie si au moins un visage correspond à une référence connue
        for encoding in face_encodings:
            matches = face_recognition.compare_faces(self._reference_encodings, encoding, tolerance)
            if any(matches):
                return False  # une correspondance trouvée → pas un intrus

        # Aucun visage reconnu → intrus
        return True