import logging
from typing import Optional
from rich.console import Console
from rich.logging import RichHandler
from tqdm import tqdm

# Console pour l'affichage riche
console = Console()

# Progress bar globale
progress_bar: Optional[tqdm] = None

def init_progress():
    """Initialise la barre de progression globale."""
    global progress_bar
    if progress_bar:
        progress_bar.close()
    progress_bar = None

def update_progress(description: str, current: int, total: int):
    """Met à jour la barre de progression."""
    global progress_bar
    if progress_bar is None:
        progress_bar = tqdm(
            total=total,
            desc=description,
            unit="lignes",
            ncols=100,
            bar_format='{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]'
        )
    else:
        progress_bar.set_description(description)
        progress_bar.update(current - progress_bar.n)

def stop_progress():
    """Arrête la barre de progression."""
    global progress_bar
    if progress_bar:
        progress_bar.close()
        progress_bar = None

def setup_logging():
    """Configure le système de logging avec Rich."""
    # Configurer le handler Rich
    rich_handler = RichHandler(
        console=console,
        show_time=True,
        show_path=False,
        enable_link_path=False,
        markup=True,
        rich_tracebacks=True
    )
    
    # Configurer le formateur
    formatter = logging.Formatter("%(message)s")
    rich_handler.setFormatter(formatter)
    
    # Configurer le logger root
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Supprimer les handlers existants
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Ajouter le nouveau handler
    root_logger.addHandler(rich_handler) 