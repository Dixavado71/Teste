"""
Watcher - Observa mudanças na interface em tempo real
"""
import time
import threading
from typing import Callable, Optional, List
from lib.dumper import Dumper
from lib.logs import logger


class UIWatcher:
    """Observa a interface e detecta mudanças."""
    
    def __init__(self, dumper: Dumper):
        self.dumper = dumper
        self.log = logger.get_logger("Watcher")
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._callbacks: List[Callable] = []
        self._last_hash: Optional[str] = None
        self._poll_interval = 0.5
    
    def start(self, callback: Callable = None, poll_interval: float = 0.5):
        """Inicia watcher em thread separada."""
        if self._running:
            return
        
        self._poll_interval = poll_interval
        self._running = True
        
        if callback:
            self._callbacks.append(callback)
        
        self._thread = threading.Thread(target=self._watch_loop, daemon=True)
        self._thread.start()
        self.log.info("Watcher iniciado")
    
    def stop(self):
        """Para o watcher."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)
        self.log.info("Watcher parado")
    
    def _watch_loop(self):
        """Loop principal do watcher."""
        while self._running:
            try:
                ui_changed, _ = self.dumper.dump(use_cache=True)
                
                if ui_changed:
                    self.log.debug("Mudança de UI detectada")
                    for callback in self._callbacks:
                        try:
                            callback(self.dumper.get_current_tree())
                        except Exception as e:
                            self.log.error(f"Erro no callback: {e}")
                
                time.sleep(self._poll_interval)
            except Exception as e:
                self.log.error(f"Erro no watcher: {e}")
                time.sleep(1)
    
    def add_callback(self, callback: Callable):
        """Adiciona callback para mudanças de UI."""
        self._callbacks.append(callback)
    
    def remove_callback(self, callback: Callable):
        """Remove callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    def wait_for_text(self, text: str, timeout: int = 10, 
                      finder=None) -> bool:
        """Aguarda até que texto apareça na tela."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            _, root = self.dumper.dump()
            
            for node in root.get_all_descendants():
                if text.lower() in node.text.lower():
                    self.log.success(f"Texto '{text}' encontrado")
                    return True
            
            time.sleep(self._poll_interval)
        
        self.log.warning(f"Timeout aguardando texto: {text}")
        return False
    
    def wait_for_element(self, timeout: int = 10, **kwargs) -> bool:
        """Aguarda até que elemento corresponda aos critérios."""
        from lib.finder import Finder
        finder = Finder(self.dumper.get_current_tree)
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            _, root = self.dumper.dump()
            
            try:
                found = finder.find_first(**kwargs)
                if found:
                    return True
            except:
                pass
            
            time.sleep(self._poll_interval)
        
        return False
