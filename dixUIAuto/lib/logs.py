"""
Sistema de Logging do dixUIAuto
"""
import logging
import os
from config.settings import LOG_LEVEL, LOG_FORMAT, LOG_FILE


class DixLogger:
    """Gerenciador de logs centralizado."""
    
    _instance = None
    _logger = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._logger is None:
            self._setup_logger()
    
    def _setup_logger(self):
        """Configura o logger principal."""
        self._logger = logging.getLogger("dixUIAuto")
        self._logger.setLevel(getattr(logging, LOG_LEVEL.upper()))
        
        # Limpar handlers existentes
        self._logger.handlers.clear()
        
        # Handler para arquivo
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(LOG_FORMAT)
        file_handler.setFormatter(file_formatter)
        
        # Handler para console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, LOG_LEVEL.upper()))
        console_formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%H:%M:%S"
        )
        console_handler.setFormatter(console_formatter)
        
        self._logger.addHandler(file_handler)
        self._logger.addHandler(console_handler)
    
    def get_logger(self, name: str = None) -> logging.Logger:
        """Retorna um logger com nome específico."""
        if name:
            logger = logging.getLogger(f"dixUIAuto.{name}")
            logger.handlers = self._logger.handlers.copy()
            return logger
        return self._logger
    
    def debug(self, message: str, **kwargs):
        self._logger.debug(message, **kwargs)
    
    def info(self, message: str, **kwargs):
        self._logger.info(message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        self._logger.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs):
        self._logger.error(message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        self._logger.critical(message, **kwargs)
    
    def success(self, message: str, **kwargs):
        """Log de sucesso customizado."""
        self._logger.info(f"✓ {message}", **kwargs)


# Logger global
logger = DixLogger()
