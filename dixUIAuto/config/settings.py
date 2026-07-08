"""
Configurações Globais do dixUIAuto
"""
import os

# Diretórios base
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGS_DIR = os.path.join(BASE_DIR, "logs")
DUMPS_DIR = os.path.join(BASE_DIR, "dumps")
CACHE_DIR = os.path.join(BASE_DIR, "cache")
SCREENSHOTS_DIR = os.path.join(BASE_DIR, "screenshots")
FLOWS_DIR = os.path.join(BASE_DIR, "flows")

# Criar diretórios se não existirem
for directory in [LOGS_DIR, DUMPS_DIR, CACHE_DIR, SCREENSHOTS_DIR, FLOWS_DIR]:
    os.makedirs(directory, exist_ok=True)

# Configurações ADB
ADB_HOST = "127.0.0.1"
ADB_PORT = 5037
ADB_TIMEOUT = 30
ADB_RETRY_ATTEMPTS = 3

# Configurações de Cache
CACHE_ENABLED = True
CACHE_TTL = 300  # segundos
CACHE_MAX_SIZE = 100

# Configurações de Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = os.path.join(LOGS_DIR, "dixuiauto.log")

# Configurações de Timeout
DEFAULT_TIMEOUT = 10
ELEMENT_POLL_INTERVAL = 0.5
SCREEN_CHANGE_THRESHOLD = 0.95

# Configurações do Inspector
INSPECTOR_HIGHLIGHT_COLOR = "#FF0000"
INSPECTOR_HIGHLIGHT_DURATION = 2.0

# Configurações de Smart Form
FORM_FILL_DELAY = 0.3
FORM_VALIDATION_ENABLED = True
