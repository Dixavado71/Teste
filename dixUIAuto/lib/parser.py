"""
XML Parser - Transforma XML em árvore navegável de objetos
"""
import xml.etree.ElementTree as ET
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from lib.logs import logger
from lib.exceptions import ParseError


@dataclass
class UINode:
    """Representa um elemento da interface como objeto."""
    
    # Atributos do nó
    text: str = ""
    resource_id: str = ""
    class_name: str = ""
    content_desc: str = ""
    bounds: tuple = (0, 0, 0, 0)  # (left, top, right, bottom)
    checkable: bool = False
    checked: bool = False
    clickable: bool = False
    enabled: bool = True
    focusable: bool = False
    focused: bool = False
    scrollable: bool = False
    long_clickable: bool = False
    password: bool = False
    selected: bool = False
    visible_to_user: bool = True
    
    # Relacionamentos
    parent: Optional['UINode'] = None
    children: List['UINode'] = field(default_factory=list)
    
    # Metadados
    depth: int = 0
    index: int = 0
    
    @property
    def center(self) -> tuple:
        """Retorna centro do elemento."""
        left, top, right, bottom = self.bounds
        return ((left + right) // 2, (top + bottom) // 2)
    
    @property
    def width(self) -> int:
        return self.bounds[2] - self.bounds[0]
    
    @property
    def height(self) -> int:
        return self.bounds[3] - self.bounds[1]
    
    @property
    def is_visible(self) -> bool:
        """Verifica se elemento é visível e tem dimensões."""
        return self.visible_to_user and self.width > 0 and self.height > 0
    
    @property
    def is_interactive(self) -> bool:
        """Verifica se elemento pode ser interagido."""
        return self.clickable or self.long_clickable or self.scrollable
    
    def get_siblings(self) -> List['UINode']:
        """Retorna irmãos do nó."""
        if not self.parent:
            return []
        return [c for c in self.parent.children if c != self]
    
    def get_all_descendants(self) -> List['UINode']:
        """Retorna todos os descendentes recursivamente."""
        descendants = []
        for child in self.children:
            descendants.append(child)
            descendants.extend(child.get_all_descendants())
        return descendants
    
    def find_ancestor(self, class_name: str = None, resource_id: str = None) -> Optional['UINode']:
        """Encontra ancestral que corresponde aos critérios."""
        current = self.parent
        while current:
            if (class_name and class_name in current.class_name) or \
               (resource_id and resource_id in current.resource_id):
                return current
            current = current.parent
        return None
    
    def to_dict(self) -> Dict:
        """Converte nó para dicionário."""
        return {
            "text": self.text,
            "resource_id": self.resource_id,
            "class_name": self.class_name,
            "content_desc": self.content_desc,
            "bounds": self.bounds,
            "center": self.center,
            "checkable": self.checkable,
            "checked": self.checked,
            "clickable": self.clickable,
            "enabled": self.enabled,
            "focusable": self.focusable,
            "scrollable": self.scrollable,
            "long_clickable": self.long_clickable,
            "password": self.password,
            "selected": self.selected,
            "visible_to_user": self.visible_to_user,
            "depth": self.depth,
            "index": self.index,
            "children_count": len(self.children)
        }
    
    def __str__(self) -> str:
        text_preview = self.text[:30] + "..." if len(self.text) > 30 else self.text
        return f"<{self.class_name.split('.')[-1]} text='{text_preview}' id='{self.resource_id.split('/')[-1] if '/' in self.resource_id else self.resource_id}'>"


class XMLParser:
    """Parseia XML do uiautomator e cria árvore de UINode."""
    
    def __init__(self):
        self.log = logger.get_logger("Parser")
        self.root: Optional[UINode] = None
        self._node_count = 0
    
    def parse(self, xml_content: str) -> UINode:
        """Parseia conteúdo XML e retorna árvore de nós."""
        try:
            self.log.debug(f"Parseando XML ({len(xml_content)} bytes)...")
            
            # Tratar namespace Android
            xml_content = xml_content.replace('android:', '')
            
            root_elem = ET.fromstring(xml_content)
            self._node_count = 0
            
            self.root = self._parse_element(root_elem, None, 0)
            
            self.log.success(f"XML parseado: {self._node_count} nós")
            return self.root
            
        except ET.ParseError as e:
            raise ParseError(f"Erro ao parsear XML: {e}")
        except Exception as e:
            raise ParseError(f"Erro inesperado: {e}")
    
    def _parse_element(self, elem: ET.Element, parent: Optional[UINode], depth: int) -> UINode:
        """Cria UINode a partir de elemento XML."""
        node = UINode()
        node.depth = depth
        node.index = len(parent.children) if parent else 0
        node.parent = parent
        
        # Extrair atributos
        for attr in elem.attrib:
            value = elem.get(attr)
            
            if attr == "text":
                node.text = value or ""
            elif attr == "resource-id":
                node.resource_id = value or ""
            elif attr == "class":
                node.class_name = value or ""
            elif attr == "content-desc":
                node.content_desc = value or ""
            elif attr == "bounds":
                node.bounds = self._parse_bounds(value)
            elif attr == "checkable":
                node.checkable = value == "true"
            elif attr == "checked":
                node.checked = value == "true"
            elif attr == "clickable":
                node.clickable = value == "true"
            elif attr == "enabled":
                node.enabled = value == "true"
            elif attr == "focusable":
                node.focusable = value == "true"
            elif attr == "focused":
                node.focused = value == "true"
            elif attr == "scrollable":
                node.scrollable = value == "true"
            elif attr == "long-clickable":
                node.long_clickable = value == "true"
            elif attr == "password":
                node.password = value == "true"
            elif attr == "selected":
                node.selected = value == "true"
            elif attr == "visible-to-user":
                node.visible_to_user = value == "true"
        
        # Processar filhos
        for child_elem in elem:
            child_node = self._parse_element(child_elem, node, depth + 1)
            node.children.append(child_node)
        
        self._node_count += 1
        return node
    
    def _parse_bounds(self, bounds_str: str) -> tuple:
        """Parseia string de bounds [x1,y1][x2,y2]."""
        try:
            # Formato: [x1,y1][x2,y2]
            bounds_str = bounds_str.strip('[]')
            parts = bounds_str.split('][')
            if len(parts) == 2:
                x1, y1 = map(int, parts[0].split(','))
                x2, y2 = map(int, parts[1].split(','))
                return (x1, y1, x2, y2)
        except Exception:
            pass
        return (0, 0, 0, 0)
    
    def find_all(self, **kwargs) -> List[UINode]:
        """Encontra todos os nós que correspondem aos critérios."""
        if not self.root:
            return []
        
        results = []
        nodes_to_check = [self.root]
        
        while nodes_to_check:
            node = nodes_to_check.pop(0)
            if self._matches_criteria(node, **kwargs):
                results.append(node)
            nodes_to_check.extend(node.children)
        
        return results
    
    def _matches_criteria(self, node: UINode, **kwargs) -> bool:
        """Verifica se nó corresponde aos critérios."""
        for key, value in kwargs.items():
            if value is None:
                continue
            
            node_value = getattr(node, key, None)
            
            if key == "text_contains":
                if value not in node.text:
                    return False
            elif key == "text_matches":
                import re
                if not re.search(value, node.text, re.IGNORECASE):
                    return False
            elif key == "id_contains":
                if value not in node.resource_id:
                    return False
            elif key == "class_contains":
                if value not in node.class_name:
                    return False
            elif node_value != value:
                return False
        
        return True
    
    def get_tree_summary(self) -> Dict:
        """Retorna resumo da árvore UI."""
        if not self.root:
            return {}
        
        all_nodes = self.root.get_all_descendants()
        
        return {
            "total_nodes": len(all_nodes) + 1,
            "max_depth": max(n.depth for n in all_nodes) if all_nodes else 0,
            "interactive_elements": sum(1 for n in all_nodes if n.is_interactive),
            "visible_elements": sum(1 for n in all_nodes if n.is_visible),
            "with_text": sum(1 for n in all_nodes if n.text),
            "with_content_desc": sum(1 for n in all_nodes if n.content_desc),
            "edit_texts": sum(1 for n in all_nodes if 'EditText' in n.class_name),
            "buttons": sum(1 for n in all_nodes if 'Button' in n.class_name),
        }
