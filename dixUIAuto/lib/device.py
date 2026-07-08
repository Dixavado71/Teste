"""
Device Manager - Gerenciamento de dispositivos Android
"""
import time
from typing import Optional, List
from lib.adb_bridge import ADBBridge
from lib.logs import logger
from lib.exceptions import DeviceNotFoundError, DeviceConnectionError


class Device:
    """Representa um dispositivo Android."""
    
    def __init__(self, device_id: str):
        self.device_id = device_id
        self.adb = ADBBridge(device_id)
        self.screen_width = 0
        self.screen_height = 0
        self._update_screen_size()
    
    def _update_screen_size(self):
        """Atualiza resolução da tela."""
        try:
            self.screen_width, self.screen_height = self.adb.get_screen_size()
        except Exception:
            self.screen_width, self.screen_height = 1080, 1920
    
    @property
    def center(self) -> tuple:
        return (self.screen_width // 2, self.screen_height // 2)
    
    def is_connected(self) -> bool:
        """Verifica se dispositivo está conectado."""
        devices = self.adb.get_devices()
        return self.device_id in devices
    
    def is_screen_on(self) -> bool:
        """Verifica se tela está ligada."""
        return self.adb.is_screen_on()
    
    def wake_up(self) -> bool:
        """Liga a tela."""
        return self.adb.wake_up()
    
    def unlock(self) -> bool:
        """Desbloqueia dispositivo."""
        if not self.is_screen_on():
            self.wake_up()
            time.sleep(0.5)
        return self.adb.unlock()
    
    def ensure_ready(self) -> bool:
        """Garante que dispositivo está pronto para uso."""
        if not self.is_connected():
            raise DeviceConnectionError(f"Dispositivo {self.device_id} não conectado")
        
        if not self.is_screen_on():
            self.wake_up()
            time.sleep(1)
        
        # Tentar desbloquear
        self.unlock()
        time.sleep(0.5)
        
        self._update_screen_size()
        return True


class DeviceManager:
    """Gerencia múltiplos dispositivos Android."""
    
    def __init__(self):
        self.log = logger.get_logger("Device")
        self._devices: dict[str, Device] = {}
        self._current_device: Optional[Device] = None
        self._adb = ADBBridge()
    
    def list_devices(self) -> List[str]:
        """Lista todos os dispositivos conectados."""
        return self._adb.get_devices()
    
    def connect_usb(self) -> Optional[Device]:
        """Conecta ao primeiro dispositivo USB disponível."""
        devices = self.list_devices()
        if not devices:
            raise DeviceNotFoundError("Nenhum dispositivo USB encontrado")
        
        device_id = devices[0]
        return self.select_device(device_id)
    
    def connect_tcp(self, host: str, port: int = 5555) -> Optional[Device]:
        """Conecta via TCP/IP."""
        self.log.info(f"Conectando a {host}:{port}...")
        
        if not self._adb.connect(host, port):
            raise DeviceConnectionError(f"Falha ao conectar em {host}:{port}")
        
        # Aguardar conexão estabelecer
        time.sleep(1)
        
        devices = self.list_devices()
        target = f"{host}:{port}"
        
        if target not in devices:
            raise DeviceConnectionError(f"Dispositivo {target} não apareceu na lista")
        
        return self.select_device(target)
    
    def select_device(self, device_id: str) -> Device:
        """Seleciona um dispositivo para uso."""
        if device_id in self._devices:
            self._current_device = self._devices[device_id]
        else:
            device = Device(device_id)
            self._devices[device_id] = device
            self._current_device = device
        
        self.log.success(f"Dispositivo selecionado: {device_id}")
        return self._current_device
    
    def get_current(self) -> Optional[Device]:
        """Retorna dispositivo atual."""
        return self._current_device
    
    def switch_device(self, device_id: str) -> Device:
        """Troca para outro dispositivo."""
        return self.select_device(device_id)
    
    def disconnect_all(self):
        """Desconecta todos os dispositivos TCP."""
        self._adb.disconnect()
        self._devices.clear()
        self._current_device = None
        self.log.info("Todos os dispositivos desconectados")
    
    def wait_for_device(self, timeout: int = 30) -> Device:
        """Aguarda até que um dispositivo esteja disponível."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            devices = self.list_devices()
            if devices:
                return self.connect_usb()
            time.sleep(1)
        
        raise DeviceNotFoundError(f"Nenhum dispositivo após {timeout}s")
