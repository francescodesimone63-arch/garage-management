"""
Système de logging avancé pour le backend.
Permet le debugging efficace et le tracking des erreurs.
"""

import logging
import json
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
import sys


class DebugLogger:
    """Logger personnalisé avec support complet du debugging."""
    
    def __init__(self, name: str, log_file: Optional[str] = None):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Créer le répertoire logs s'il n'existe pas
        log_dir = Path(__file__).parent.parent.parent / "logs"
        log_dir.mkdir(exist_ok=True)
        
        # Format détaillé
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handler pour console (coloré)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # Handler pour fichier
        if log_file is None:
            log_file = "debug.log"
        
        file_handler = logging.FileHandler(log_dir / log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        self.log_file = log_dir / log_file
    
    def debug(self, message: str, **kwargs):
        """Log debug avec kwargs."""
        if kwargs:
            self.logger.debug(f"{message} | {json.dumps(kwargs, default=str, indent=2)}")
        else:
            self.logger.debug(message)
    
    def info(self, message: str, **kwargs):
        """Log info avec kwargs."""
        if kwargs:
            self.logger.info(f"{message} | {json.dumps(kwargs, default=str, indent=2)}")
        else:
            self.logger.info(message)
    
    def warning(self, message: str, **kwargs):
        """Log warning avec kwargs."""
        if kwargs:
            self.logger.warning(f"{message} | {json.dumps(kwargs, default=str, indent=2)}")
        else:
            self.logger.warning(message)
    
    def error(self, message: str, exception: Optional[Exception] = None, **kwargs):
        """Log erreur avec stack trace."""
        error_data = {
            "timestamp": datetime.now().isoformat(),
            "message": message,
            **kwargs
        }
        
        if exception:
            error_data["exception"] = str(exception)
            error_data["exception_type"] = type(exception).__name__
            error_data["traceback"] = traceback.format_exc()
            self.logger.error(
                f"{message}\n{json.dumps(error_data, default=str, indent=2)}",
                exc_info=True
            )
        else:
            self.logger.error(f"{message} | {json.dumps(error_data, default=str, indent=2)}")
    
    def critical(self, message: str, exception: Optional[Exception] = None, **kwargs):
        """Log critique avec stack trace."""
        error_data = {
            "timestamp": datetime.now().isoformat(),
            "message": message,
            **kwargs
        }
        
        if exception:
            error_data["exception"] = str(exception)
            error_data["exception_type"] = type(exception).__name__
            error_data["traceback"] = traceback.format_exc()
            self.logger.critical(
                f"{message}\n{json.dumps(error_data, default=str, indent=2)}",
                exc_info=True
            )
        else:
            self.logger.critical(f"{message} | {json.dumps(error_data, default=str, indent=2)}")
    
    def api_request(self, method: str, path: str, **kwargs):
        """Log une requête API."""
        request_data = {
            "method": method,
            "path": path,
            "timestamp": datetime.now().isoformat(),
            **kwargs
        }
        self.logger.info(f"📨 API REQUEST | {json.dumps(request_data, default=str, indent=2)}")
    
    def api_response(self, method: str, path: str, status_code: int, **kwargs):
        """Log une réponse API."""
        response_data = {
            "method": method,
            "path": path,
            "status_code": status_code,
            "timestamp": datetime.now().isoformat(),
            **kwargs
        }
        status_emoji = "✅" if 200 <= status_code < 300 else "⚠️" if status_code < 500 else "❌"
        self.logger.info(f"{status_emoji} API RESPONSE | {json.dumps(response_data, default=str, indent=2)}")
    
    def validation_error(self, field: str, error: str, **kwargs):
        """Log erreur de validation."""
        validation_data = {
            "field": field,
            "error": error,
            "timestamp": datetime.now().isoformat(),
            **kwargs
        }
        self.logger.warning(f"⚠️ VALIDATION ERROR | {json.dumps(validation_data, default=str, indent=2)}")
    
    def database_error(self, operation: str, table: str, exception: Exception, **kwargs):
        """Log erreur base de données."""
        db_error_data = {
            "operation": operation,
            "table": table,
            "exception": str(exception),
            "exception_type": type(exception).__name__,
            "timestamp": datetime.now().isoformat(),
            **kwargs
        }
        self.logger.error(f"🔴 DATABASE ERROR | {json.dumps(db_error_data, default=str, indent=2)}", exc_info=True)
    
    def get_last_logs(self, lines: int = 50) -> str:
        """Récupère les dernières lignes du fichier log."""
        try:
            with open(self.log_file, 'r') as f:
                all_lines = f.readlines()
                return ''.join(all_lines[-lines:])
        except Exception as e:
            return f"Errore: {e}"


# Instances globales pour utilisation rapide
main_logger = DebugLogger("garage_main")
vehicle_logger = DebugLogger("garage_vehicles", "vehicles.log")
customer_logger = DebugLogger("garage_customers", "customers.log")
work_order_logger = DebugLogger("garage_workorders", "workorders.log")
auth_logger = DebugLogger("garage_auth", "auth.log")
