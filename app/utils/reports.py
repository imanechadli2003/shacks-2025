from typing import Optional, Dict, List, Any
from .options import settings
import time

class Report:
    """Représente un rapport d'intrusion."""
    
    def __init__(self, report_id: str, pdf_path: str, content: Dict[str, Any]):
        self.id = report_id
        self.pdf_path = pdf_path
        self.content = content
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit le rapport en dictionnaire pour la sérialisation."""
        return {
            "id": self.id,
            "pdf_path": self.pdf_path,
            "content": self.content
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Report':
        """Crée un rapport depuis un dictionnaire."""
        return Report(
            report_id=data["id"],
            pdf_path=data["pdf_path"],
            content=data["content"]
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
    
    def add_report(self, pdf_path: str, content: Dict[str, Any]) -> Report:
        """
        Ajoute un nouveau rapport.
        
        Args:
            pdf_path: Chemin vers le fichier PDF du rapport
            content: Contenu JSON du rapport (données structurées)
        
        Returns:
            Le rapport créé avec son ID
        """
        report_id = self._generate_id()
        report = Report(report_id, pdf_path, content)
        
        # Récupérer la liste actuelle
        reports_data = self._get_reports_data()
        
        # Ajouter le nouveau rapport
        reports_data.append(report.to_dict())
        
        # Sauvegarder
        self._save_reports_data(reports_data)
        
        print(f"[ReportsManager] Rapport ajouté: {report_id}")
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