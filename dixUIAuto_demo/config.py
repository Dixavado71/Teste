"""
Configurações do projeto demo dixUIAuto
"""

# Package do aplicativo a ser testado (exemplo)
APP_PACKAGE = "com.example.app"

# Activity inicial (opcional, se None tenta detectar automaticamente)
APP_ACTIVITY = None

# ID do dispositivo (None usa o primeiro disponível)
# Ex: DEVICE_ID = "emulator-5554" ou DEVICE_ID = "192.168.1.100:5555"
DEVICE_ID = None

# Timeout padrão em segundos para operações
DEFAULT_TIMEOUT = 10

# Timeout para espera de elementos
ELEMENT_WAIT_TIMEOUT = 5

# Habilitar logs detalhados
DEBUG_MODE = True

# Diretório para screenshots
SCREENSHOT_DIR = "screenshots"

# Diretório para fluxos JSON
FLOWS_DIR = "flows"

# Habilitar cache de UI
ENABLE_CACHE = True

# Intervalo de refresh do watcher (segundos)
WATCHER_INTERVAL = 0.5

# Número máximo de tentativas para ações
MAX_RETRIES = 3

# Delay entre ações (segundos)
ACTION_DELAY = 0.3
