"""
Sistema di logging centralizzato per debugging avanzato
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime

# Directory per i log
LOG_DIR = Path(__file__).parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Formattazione dettagliata
DETAILED_FORMAT = logging.Formatter(
    '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

SIMPLE_FORMAT = logging.Formatter(
    '%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%H:%M:%S'
)


def setup_logging(app_name: str = "garage_management", level: str = "DEBUG"):
    """
    Configura il sistema di logging con file separati per livello
    """
    # Logger principale
    logger = logging.getLogger(app_name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Rimuovi handler esistenti
    logger.handlers = []
    
    # 1. FILE: Tutti i log (rotating, max 10MB, 5 backup)
    all_handler = RotatingFileHandler(
        LOG_DIR / f"{app_name}_all.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    all_handler.setLevel(logging.DEBUG)
    all_handler.setFormatter(DETAILED_FORMAT)
    logger.addHandler(all_handler)
    
    # 2. FILE: Solo errori
    error_handler = RotatingFileHandler(
        LOG_DIR / f"{app_name}_errors.log",
        maxBytes=10*1024*1024,
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(DETAILED_FORMAT)
    logger.addHandler(error_handler)
    
    # 3. FILE: API requests (separato)
    api_handler = RotatingFileHandler(
        LOG_DIR / f"{app_name}_api.log",
        maxBytes=10*1024*1024,
        backupCount=5,
        encoding='utf-8'
    )
    api_handler.setLevel(logging.INFO)
    api_handler.setFormatter(SIMPLE_FORMAT)
    logger.addHandler(api_handler)
    
    # 4. CONSOLE: Solo warning e superiori
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(SIMPLE_FORMAT)
    logger.addHandler(console_handler)
    
    # Log di avvio
    logger.info("="*80)
    logger.info(f"Sistema di logging inizializzato - {datetime.now()}")
    logger.info(f"Livello: {level.upper()}")
    logger.info(f"Directory log: {LOG_DIR}")
    logger.info("="*80)
    
    return logger


def get_logger(name: str):
    """Ottieni un logger per un modulo specifico"""
    return logging.getLogger(f"garage_management.{name}")


# Logger API per tracciare richieste
class APILogger:
    """Logger specializzato per richieste API"""
    
    def __init__(self):
        self.logger = get_logger("api")
    
    def log_request(self, method: str, path: str, user_id: int = None):
        """Log richiesta API"""
        user_info = f"User:{user_id}" if user_id else "Anonymous"
        self.logger.info(f"→ {method:6s} {path:50s} | {user_info}")
    
    def log_response(self, method: str, path: str, status: int, duration_ms: float):
        """Log risposta API"""
        level = self.logger.info if status < 400 else self.logger.error
        level(f"← {method:6s} {path:50s} | Status:{status} | {duration_ms:.2f}ms")
    
    def log_error(self, method: str, path: str, error: Exception):
        """Log errore API"""
        self.logger.error(
            f"✗ {method:6s} {path:50s} | ERROR: {type(error).__name__}: {str(error)}", 
            exc_info=True
        )


# Logger DB per tracciare query
class DBLogger:
    """Logger specializzato per operazioni database"""
    
    def __init__(self):
        self.logger = get_logger("database")
    
    def log_query(self, operation: str, table: str, filters: dict = None):
        """Log query database"""
        filter_str = f" | Filters:{filters}" if filters else ""
        self.logger.debug(f"DB {operation:8s} | Table:{table:20s}{filter_str}")
    
    def log_slow_query(self, query: str, duration_ms: float):
        """Log query lente (>1000ms)"""
        if duration_ms > 1000:
            self.logger.warning(f"SLOW QUERY ({duration_ms:.2f}ms): {query[:200]}")


# Istanze globali
api_logger = APILogger()
db_logger = DBLogger()
