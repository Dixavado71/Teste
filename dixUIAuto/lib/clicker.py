"""
Click Engine - Execução de ações de clique e toque
"""
import time
from typing import Optional, Tuple
from lib.parser import UINode
from lib.adb_bridge import ADBBridge
from lib.logs import logger
from lib.exceptions import ElementNotClickableError


class Clicker:
    """Executa ações de clique e toque na tela."""
    
    def __init__(self, adb: ADBBridge):
        self.adb = adb
        self.log = logger.get_logger("Clicker")
    
    def click(self, node: UINode, offset: Tuple[int, int] = None) -> bool:
        """
        Clica no centro do elemento.
        
        Args:
            node: Nó UI a ser clicado
            offset: Offset opcional (dx, dy) do centro
        """
        if not node.is_visible:
            raise ElementNotClickableError("Elemento não está visível")
        
        center_x, center_y = node.center
        
        if offset:
            center_x += offset[0]
            center_y += offset[1]
        
        self.log.info(f"Clicando em {node} ({center_x}, {center_y})")
        return self.adb.input_tap(center_x, center_y)
    
    def click_coords(self, x: int, y: int) -> bool:
        """Clica em coordenadas específicas."""
        self.log.info(f"Clicando em ({x}, {y})")
        return self.adb.input_tap(x, y)
    
    def double_click(self, node: UINode, interval: float = 0.1) -> bool:
        """Executa duplo clique."""
        success = self.click(node)
        if success:
            time.sleep(interval)
            success = self.click(node)
        return success
    
    def long_click(self, node: UINode, duration: int = 1000) -> bool:
        """
        Executa long press.
        
        Args:
            node: Nó UI
            duration: Duração em milissegundos
        """
        if not node.is_visible:
            raise ElementNotClickableError("Elemento não está visível")
        
        x, y = node.center
        self.log.info(f"Long click em {node} por {duration}ms")
        
        # Simular long press via input swipe no mesmo ponto
        return self.adb.input_swipe(x, y, x, y, duration)
    
    def tap(self, x: int, y: int) -> bool:
        """Alias para click_coords."""
        return self.click_coords(x, y)
    
    def tap_center(self) -> bool:
        """Clica no centro da tela."""
        w, h = self.adb.get_screen_size()
        return self.click_coords(w // 2, h // 2)
    
    def click_parent(self, node: UINode) -> bool:
        """Clica no pai do elemento."""
        if not node.parent:
            raise ValueError("Elemento não tem pai")
        
        if not node.parent.is_visible:
            raise ElementNotClickableError("Pai não está visível")
        
        return self.click(node.parent)
    
    def click_nearest(self, reference_node: UINode, 
                      candidates: list, locator) -> bool:
        """
        Clica no elemento candidato mais próximo da referência.
        
        Args:
            reference_node: Nó de referência
            candidates: Lista de nós candidatos
            locator: Instância de Locator para cálculo
        """
        nearest = locator.find_nearest(reference_node, candidates)
        if not nearest:
            raise ElementNotClickableError("Nenhum candidato encontrado")
        
        return self.click(nearest)
    
    def click_text(self, text: str, finder) -> bool:
        """Encontra e clica em elemento por texto."""
        node = finder.find_text(text)
        return self.click(node)
    
    def click_desc(self, desc: str, finder) -> bool:
        """Encontra e clica em elemento por content-desc."""
        node = finder.find_desc(desc)
        return self.click(node)
    
    def click_resource(self, resource_id: str, finder) -> bool:
        """Encontra e clica em elemento por resource-id."""
        node = finder.find_resource(resource_id)
        return self.click(node)
    
    def wait_and_click(self, node: UINode, timeout: int = 10,
                       poll_interval: float = 0.5) -> bool:
        """
        Aguarda elemento ficar visível e clica.
        
        Args:
            node: Nó UI
            timeout: Tempo máximo em segundos
            poll_interval: Intervalo entre verificações
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if node.is_visible:
                return self.click(node)
            time.sleep(poll_interval)
        
        raise ElementNotClickableError(f"Timeout após {timeout}s")
