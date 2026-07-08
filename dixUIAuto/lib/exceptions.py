"""
Exceções personalizadas do dixUIAuto
"""


class DixUIAutoError(Exception):
    """Exceção base para todos os erros do framework."""
    pass


class DeviceNotFoundError(DixUIAutoError):
    """Nenhum dispositivo Android encontrado."""
    pass


class DeviceConnectionError(DixUIAutoError):
    """Erro ao conectar com o dispositivo."""
    pass


class AppNotFoundError(DixUIAutoError):
    """Aplicativo não encontrado no dispositivo."""
    pass


class ElementNotFoundError(DixUIAutoError):
    """Elemento UI não encontrado."""
    
    def __init__(self, strategy: str, value: str, message: str = None):
        self.strategy = strategy
        self.value = value
        msg = message or f"Elemento não encontrado usando {strategy}='{value}'"
        super().__init__(msg)


class ElementNotVisibleError(DixUIAutoError):
    """Elemento existe mas não está visível."""
    pass


class ElementNotClickableError(DixUIAutoError):
    """Elemento não pode ser clicado."""
    pass


class TimeoutError(DixUIAutoError):
    """Tempo limite excedido para operação."""
    pass


class CacheError(DixUIAutoError):
    """Erro ao operar com cache."""
    pass


class ParseError(DixUIAutoError):
    """Erro ao fazer parse do XML."""
    pass


class FlowError(DixUIAutoError):
    """Erro na execução de fluxo."""
    pass


class ValidationError(DixUIAutoError):
    """Erro de validação."""
    pass


class ADBError(DixUIAutoError):
    """Erro em comando ADB."""
    
    def __init__(self, command: str, output: str = ""):
        self.command = command
        self.output = output
        super().__init__(f"Erro no comando ADB '{command}': {output}")


class InspectorError(DixUIAutoError):
    """Erro no módulo de inspeção."""
    pass
