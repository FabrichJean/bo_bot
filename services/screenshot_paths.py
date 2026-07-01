import os
from datetime import datetime

from config import SCREENSHOT_ROOT_DIR


def get_screenshot_path(user, status_type, timestamp=None):
    """
    Génère le chemin de screenshot avec la structure: screenshots/{user}/{active|inactive}/{timestamp}.png
    Args:
        user: Nom d'utilisateur
        status_type: 'active' ou 'inactive'
        timestamp: Timestamp optionnel (par défaut: datetime actuel)
    Returns:
        str: Chemin complet du fichier screenshot
    """
    if timestamp is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Créer le chemin complet
    screenshot_dir = os.path.join(SCREENSHOT_ROOT_DIR, user, status_type)

    # Créer les dossiers s'ils n'existent pas
    os.makedirs(screenshot_dir, exist_ok=True)

    # Construire le chemin complet du fichier
    filename = f"{timestamp}.png"
    full_path = os.path.join(screenshot_dir, filename)

    return full_path
