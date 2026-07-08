"""
Gestures - Sistema de gestos e movimentos na tela
"""
import time
from typing import Optional, Tuple, List
from lib.adb_bridge import ADBBridge
from lib.logs import logger


class Gestures:
    """Executa gestos complexos na tela."""
    
    def __init__(self, adb: ADBBridge, screen_width: int, screen_height: int):
        self.adb = adb
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.log = logger.get_logger("Gestures")
    
    def swipe(self, start: Tuple[int, int], end: Tuple[int, int], 
              duration: int = 300) -> bool:
        """Executa swipe entre dois pontos."""
        self.log.info(f"Swipe de {start} para {end}")
        return self.adb.input_swipe(start[0], start[1], end[0], end[1], duration)
    
    def scroll(self, direction: str = "down", steps: int = 1) -> bool:
        """
        Executa scroll na direção especificada.
        
        Args:
            direction: 'up', 'down', 'left', 'right'
            steps: Número de scrolls
        """
        margin = 100
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2
        
        gestures = {
            "down": (center_x, self.screen_height - margin, center_x, margin),
            "up": (center_x, margin, center_x, self.screen_height - margin),
            "left": (self.screen_width - margin, center_y, margin, center_y),
            "right": (margin, center_y, self.screen_width - margin, center_y)
        }
        
        if direction not in gestures:
            raise ValueError(f"Direção inválida: {direction}")
        
        for _ in range(steps):
            x1, y1, x2, y2 = gestures[direction]
            self.swipe((x1, y1), (x2, y2), duration=200)
            time.sleep(0.2)
        
        return True
    
    def fling(self, direction: str = "down", speed: int = 100) -> bool:
        """Executa fling (scroll rápido)."""
        return self.scroll(direction, steps=1)
    
    def pinch(self, center: Tuple[int, int] = None, scale: float = 0.5) -> bool:
        """
        Executa gesto de pinça (zoom out).
        
        Args:
            center: Centro do gesto (padrão: centro da tela)
            scale: Fator de escala (0-1 para zoom out, >1 para zoom in)
        """
        if center is None:
            center = (self.screen_width // 2, self.screen_height // 2)
        
        distance = min(self.screen_width, self.screen_height) // 4
        
        # Pinch out (dois dedos se afastando)
        if scale > 1:
            start1 = (center[0] - distance, center[1])
            start2 = (center[0] + distance, center[1])
            end1 = (center[0] - int(distance * scale), center[1])
            end2 = (center[0] + int(distance * scale), center[1])
        else:
            # Pinch in (dois dedos se aproximando)
            start_dist = int(distance * scale)
            start1 = (center[0] - start_dist, center[1])
            start2 = (center[0] + start_dist, center[1])
            end1 = (center[0] - distance, center[1])
            end2 = (center[0] + distance, center[1])
        
        # Simular multi-touch via comandos sequenciais
        self.adb.input_swipe(start1[0], start1[1], end1[0], end1[1], 200)
        time.sleep(0.1)
        self.adb.input_swipe(start2[0], start2[1], end2[0], end2[1], 200)
        
        return True
    
    def zoom(self, center: Tuple[int, int] = None, factor: float = 1.5) -> bool:
        """Executa zoom in/out."""
        return self.pinch(center, scale=factor)
    
    def drag(self, start: Tuple[int, int], end: Tuple[int, int], 
             duration: int = 500) -> bool:
        """Executa arrastar de um ponto a outro."""
        self.log.info(f"Drag de {start} para {end}")
        return self.adb.input_swipe(start[0], start[1], end[0], end[1], duration)
    
    def tap_sequence(self, points: List[Tuple[int, int]], interval: float = 0.1) -> bool:
        """Executa sequência de taps."""
        for point in points:
            self.adb.input_tap(point[0], point[1])
            time.sleep(interval)
        return True
    
    def gesture_path(self, points: List[Tuple[int, int]], 
                     duration_per_segment: int = 100) -> bool:
        """
        Executa gesto seguindo caminho de pontos.
        
        Args:
            points: Lista de coordenadas [(x1,y1), (x2,y2), ...]
            duration_per_segment: Duração por segmento em ms
        """
        if len(points) < 2:
            raise ValueError("Mínimo de 2 pontos necessário")
        
        for i in range(len(points) - 1):
            self.swipe(points[i], points[i+1], duration_per_segment)
        
        return True
    
    def scroll_to_show(self, node, finder, dumper, max_swipes: int = 10) -> bool:
        """
        Rola a tela até mostrar o elemento.
        
        Args:
            node: Nó a ser mostrado (ou critérios de busca)
            finder: Instância do Finder
            dumper: Instância do Dumper
            max_swipes: Número máximo de scrolls
        """
        for i in range(max_swipes):
            _, root = dumper.dump()
            
            # Verificar se elemento está visível
            if hasattr(node, 'is_visible') and node.is_visible:
                return True
            
            # Tentar encontrar por critérios se for string
            if isinstance(node, str):
                found = finder.find_text(node)
                if found and found.is_visible:
                    return True
            
            # Scroll para baixo
            self.scroll("down")
            time.sleep(0.5)
        
        return False
