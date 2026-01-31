"""
Configuration du logging avec rotation
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from config import LOG_CONFIG


def setup_logger(name: str = "tiktok_automation") -> logging.Logger:
    """
    Configurer le logger avec rotation de fichiers
    
    Args:
        name: Nom du logger
        
    Returns:
        Logger configuré
    """
    logger = logging.getLogger(name)
    logger.setLevel(LOG_CONFIG["level"])
    
    # Éviter les doublons de handlers
    if logger.handlers:
        return logger
    
    # Handler fichier avec rotation
    file_handler = RotatingFileHandler(
        LOG_CONFIG["file"],
        maxBytes=LOG_CONFIG["max_bytes"],
        backupCount=LOG_CONFIG["backup_count"],
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(LOG_CONFIG["format"])
    file_handler.setFormatter(file_formatter)
    
    # Handler console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    
    # Ajouter les handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
