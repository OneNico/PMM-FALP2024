# src/config/logging_config.py

import logging
import os
from src.config.settings import LOG_DIR

def setup_logging():
    """
    Configura el sistema de logging para la aplicación.
    """
    log_file = os.path.join(LOG_DIR, 'app.log')
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
