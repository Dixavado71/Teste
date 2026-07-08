"""
dixUIAuto - Framework de Automação Android
Engine Central que coordena todos os módulos
"""
import time
from typing import Optional, List, Dict
from lib.device import DeviceManager, Device
from lib.adb_bridge import ADBBridge
from lib.dumper import Dumper
from lib.finder import Finder
from lib.locator import Locator
from lib.clicker import Clicker
from lib.keyboard import Keyboard
from lib.gestures import Gestures
from lib.watcher import UIWatcher
from lib.validator import Validator
from lib.form import SmartForm
from lib.flow import FlowEngine
from lib.logs import logger
from lib.exceptions import DixUIAutoError


class DixEngine:
    """
    Engine principal do dixUIAuto.
    
    Exemplo de uso:
        engine = DixEngine()
        engine.connect()
        engine.open("com.app.package")
        engine.click(text="Entrar")
        engine.form.fill(label="CPF", value="02959350146")
    """
    
    def __init__(self):
        self.log = logger.get_logger("Engine")
        self.device_manager = DeviceManager()
        self.device: Optional[Device] = None
        self.adb: Optional[ADBBridge] = None
        self.dumper: Optional[Dumper] = None
        self.finder: Optional[Finder] = None
        self.locator: Optional[Locator] = None
        self.clicker: Optional[Clicker] = None
        self.keyboard: Optional[Keyboard] = None
        self.gestures: Optional[Gestures] = None
        self.watcher: Optional[UIWatcher] = None
        self.validator: Optional[Validator] = None
        self.form: Optional[SmartForm] = None
        self.flow: Optional[FlowEngine] = None
        self._initialized = False
    
    def connect(self, device_id: str = None, tcp_host: str = None, 
                tcp_port: int = 5555) -> 'DixEngine':
        """
        Conecta ao dispositivo Android.
        
        Args:
            device_id: ID do dispositivo (USB ou TCP)
            tcp_host: Host para conexão TCP/IP
            tcp_port: Porta para conexão TCP/IP
        
        Returns:
            Self para chaining
        """
        self.log.info("Iniciando conexão...")
        
        if tcp_host:
            self.device = self.device_manager.connect_tcp(tcp_host, tcp_port)
        elif device_id:
            self.device = self.device_manager.select_device(device_id)
        else:
            self.device = self.device_manager.connect_usb()
        
        # Garantir dispositivo pronto
        self.device.ensure_ready()
        
        # Inicializar componentes
        self.adb = ADBBridge(self.device.device_id)
        self.dumper = Dumper(self.adb)
        
        screen_w, screen_h = self.adb.get_screen_size()
        self.locator = Locator(screen_w, screen_h)
        
        # Finder precisa de callable para obter root
        self.finder = Finder(self.dumper.get_current_tree)
        
        self.clicker = Clicker(self.adb)
        self.keyboard = Keyboard(self.adb)
        self.gestures = Gestures(self.adb, screen_w, screen_h)
        self.watcher = UIWatcher(self.dumper)
        self.validator = Validator()
        
        # Form precisa dos outros componentes
        self.form = SmartForm(self.finder, self.locator, self.clicker, self.keyboard)
        
        # Flow engine
        self.flow = FlowEngine(self)
        
        self._initialized = True
        self.log.success("Conexão estabelecida e engine inicializada")
        
        return self
    
    def disconnect(self):
        """Desconecta do dispositivo."""
        self.device_manager.disconnect_all()
        self._initialized = False
        self.log.info("Desconectado")
    
    def open(self, package: str, activity: str = None) -> bool:
        """Abre aplicativo."""
        self.log.info(f"Abrindo {package}")
        return self.adb.start_app(package, activity)
    
    def close(self, package: str) -> bool:
        """Fecha aplicativo."""
        return self.adb.stop_app(package)
    
    def wait(self, text: str = None, timeout: int = 10, **kwargs) -> bool:
        """Aguarda elemento/texto aparecer."""
        if text:
            return self.watcher.wait_for_text(text, timeout)
        return self.watcher.wait_for_element(timeout, **kwargs)
    
    def click(self, text: str = None, desc: str = None, 
              resource_id: str = None, **kwargs) -> bool:
        """Clica em elemento por critérios."""
        self._refresh_if_needed()
        
        if text:
            node = self.finder.find_text(text)
        elif desc:
            node = self.finder.find_desc(desc)
        elif resource_id:
            node = self.finder.find_resource(resource_id)
        else:
            node = self.finder.find_first(**kwargs)
        
        if node:
            return self.clicker.click(node)
        return False
    
    def input(self, text: str) -> bool:
        """Digita texto."""
        return self.keyboard.send_keys(text)
    
    def scroll(self, direction: str = "down", steps: int = 1) -> bool:
        """Rola tela."""
        return self.gestures.scroll(direction, steps)
    
    def screenshot(self, filename: str = None) -> str:
        """Captura screenshot."""
        import time
        from config.settings import SCREENSHOTS_DIR
        
        if not filename:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
        
        remote_path = f"/sdcard/{filename}"
        local_path = f"{SCREENSHOTS_DIR}/{filename}"
        
        self.adb.screenshot(remote_path)
        self.adb.pull(remote_path, local_path)
        
        self.log.success(f"Screenshot salva: {local_path}")
        return local_path
    
    def _refresh_if_needed(self):
        """Atualiza dump se necessário."""
        if self.dumper:
            self.dumper.dump(use_cache=True)
    
    def get_ui_summary(self) -> Dict:
        """Retorna resumo da UI atual."""
        if self.dumper:
            return self.dumper.get_summary()
        return {}
    
    @property
    def current_package(self) -> str:
        """Pacote em primeiro plano."""
        return self.adb.get_current_package() if self.adb else ""


# Export convenience
__all__ = ['DixEngine']
