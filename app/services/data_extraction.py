import os
import pandas as pd
import logging
import glob
from time import sleep
import backoff
from sqlalchemy.orm import Session
from sqlalchemy import func
from kagglehub import dataset_download
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from typing import Dict, Any

from app.db.models.base import Epidemic, DailyStats, Localisation, DataSource, OverallStats
from app.utils.data_cleaning import clean_dataset

logger = logging.getLogger(__name__)

KAGGLE_DATASETS = {
    "mpox": "utkarshx27/mpox-monkeypox-data",
    "covid19": "josephassaker/covid19-global-dataset",
    "corona": "imdevskp/corona-virus-report",
}

@backoff.on_exception(backoff.expo, (SQLAlchemyError, OperationalError), max_tries=5)
def get_or_create_location(db: Session, location_data) -> int:
    try:
        if isinstance(location_data, str):
            location_name = location_data
            region = None
            iso_code = None
        else:
            location_name = (
                location_data.get("location", "Unknown")
                if hasattr(location_data, "get") else str(location_data)
            )
            region = (
                location_data.get("region") or location_data.get("state") or location_data.get("province")
                if hasattr(location_data, "get") else None
            )
            iso_code = (
                location_data.get("iso_code") or location_data.get("iso") or location_data.get("code")
                if hasattr(location_data, "get") else None
            )

        if pd.isna(location_name) or location_name.strip() == "":
            location_name = "Unknown"

        location = db.query(Localisation).filter_by(country=location_name).first()

        if not location:
            location = Localisation(
                country=location_name,
                region=region if pd.notna(region) else None,
                iso_code=iso_code if pd.notna(iso_code) else None
            )
            db.add(location)
            try:
                db.commit()
                db.refresh(location)
            except Exception as e:
                db.rollback()
                logger.error(f"Error creating location {location_name}: {e}")
                raise

        return location.id
    except Exception as e:
        logger.error(f"Error in get_or_create_location for {location_data}: {e}")
        raise

def get_csv_files_from_directory(dataset_path: str):
    return glob.glob(os.path.join(dataset_path, "**", "*.csv"), recursive=True)


def validate_stats_fields(stats: dict) -> bool:
    required_fields = ['id_epidemic', 'id_source', 'id_loc']
    for field in required_fields:
        if not stats.get(field):
            logger.error(f"{field} manquant dans les statistiques: {stats}")
            return False
    return True

@backoff.on_exception(backoff.expo, (SQLAlchemyError, OperationalError), max_tries=5)
def insert_or_update_single_stat(db: Session, stats: dict) -> bool:
    try:
        existing_stat = db.query(DailyStats).filter(
            DailyStats.id_epidemic == stats['id_epidemic'],
            DailyStats.id_loc == stats['id_loc'],
            DailyStats.date == stats['date']
        ).first()

        if existing_stat:
            for field, value in stats.items():
                setattr(existing_stat, field, value)
        else:
            db.add(DailyStats(**stats))

        db.commit()
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Erreur lors de l'insertion/update d'une stat: {e}")
        return False

@backoff.on_exception(backoff.expo, (SQLAlchemyError, OperationalError), max_tries=5)
def insert_or_update_stats(db: Session, daily_stats: list) -> int:
    processed = 0
    for stats in daily_stats:
        if not validate_stats_fields(stats):
            continue

        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            success = insert_or_update_single_stat(db, stats)
            if success:
                processed += 1
                break
            else:
                retry_count += 1
                if retry_count == max_retries:
                    logger.error(f"Échec après {max_retries} tentatives pour: {stats}")
                sleep(2 ** retry_count)

    return processed

@backoff.on_exception(backoff.expo, Exception, max_tries=5)
def process_generic_data(db: Session, data: pd.DataFrame, source_id: int, epidemic_name: str, reset: bool = False) -> None:
    try:
        epidemic = db.query(Epidemic).filter(Epidemic.name == epidemic_name).first()

        if not epidemic:
            epidemic = Epidemic(name=epidemic_name)
            db.add(epidemic)
            try:
                db.commit()
            except Exception as e:
                db.rollback()
                logger.error(f"Erreur lors de la création de l'épidémie: {e}")
                raise

        epidemic_id = epidemic.id

        if reset:
            try:
                db.query(DailyStats).filter(
                    DailyStats.id_epidemic == epidemic_id,
                    DailyStats.id_source == source_id
                ).delete()
                db.commit()
            except Exception as e:
                db.rollback()
                logger.error(f"Erreur lors de la suppression des anciennes données: {e}")
                raise

        daily_stats = []
        for _, row in data.iterrows():
            try:
                location_id = get_or_create_location(db, row['location'] if isinstance(row['location'], str) else row)
                if not location_id:
                    logger.error(f"Location non trouvée/créée pour: {row['location']}")
                    continue

                stats = {
                    'id_epidemic': epidemic_id,
                    'id_source': source_id,
                    'id_loc': location_id,
                    'date': row['date'],
                    'cases': row.get('cases', 0) if hasattr(row, 'get') else 0,
                    'deaths': row.get('deaths', 0) if hasattr(row, 'get') else 0,
                    'recovered': row.get('recovered', 0) if hasattr(row, 'get') else 0,
                    'active': row.get('active', 0) if hasattr(row, 'get') else 0,
                    'new_cases': row.get('new_cases', 0) if hasattr(row, 'get') else 0,
                    'new_deaths': row.get('new_deaths', 0) if hasattr(row, 'get') else 0,
                    'new_recovered': row.get('new_recovered', 0) if hasattr(row, 'get') else 0
                }
                daily_stats.append(stats)

            except Exception as e:
                logger.error(f"Erreur lors du traitement de la ligne: {e}")
                continue

        if daily_stats:
            processed = insert_or_update_stats(db, daily_stats)
            logger.info(f"Nombre d'enregistrements traités: {processed}")
        else:
            logger.warning("Aucune donnée à traiter")

    except Exception as e:
        logger.error(f"Erreur lors du traitement des données: {e}")
        raise

@backoff.on_exception(backoff.expo, (SQLAlchemyError, OperationalError), max_tries=5)
def calculate_overall_stats(db: Session):
    try:
        epidemics = db.query(Epidemic).all()
        for epidemic in epidemics:
            stats = db.query(
                func.sum(DailyStats.cases).label('total_cases'),
                func.sum(DailyStats.deaths).label('total_deaths')
            ).filter(DailyStats.id_epidemic == epidemic.id).first()

            if stats:
                total_cases = stats.total_cases or 0
                total_deaths = stats.total_deaths or 0
                fatality_ratio = (total_deaths / total_cases * 100) if total_cases > 0 else 0

                overall_stats = db.query(OverallStats).filter_by(id_epidemic=epidemic.id).first()
                if not overall_stats:
                    overall_stats = OverallStats(id_epidemic=epidemic.id)
                    db.add(overall_stats)

                overall_stats.total_cases = total_cases
                overall_stats.total_deaths = total_deaths
                overall_stats.fatality_ratio = fatality_ratio
                db.commit()
    except Exception as e:
        logger.error(f"Erreur stats globales: {e}")
        db.rollback()
        raise

def extract_and_load_datasets(db: Session):
    results = []
    max_retries = 3

    for name, path in KAGGLE_DATASETS.items():
        retry_count = 0
        while retry_count < max_retries:
            try:
                logger.info(f"Début du traitement du dataset {name} depuis {path}")
                dataset_path = dataset_download(path)
                logger.info(f"Téléchargement terminé pour {name} -> {dataset_path}")

                data_source = db.query(DataSource).filter_by(source_type=name).first()
                if not data_source:
                    logger.info(f"Création d'une nouvelle source de données pour {name}")
                    data_source = DataSource(
                        source_type=name,
                        reference=path,
                        url=f"https://www.kaggle.com/datasets/{path}"
                    )
                    db.add(data_source)
                    db.commit()
                    db.refresh(data_source)
                    logger.info(f"Source de données créée avec l'ID {data_source.id}")
                else:
                    logger.info(f"Source de données existante trouvée pour {name} (ID: {data_source.id})")

                csv_files = get_csv_files_from_directory(dataset_path)
                logger.info(f"{len(csv_files)} CSV trouvés pour {name}")

                if not csv_files:
                    logger.warning(f"Aucun fichier CSV trouvé pour {name}")
                    results.append({"dataset": name, "status": "warning", "message": "Aucun fichier CSV trouvé"})
                    break

                for file in csv_files:
                    file_retry_count = 0
                    while file_retry_count < max_retries:
                        try:
                            logger.info(f"Traitement du fichier {file}")
                            df = pd.read_csv(file)
                            logger.info(f"Fichier {file} lu avec succès, {len(df)} lignes")

                            df = clean_dataset(df, dataset_type=name, file_name=os.path.basename(file))
                            logger.info(f"Données nettoyées pour {file}")

                            process_generic_data(db, df, data_source.id, name, reset=False)
                            logger.info(f"Traitement terminé pour {file}: {len(df)} lignes traitées")

                            results.append({"dataset": name, "file": os.path.basename(file), "rows": len(df), "status": "success"})
                            break
                        except Exception as e:
                            file_retry_count += 1
                            if file_retry_count == max_retries:
                                logger.error(f"Erreur fichier {file} après {max_retries} tentatives: {e}")
                                results.append({"dataset": name, "file": os.path.basename(file), "error": str(e), "status": "error"})
                            else:
                                logger.warning(f"Tentative {file_retry_count}/{max_retries} échouée pour {file}: {e}")
                                sleep(2 ** file_retry_count)
                break
            except Exception as e:
                retry_count += 1
                if retry_count == max_retries:
                    logger.error(f"Erreur sur le dataset {name} après {max_retries} tentatives: {e}")
                    results.append({"dataset": name, "status": "error", "error": str(e)})
                else:
                    logger.warning(f"Tentative {retry_count}/{max_retries} échouée pour {name}: {e}")
                    sleep(2 ** retry_count)

    try:
        logger.info("Calcul des statistiques globales")
        calculate_overall_stats(db)
        logger.info("Statistiques globales calculées avec succès")
    except Exception as e:
        logger.error(f"Erreur lors du calcul des statistiques globales: {e}")
        results.append({"dataset": "overall_stats", "status": "error", "error": str(e)})

    return results

def run_etl(db: Session) -> Dict[str, Any]:
    """
    Exécute le processus ETL complet.
    """
    try:
        # Exemple de traitement ETL simple
        stats = {
            "processed_epidemics": db.query(Epidemic).count(),
            "processed_daily_stats": db.query(DailyStats).count(),
            "processed_locations": db.query(Localisation).count(),
            "processed_sources": db.query(DataSource).count()
        }
        return {"status": "success", "stats": stats}
    except Exception as e:
        return {"status": "error", "message": str(e)}
