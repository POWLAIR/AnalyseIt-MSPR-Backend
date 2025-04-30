from sqlalchemy.orm import Session
from sqlalchemy import func, distinct, desc
from typing import List, Dict, Any
from ..db.models.base import Epidemic, DailyStats, Localisation

class StatsService:
    def __init__(self, db: Session):
        self.db = db

    def get_dashboard_stats(self) -> Dict[str, Any]:
        """
        Récupère toutes les statistiques pour le tableau de bord
        """
        return {
            "global_stats": self._get_global_stats(),
            "type_distribution": self._get_type_distribution(),
            "geographic_distribution": self._get_geographic_distribution(),
            "daily_evolution": self._get_daily_evolution(),
            "top_active_epidemics": self._get_top_active_epidemics()
        }

    def _get_global_stats(self) -> Dict[str, Any]:
        """
        Calcule les statistiques globales
        """
        # Récupérer les dernières statistiques quotidiennes
        latest_stats = self.db.query(
            func.sum(DailyStats.cases).label('total_cases'),
            func.sum(DailyStats.deaths).label('total_deaths')
        ).first()

        # Compter les épidémies
        total_epidemics = self.db.query(func.count(distinct(DailyStats.id_epidemic))).scalar()
        
        # Calculer le taux de mortalité
        total_cases = int(latest_stats.total_cases or 0)
        total_deaths = int(latest_stats.total_deaths or 0)
        mortality_rate = (total_deaths / total_cases * 100) if total_cases > 0 else 0

        return {
            "total_cases": total_cases,
            "total_deaths": total_deaths,
            "total_epidemics": total_epidemics,
            "active_epidemics": total_epidemics,  # Comme nous n'avons pas de flag actif/inactif
            "mortality_rate": float(mortality_rate)
        }

    def _get_type_distribution(self) -> List[Dict[str, Any]]:
        """
        Calcule la distribution par type d'épidémie
        """
        results = self.db.query(
            Epidemic.type,
            func.sum(DailyStats.cases).label('cases'),
            func.sum(DailyStats.deaths).label('deaths')
        ).join(
            DailyStats,
            DailyStats.id_epidemic == Epidemic.id
        ).group_by(Epidemic.type).all()

        return [
            {
                "type": result.type or "Non spécifié",
                "cases": int(result.cases or 0),
                "deaths": int(result.deaths or 0)
            }
            for result in results
        ]

    def _get_geographic_distribution(self) -> List[Dict[str, Any]]:
        """
        Calcule la distribution géographique des cas
        """
        results = self.db.query(
            Localisation.country,
            func.sum(DailyStats.cases).label('cases'),
            func.sum(DailyStats.deaths).label('deaths')
        ).join(
            DailyStats,
            DailyStats.id_loc == Localisation.id
        ).group_by(
            Localisation.country
        ).order_by(
            desc('cases')
        ).limit(10).all()

        return [
            {
                "country": result.country,
                "cases": int(result.cases or 0),
                "deaths": int(result.deaths or 0)
            }
            for result in results
        ]

    def _get_daily_evolution(self) -> List[Dict[str, Any]]:
        """
        Récupère l'évolution quotidienne des cas sur les 30 derniers jours
        """
        # Récupérer toutes les dates disponibles
        dates = self.db.query(
            DailyStats.date
        ).distinct().order_by(DailyStats.date.asc()).all()
        
        if not dates:
            return []

        results = self.db.query(
            DailyStats.date,
            func.sum(DailyStats.new_cases).label('new_cases'),
            func.sum(DailyStats.new_deaths).label('new_deaths'),
            func.sum(DailyStats.active).label('active_cases')
        ).group_by(
            DailyStats.date
        ).order_by(
            DailyStats.date.asc()
        ).all()

        return [
            {
                "date": result.date.isoformat(),
                "new_cases": int(result.new_cases or 0),
                "new_deaths": int(result.new_deaths or 0),
                "active_cases": int(result.active_cases or 0)
            }
            for result in results
        ]

    def _get_top_active_epidemics(self) -> List[Dict[str, Any]]:
        """
        Récupère les épidémies les plus importantes
        """
        # Sous-requête pour obtenir les totaux par épidémie
        epidemic_stats = self.db.query(
            DailyStats.id_epidemic,
            func.sum(DailyStats.cases).label('total_cases'),
            func.sum(DailyStats.deaths).label('total_deaths')
        ).group_by(
            DailyStats.id_epidemic
        ).subquery()

        results = self.db.query(
            Epidemic.id,
            Epidemic.name,
            Epidemic.type,
            Epidemic.country,
            epidemic_stats.c.total_cases,
            epidemic_stats.c.total_deaths
        ).join(
            epidemic_stats,
            epidemic_stats.c.id_epidemic == Epidemic.id
        ).order_by(
            desc(epidemic_stats.c.total_cases)
        ).limit(5).all()

        return [
            {
                "id": result.id,
                "name": result.name,
                "type": result.type or "Non spécifié",
                "country": result.country,
                "total_cases": int(result.total_cases or 0),
                "total_deaths": int(result.total_deaths or 0)
            }
            for result in results
        ] 