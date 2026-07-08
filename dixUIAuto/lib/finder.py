"""
Finder - Sistema de pesquisa de elementos UI
"""
import re
from typing import List, Optional, Union
from lib.parser import UINode
from lib.logs import logger
from lib.exceptions import ElementNotFoundError


class Finder:
    """Sistema responsável pela pesquisa de elementos na árvore UI."""
    
    def __init__(self, get_root_callable):
        """
        Inicializa Finder.
        
        Args:
            get_root_callable: Função que retorna o root node atual
        """
        self.log = logger.get_logger("Finder")
        self._get_root = get_root_callable
    
    def _get_tree(self) -> Optional[UINode]:
        """Obtém árvore UI atual."""
        return self._get_root()
    
    def find_text(self, text: str, exact: bool = False) -> Optional[UINode]:
        """Encontra elemento por texto."""
        root = self._get_tree()
        if not root:
            return None
        
        for node in root.get_all_descendants():
            if exact:
                if node.text == text:
                    return node
            else:
                if text.lower() in node.text.lower():
                    return node
        
        raise ElementNotFoundError("text", text)
    
    def find_text_contains(self, text: str) -> Optional[UINode]:
        """Encontra elemento que contém texto."""
        return self.find_text(text, exact=False)
    
    def find_desc(self, desc: str, exact: bool = False) -> Optional[UINode]:
        """Encontra elemento por content-desc."""
        root = self._get_tree()
        if not root:
            return None
        
        for node in root.get_all_descendants():
            if exact:
                if node.content_desc == desc:
                    return node
            else:
                if desc.lower() in node.content_desc.lower():
                    return node
        
        raise ElementNotFoundError("content_desc", desc)
    
    def find_resource(self, resource_id: str) -> Optional[UINode]:
        """Encontra elemento por resource-id."""
        root = self._get_tree()
        if not root:
            return None
        
        # Tentar match exato
        for node in root.get_all_descendants():
            if node.resource_id == resource_id:
                return node
        
        # Tentar match parcial (último segmento do ID)
        short_id = resource_id.split('/')[-1] if '/' in resource_id else resource_id
        for node in root.get_all_descendants():
            if node.resource_id.endswith(short_id):
                return node
        
        raise ElementNotFoundError("resource_id", resource_id)
    
    def find_class(self, class_name: str) -> Optional[UINode]:
        """Encontra elemento por classe."""
        root = self._get_tree()
        if not root:
            return None
        
        for node in root.get_all_descendants():
            if class_name in node.class_name:
                return node
        
        raise ElementNotFoundError("class", class_name)
    
    def find_xpath(self, xpath: str) -> Optional[UINode]:
        """
        Encontra elemento usando expressão XPath simplificada.
        
        Suporta:
        - //ClassName - qualquer nó da classe
        - //ClassName[@text='texto'] - com texto específico
        - //ClassName[@resource-id='id'] - com ID específico
        """
        root = self._get_tree()
        if not root:
            return None
        
        # Parse simples de XPath
        xpath = xpath.strip()
        
        # Extrair classe e condições
        class_match = re.match(r'//(\w+)(?:\[(.+)\])?', xpath)
        if not class_match:
            raise ValueError(f"XPath inválido: {xpath}")
        
        target_class = class_match.group(1)
        conditions = class_match.group(2)
        
        # Encontrar nós da classe
        candidates = []
        for node in root.get_all_descendants():
            if target_class in node.class_name:
                candidates.append(node)
        
        if not candidates:
            raise ElementNotFoundError("xpath", xpath)
        
        # Aplicar condições se existirem
        if conditions:
            cond_match = re.match(r"@(\w+)='([^']+)'", conditions)
            if cond_match:
                attr_name = cond_match.group(1)
                attr_value = cond_match.group(2)
                
                for node in candidates:
                    node_attr = getattr(node, attr_name.replace('-', '_'), "")
                    if node_attr == attr_value:
                        return node
                
                raise ElementNotFoundError("xpath", xpath)
        
        return candidates[0]
    
    def find_regex(self, pattern: str, field: str = "text") -> Optional[UINode]:
        """Encontra elemento usando regex em campo específico."""
        root = self._get_tree()
        if not root:
            return None
        
        regex = re.compile(pattern, re.IGNORECASE)
        
        for node in root.get_all_descendants():
            value = getattr(node, field, "")
            if regex.search(value):
                return node
        
        raise ElementNotFoundError("regex", pattern)
    
    def find_multiple(self, **kwargs) -> List[UINode]:
        """
        Encontra múltiplos elementos que correspondem aos critérios.
        
        Exemplo: find_multiple(text_contains="btn", clickable=True)
        """
        root = self._get_tree()
        if not root:
            return []
        
        results = []
        
        for node in root.get_all_descendants():
            if self._matches_all(node, **kwargs):
                results.append(node)
        
        return results
    
    def _matches_all(self, node: UINode, **kwargs) -> bool:
        """Verifica se nó corresponde a todos os critérios."""
        for key, value in kwargs.items():
            if key == "text_contains":
                if value not in node.text:
                    return False
            elif key == "text_matches":
                if not re.search(value, node.text, re.IGNORECASE):
                    return False
            elif key == "desc_contains":
                if value not in node.content_desc:
                    return False
            elif key == "id_contains":
                if value not in node.resource_id:
                    return False
            elif key == "class_contains":
                if value not in node.class_name:
                    return False
            else:
                node_value = getattr(node, key, None)
                if node_value != value:
                    return False
        
        return True
    
    def find_first(self, **kwargs) -> Optional[UINode]:
        """Encontra primeiro elemento que corresponde aos critérios."""
        results = self.find_multiple(**kwargs)
        return results[0] if results else None
    
    def find_visible(self, **kwargs) -> List[UINode]:
        """Encontra elementos visíveis que correspondem aos critérios."""
        all_matches = self.find_multiple(**kwargs)
        return [n for n in all_matches if n.is_visible]
    
    def find_clickable(self, **kwargs) -> List[UINode]:
        """Encontra elementos clicáveis que correspondem aos critérios."""
        all_matches = self.find_multiple(**kwargs)
        return [n for n in all_matches if n.clickable]
    
    def find_by_label(self, label: str) -> Optional[UINode]:
        """
        Encontra elemento associado a um label.
        Útil para encontrar campos de formulário próximos a labels.
        """
        root = self._get_tree()
        if not root:
            return None
        
        # Primeiro, encontrar o label
        label_node = None
        for node in root.get_all_descendants():
            if label.lower() in node.text.lower():
                label_node = node
                break
        
        if not label_node:
            raise ElementNotFoundError("label", label)
        
        # Procurar EditText próximo (irmão ou filho do pai)
        parent = label_node.parent
        if parent:
            for sibling in parent.children:
                if 'EditText' in sibling.class_name and sibling.is_visible:
                    return sibling
        
        # Procurar em descendentes do label
        for node in label_node.get_all_descendants():
            if 'EditText' in node.class_name and node.is_visible:
                return node
        
        return None
