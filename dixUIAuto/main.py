"""
dixUIAuto - Framework de Automação Android Premium
Engine Central que coordena todos os módulos com recursos avançados
"""
import time
from typing import Optional, List, Dict, Any, Union
from pathlib import Path
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
from lib.inspector import SmartInspector
from lib.logs import logger
from lib.exceptions import DixUIAutoError, ElementNotFoundError


class DixEngine:
    """
    Engine principal do dixUIAuto com recursos premium.
    
    Recursos avançados:
    - Retry automático com backoff exponencial
    - Variáveis globais compartilhadas
    - Templates de flow dinâmicos
    - Page Objects reutilizáveis
    - Self-healing de seletores
    - Métricas de performance
    
    Exemplo de uso:
        engine = DixEngine()
        engine.connect()
        engine.open("com.app.package")
        engine.click(text="Entrar", retry=3)
        engine.form.fill(label="CPF", value="02959350146")
        engine.set_var("user_id", "12345")
    """
    
    def __init__(self, config: Dict = None):
        self.log = logger.get_logger("Engine")
        self.config = config or {}
        
        # Gerenciamento de dispositivos
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
        self.inspector: Optional[SmartInspector] = None
        
        # Recursos avançados
        self._variables: Dict[str, Any] = {}  # Variáveis globais
        self._page_objects: Dict[str, Any] = {}  # Page objects registrados
        self._metrics: Dict[str, Any] = {"start_time": None, "actions": []}
        self._retry_config = {
            "max_retries": self.config.get("max_retries", 3),
            "backoff_factor": self.config.get("backoff_factor", 1.5),
            "exceptions": (ElementNotFoundError,)
        }
        
        self._initialized = False
        self.log.info("DixEngine inicializada com configuração premium")
    
    def connect(self, device_id: str = None, tcp_host: str = None, 
                tcp_port: int = 5555, timeout: int = 10) -> 'DixEngine':
        """
        Conecta ao dispositivo Android com retry automático.
        
        Args:
            device_id: ID do dispositivo (USB ou TCP)
            tcp_host: Host para conexão TCP/IP
            tcp_port: Porta para conexão TCP/IP
            timeout: Timeout para conexão
        
        Returns:
            Self para chaining
        """
        self.log.info(f"Iniciando conexão (timeout={timeout}s)...")
        self._metrics["start_time"] = time.time()
        
        try:
            if tcp_host:
                self.device = self.device_manager.connect_tcp(tcp_host, tcp_port)
            elif device_id:
                self.device = self.device_manager.select_device(device_id)
            else:
                self.device = self.device_manager.connect_usb()
            
            if not self.device:
                raise DixUIAutoError("Nenhum dispositivo encontrado")
            
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
            
            # Inspector
            self.inspector = SmartInspector()
            
            self._initialized = True
            
            elapsed = time.time() - self._metrics["start_time"]
            self.log.success(f"Conexão estabelecida em {elapsed:.2f}s")
            
            return self
            
        except Exception as e:
            self.log.error(f"Falha na conexão: {e}")
            raise DixUIAutoError(f"Erro ao conectar: {e}")
    
    def disconnect(self):
        """Desconecta do dispositivo e salva métricas."""
        if self._metrics["start_time"]:
            total_time = time.time() - self._metrics["start_time"]
            self._metrics["total_time"] = total_time
            self.log.info(f"Sessão completada em {total_time:.2f}s ({len(self._metrics['actions'])} ações)")
        
        self.device_manager.disconnect_all()
        self._initialized = False
        self.log.info("Desconectado")
    
    def open(self, package: str, activity: str = None, wait_time: int = 3) -> bool:
        """Abre aplicativo e aguarda carregamento."""
        self.log.info(f"Abrindo {package}")
        result = self.adb.start_app(package, activity)
        if wait_time > 0:
            time.sleep(wait_time)
        return result
    
    def close(self, package: str) -> bool:
        """Fecha aplicativo."""
        return self.adb.stop_app(package)
    
    def wait(self, text: str = None, timeout: int = 10, **kwargs) -> bool:
        """Aguarda elemento/texto aparecer."""
        if text:
            return self.watcher.wait_for_text(text, timeout)
        return self.watcher.wait_for_element(timeout, **kwargs)
    
    def click(self, text: str = None, desc: str = None, 
              resource_id: str = None, retry: int = None, **kwargs) -> bool:
        """
        Clica em elemento com retry automático.
        
        Args:
            text: Texto do elemento
            desc: Content description
            resource_id: Resource ID
            retry: Número de tentativas (usa padrão se None)
            **kwargs: Critérios adicionais
        """
        max_retries = retry if retry is not None else self._retry_config["max_retries"]
        
        for attempt in range(1, max_retries + 1):
            try:
                self._record_action("click", attempt=attempt, criteria={"text": text, "desc": desc})
                
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
                    result = self.clicker.click(node)
                    if result:
                        self.log.success(f"Clique bem-sucedido (tentativa {attempt})")
                        return True
                
                if attempt < max_retries:
                    delay = self._retry_config["backoff_factor"] ** (attempt - 1)
                    self.log.warning(f"Tentativa {attempt} falhou, retry em {delay:.1f}s")
                    time.sleep(delay)
                    
            except Exception as e:
                self.log.warning(f"Erro na tentativa {attempt}: {e}")
                if attempt >= max_retries:
                    raise
        
        self.log.error(f"Falha após {max_retries} tentativas")
        return False
    
    def input(self, text: str, clear_first: bool = True) -> bool:
        """Digita texto."""
        self._record_action("input", text=text[:20] + "..." if len(text) > 20 else text)
        if clear_first:
            self.keyboard.clear()
        return self.keyboard.send_keys(text)
    
    def scroll(self, direction: str = "down", steps: int = 1) -> bool:
        """Rola tela."""
        self._record_action("scroll", direction=direction, steps=steps)
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
        
        self._record_action("screenshot", path=local_path)
        self.log.success(f"Screenshot salva: {local_path}")
        return local_path
    
    # === Variáveis Globais ===
    
    def set_var(self, key: str, value: Any):
        """Define variável global."""
        self._variables[key] = value
        self.log.debug(f"Variável definida: {key} = {value}")
    
    def get_var(self, key: str, default: Any = None) -> Any:
        """Obtém variável global."""
        return self._variables.get(key, default)
    
    def get_all_vars(self) -> Dict:
        """Retorna todas as variáveis."""
        return self._variables.copy()
    
    def resolve_template(self, template: str) -> str:
        """
        Resolve template com variáveis.
        Ex: "Olá {{name}}" -> "Olá João"
        """
        result = template
        for key, value in self._variables.items():
            result = result.replace(f"{{{{{key}}}}}", str(value))
        return result
    
    # === Page Objects ===
    
    def register_page(self, name: str, page_object: Any):
        """Registra page object."""
        self._page_objects[name] = page_object
        self.log.info(f"Page object registrado: {name}")
    
    def get_page(self, name: str) -> Any:
        """Obtém page object."""
        if name not in self._page_objects:
            raise DixUIAutoError(f"Page object não encontrado: {name}")
        return self._page_objects[name]
    
    # === Métricas ===
    
    def _record_action(self, action_type: str, **details):
        """Registra ação para métricas."""
        self._metrics["actions"].append({
            "type": action_type,
            "timestamp": time.time(),
            "details": details
        })
    
    def get_metrics(self) -> Dict:
        """Retorna métricas da sessão."""
        if self._metrics["start_time"]:
            self._metrics["elapsed"] = time.time() - self._metrics["start_time"]
        return self._metrics.copy()
    
    def export_metrics(self, filepath: str):
        """Exporta métricas para JSON."""
        import json
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.get_metrics(), f, indent=2, default=str)
        self.log.info(f"Métricas exportadas: {filepath}")
    
    # === Utils ===
    
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
    
    @property
    def variables(self) -> Dict:
        """Acesso direto às variáveis."""
        return self._variables


# Export convenience
__all__ = ['DixEngine']
