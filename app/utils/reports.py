from typing import Optional, Dict, List, Any
from .settings import settings
import time
import shutil
import os
from pathlib import Path

class Report:
    """Représente un rapport d'intrusion."""

    def __init__(
        self,
        report_id: str,
        pdf_path: str,
        json_summary_path: str,
        intruder_image_path: Optional[str] = None,
        html_report_path: Optional[str] = None,
    ):
        self.id = report_id
        self.pdf_path = pdf_path
        self.json_summary_path = json_summary_path
        self.intruder_image_path = intruder_image_path
        self.html_report_path = html_report_path

    def to_dict(self) -> Dict[str, Any]:
        """Convertit le rapport en dictionnaire pour la sérialisation."""
        return {
            "id": self.id,
            "pdf_path": self.pdf_path,
            "json_summary_path": self.json_summary_path,
            "intruder_image_path": self.intruder_image_path,
            "html_report_path": self.html_report_path,
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Report':
        """Crée un rapport depuis un dictionnaire."""
        return Report(
            report_id=data["id"],
            pdf_path=data["pdf_path"],
            json_summary_path=data["json_summary_path"],
            intruder_image_path=data.get("intruder_image_path"),
            html_report_path=data.get("html_report_path"),
        )


class ReportsManager:
    """Gestionnaire des rapports d'intrusion."""
    
    REPORTS_KEY = "intrusion_reports"
    
    def __init__(self):
        self._ensure_reports_list()
    
    def _ensure_reports_list(self):
        """S'assure que la liste des rapports existe dans les paramètres."""
        if settings.get(self.REPORTS_KEY) is None:
            settings.set(self.REPORTS_KEY, [])
    
    def _get_reports_data(self) -> List[Dict[str, Any]]:
        """Récupère les données brutes des rapports depuis les paramètres."""
        return settings.get(self.REPORTS_KEY, [])
    
    def _save_reports_data(self, reports_data: List[Dict[str, Any]]):
        """Sauvegarde les données des rapports dans les paramètres."""
        settings.set(self.REPORTS_KEY, reports_data)
    
    def _generate_id(self) -> str:
        """Génère un ID unique pour un nouveau rapport."""
        timestamp = int(time.time() * 1000)  # milliseconds
        return f"report_{timestamp}"

    def add_report(self, pdf_path: str, json_summary_path: str) -> Report:
        """
        Ajoute un nouveau rapport.
        
        Args:
            pdf_path: Chemin vers le fichier PDF du rapport
            json_summary_path: Chemin vers le fichier JSON du rapport
        
        Returns:
            Le rapport créé avec son ID
        """
        report_id = self._generate_id()
        # Structure de sortie: reports/{id}/report.pdf et reports/{id}/report.json
        base_dir = Path("reports")
        report_dir = base_dir / report_id
        report_dir.mkdir(parents=True, exist_ok=True)

        # Chemins cibles normalisés
        new_pdf_path = report_dir / "report.pdf"
        new_json_path = report_dir / "report.json"

        # Copier les fichiers sources vers la nouvelle structure
        shutil.copy2(pdf_path, new_pdf_path)
        shutil.copy2(json_summary_path, new_json_path)

        # Copier la dernière capture d'intrus si disponible
        intruder_src = Path("captures") / "last_capture.jpg"
        intruder_dst = report_dir / "intruder.jpg"
        try:
            if intruder_src.exists():
                shutil.copy2(intruder_src, intruder_dst)
                print(f"[ReportsManager] Image intrus copiée vers: {intruder_dst}")
            else:
                print(f"[ReportsManager] Avertissement: {intruder_src} introuvable, aucune image intrus copiée")
        except Exception as e:
            print(f"[ReportsManager] Erreur lors de la copie de l'image intrus: {e}")

        # Déterminer le chemin de l'image d'intrus si elle a été copiée
        intruder_image_path = str(intruder_dst) if intruder_dst.exists() else None

        # Copier le fichier HTML de replay si disponible (rapport.html à la racine)
        html_src = Path("rapport.html")
        html_dst = report_dir / "rapport.html"
        html_report_path: Optional[str] = None
        try:
            if html_src.exists():
                shutil.copy2(html_src, html_dst)
                # Adapter les chemins des screenshots pour un accès relatif depuis le dossier du rapport
                try:
                    content = html_dst.read_text(encoding="utf-8")
                    content = content.replace("tracking/screenshots", "../../tracking/screenshots")
                    html_dst.write_text(content, encoding="utf-8")
                except Exception as e:
                    print(f"[ReportsManager] Erreur lors de l'adaptation des chemins dans le HTML: {e}")

                html_report_path = str(html_dst)
                print(f"[ReportsManager] HTML du rapport copié vers: {html_dst} (chemins screenshots réécrits -> '../../tracking/screenshots')")
            else:
                print(f"[ReportsManager] Avertissement: {html_src} introuvable, aucun HTML copié")
        except Exception as e:
            print(f"[ReportsManager] Erreur lors de la copie du HTML du rapport: {e}")

        # Créer le rapport avec les nouveaux chemins
        report = Report(report_id, str(new_pdf_path), str(new_json_path), intruder_image_path, html_report_path)
        
        # Récupérer la liste actuelle
        reports_data = self._get_reports_data()
        
        # Ajouter le nouveau rapport
        reports_data.append(report.to_dict())
        
        # Sauvegarder
        self._save_reports_data(reports_data)
        
        print(f"[ReportsManager] Rapport ajouté: {report_id}")
        print(f"[ReportsManager] PDF copié vers: {new_pdf_path}")
        print(f"[ReportsManager] JSON copié vers: {new_json_path}")
        return report
    
    def remove_report(self, report_id: str) -> bool:
        """
        Supprime un rapport par son ID.
        
        Args:
            report_id: L'ID du rapport à supprimer
        
        Returns:
            True si le rapport a été supprimé, False s'il n'existait pas
        """
        reports_data = self._get_reports_data()
        
        # Filtrer pour supprimer le rapport
        initial_count = len(reports_data)
        reports_data = [r for r in reports_data if r.get("id") != report_id]
        
        if len(reports_data) < initial_count:
            self._save_reports_data(reports_data)
            print(f"[ReportsManager] Rapport supprimé: {report_id}")
            return True
        
        print(f"[ReportsManager] Rapport non trouvé: {report_id}")
        return False
    
    def get_report(self, report_id: str) -> Optional[Report]:
        """
        Récupère un rapport spécifique par son ID.
        
        Args:
            report_id: L'ID du rapport à récupérer
        
        Returns:
            Le rapport trouvé ou None
        """
        reports_data = self._get_reports_data()
        
        for data in reports_data:
            if data.get("id") == report_id:
                return Report.from_dict(data)
        
        return None
    
    def get_all_reports(self) -> List[Report]:
        """
        Récupère la liste complète des rapports.
        
        Returns:
            Liste de tous les rapports sauvegardés
        """
        reports_data = self._get_reports_data()
        return [Report.from_dict(data) for data in reports_data]
    
    def clear_all_reports(self):
        """Supprime tous les rapports (utile pour le nettoyage)."""
        self._save_reports_data([])
        print("[ReportsManager] Tous les rapports ont été supprimés")


# Instance globale du gestionnaire
reports_manager = ReportsManager()