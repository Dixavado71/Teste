"""
Locator - Sistema de localização espacial e relacionamentos
"""
import math
from typing import List, Optional, Tuple
from lib.parser import UINode
from lib.logs import logger


class Locator:
    """Responsável por cálculos espaciais e relacionamentos entre elementos."""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.log = logger.get_logger("Locator")
    
    @staticmethod
    def get_center(node: UINode) -> Tuple[int, int]:
        """Retorna centro do elemento."""
        return node.center
    
    @staticmethod
    def get_distance(node1: UINode, node2: UINode) -> float:
        """Calcula distância entre centros de dois elementos."""
        c1 = node1.center
        c2 = node2.center
        return math.sqrt((c1[0] - c2[0])**2 + **(c1[1] - c2[1])2)
    
    @staticmethod
    def is_overlapping(node1: UINode, node2: UINode) -> bool:
        """Verifica se dois elementos se sobrepõem."""
        b1 = node1.bounds
        b2 = node2.bounds
        
        # Verificar sobreposição retangular
        return not (b1[2] < b2[0] or b1[0] > b2[2] or 
                    b1[3] < b2[1] or b1[1] > b2[3])
    
    def find_nearest(self, reference: UINode, candidates: List[UINode]) -> Optional[UINode]:
        """Encontra elemento mais próximo da referência."""
        if not candidates:
            return None
        
        min_dist = float('inf')
        nearest = None
        
        for candidate in candidates:
            dist = self.get_distance(reference, candidate)
            if dist < min_dist:
                min_dist = dist
                nearest = candidate
        
        return nearest
    
    def find_by_position(self, nodes: List[UINode], position: str) -> Optional[UINode]:
        """
        Encontra elemento por posição relativa.
        
        Args:
            nodes: Lista de candidatos
            position: 'top', 'bottom', 'left', 'right', 'center'
        """
        if not nodes:
            return None
        
        if position == 'top':
            return min(nodes, key=lambda n: n.center[1])
        elif position == 'bottom':
            return max(nodes, key=lambda n: n.center[1])
        elif position == 'left':
            return min(nodes, key=lambda n: n.center[0])
        elif position == 'right':
            return max(nodes, key=lambda n: n.center[0])
        elif position == 'center':
            screen_center = (self.screen_width // 2, self.screen_height // 2)
            return min(nodes, key=lambda n: math.sqrt(
                (n.center[0] - screen_center[0])**2 + **(n.center[1] - screen_center[1])2
            ))
        
        return nodes[0]
    
    def find_elements_above(self, reference: UINode, nodes: List[UINode]) -> List[UINode]:
        """Encontra elementos acima da referência."""
        ref_top = reference.bounds[1]
        return [n for n in nodes if n.bounds[3] < ref_top and n.is_visible]
    
    def find_elements_below(self, reference: UINode, nodes: List[UINode]) -> List[UINode]:
        """Encontra elementos abaixo da referência."""
        ref_bottom = reference.bounds[3]
        return [n for n in nodes if n.bounds[1] > ref_bottom and n.is_visible]
    
    def find_elements_left(self, reference: UINode, nodes: List[UINode]) -> List[UINode]:
        """Encontra elementos à esquerda da referência."""
        ref_left = reference.bounds[0]
        return [n for n in nodes if n.bounds[2] < ref_left and n.is_visible]
    
    def find_elements_right(self, reference: UINode, nodes: List[UINode]) -> List[UINode]:
        """Encontra elementos à direita da referência."""
        ref_right = reference.bounds[2]
        return [n for n in nodes if n.bounds[0] > ref_right and n.is_visible]
    
    def find_in_region(self, nodes: List[UINode], 
                       x: int = None, y: int = None,
                       width: int = None, height: int = None) -> List[UINode]:
        """
        Encontra elementos em uma região específica.
        
        Args:
            x, y: Coordenadas do canto superior esquerdo
            width, height: Dimensões da região
        """
        if x is None:
            x = 0
        if y is None:
            y = 0
        if width is None:
            width = self.screen_width
        if height is None:
            height = self.screen_height
        
        region_bounds = (x, y, x + width, y + height)
        
        results = []
        for node in nodes:
            if self._intersects(node.bounds, region_bounds):
                results.append(node)
        
        return results
    
    @staticmethod
    def _intersects(bounds1: tuple, bounds2: tuple) -> bool:
        """Verifica se dois retângulos se interceptam."""
        return not (bounds1[2] < bounds2[0] or bounds1[0] > bounds2[2] or
                    bounds1[3] < bounds2[1] or bounds1[1] > bounds2[3])
    
    def find_input_field_near_label(self, label_node: UINode, 
                                     all_nodes: List[UINode]) -> Optional[UINode]:
        """
        Encontra campo de input próximo a um label.
        Estratégia: procura EditText abaixo ou à direita do label.
        """
        # Procurar EditTexts visíveis
        edit_texts = [
            n for n in all_nodes 
            if 'EditText' in n.class_name and n.is_visible
        ]
        
        if not edit_texts:
            return None
        
        # Priorizar elementos abaixo do label
        below = self.find_elements_below(label_node, edit_texts)
        if below:
            # Ordenar por distância vertical
            below.sort(key=lambda n: abs(n.bounds[1] - label_node.bounds[3]))
            return below[0]
        
        # Se não encontrou abaixo, procurar à direita
        right = self.find_elements_right(label_node, edit_texts)
        if right:
            right.sort(key=lambda n: abs(n.bounds[0] - label_node.bounds[2]))
            return right[0]
        
        # Fallback: mais próximo em qualquer direção
        return self.find_nearest(label_node, edit_texts)
    
    def find_button_near_text(self, text: str, all_nodes: List[UINode]) -> Optional[UINode]:
        """Encontra botão próximo a um texto específico."""
        # Encontrar nó com o texto
        text_node = None
        for node in all_nodes:
            if text.lower() in node.text.lower():
                text_node = node
                break
        
        if not text_node:
            return None
        
        # Encontrar botões
        buttons = [
            n for n in all_nodes 
            if ('Button' in n.class_name or n.clickable) and n.is_visible
        ]
        
        if not buttons:
            return None
        
        return self.find_nearest(text_node, buttons)
    
    def is_in_viewport(self, node: UINode, margin: int = 0) -> bool:
        """Verifica se elemento está dentro da viewport visível."""
        return (node.bounds[0] >= -margin and 
                node.bounds[1] >= -margin and
                node.bounds[2] <= self.screen_width + margin and
                node.bounds[3] <= self.screen_height + margin)
    
    def get_scroll_direction_to_show(self, node: UINode) -> Optional[str]:
        """
        Determina direção de scroll necessária para mostrar elemento.
        
        Returns:
            'up', 'down', 'left', 'right' ou None se já visível
        """
        if self.is_in_viewport(node):
            return None
        
        if node.bounds[1] < 0:
            return 'up'
        elif node.bounds[3] > self.screen_height:
            return 'down'
        elif node.bounds[0] < 0:
            return 'left'
        elif node.bounds[2] > self.screen_width:
            return 'right'
        
        return None
