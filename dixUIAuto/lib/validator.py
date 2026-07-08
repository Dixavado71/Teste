"""
Validator - Validação de operações e estados
"""
import re
import time
from typing import Optional, Dict, Any
from lib.parser import UINode
from lib.logs import logger
from config.constants import PATTERNS


class Validator:
    """Confirma operações e valida estados da UI."""
    
    def __init__(self):
        self.log = logger.get_logger("Validator")
    
    def validate_text(self, node: UINode, expected: str, 
                      exact: bool = False) -> bool:
        """Valida se nó contém texto esperado."""
        if exact:
            result = node.text == expected
        else:
            result = expected.lower() in node.text.lower()
        
        if result:
            self.log.success(f"Texto validado: {expected}")
        else:
            self.log.warning(f"Texto não corresponde: esperado '{expected}', encontrado '{node.text}'")
        
        return result
    
    def validate_input(self, field_node: UINode, value: str, 
                       input_type: str = None) -> bool:
        """Valida se campo foi preenchido corretamente."""
        # Verificar se valor está no campo (se acessível)
        if field_node.text and value in field_node.text:
            self.log.success(f"Input validado: {value[:10]}...")
            return True
        
        # Validar formato por tipo
        if input_type and input_type in PATTERNS:
            pattern = PATTERNS[input_type]
            if re.match(pattern, value):
                self.log.success(f"Formato {input_type} válido")
                return True
            else:
                self.log.error(f"Formato {input_type} inválido para: {value}")
                return False
        
        return True
    
    def validate_screen_change(self, old_root: UINode, new_root: UINode,
                                threshold: float = 0.3) -> bool:
        """Valida se tela mudou significativamente."""
        if not old_root or not new_root:
            return True
        
        old_nodes = set(str(n) for n in old_root.get_all_descendants())
        new_nodes = set(str(n) for n in new_root.get_all_descendants())
        
        if not old_nodes:
            return True
        
        changed = len(new_nodes - old_nodes) / len(old_nodes)
        return changed > threshold
    
    def assert_exists(self, node: UINode, message: str = None) -> bool:
        """Assert que elemento existe."""
        if node:
            self.log.success(message or "Elemento existe")
            return True
        self.log.error(message or "Elemento não existe")
        return False
    
    def assert_visible(self, node: UINode, message: str = None) -> bool:
        """Assert que elemento está visível."""
        if node and node.is_visible:
            self.log.success(message or "Elemento visível")
            return True
        self.log.error(message or "Elemento não visível")
        return False
    
    def assert_text(self, node: UINode, text: str, 
                    contains: bool = True) -> bool:
        """Assert que elemento tem texto específico."""
        if not node:
            self.log.error("Elemento não encontrado")
            return False
        
        if contains:
            result = text.lower() in node.text.lower()
        else:
            result = text == node.text
        
        if result:
            self.log.success(f"Texto '{text}' confirmado")
            return True
        
        self.log.error(f"Texto não corresponde: '{node.text}'")
        return False
    
    def assert_count(self, nodes: list, expected: int, 
                     message: str = None) -> bool:
        """Assert que quantidade de elementos é esperada."""
        count = len(nodes)
        if count == expected:
            self.log.success(message or f"Contagem correta: {count}")
            return True
        
        self.log.error(f"Contagem incorreta: esperado {expected}, encontrado {count}")
        return False
    
    def validate_form_filled(self, fields: Dict[str, UINode], 
                              values: Dict[str, str]) -> Dict[str, bool]:
        """Valida múltiplos campos de formulário."""
        results = {}
        
        for field_name, node in fields.items():
            expected_value = values.get(field_name, "")
            results[field_name] = self.validate_input(node, expected_value)
        
        all_valid = all(results.values())
        if all_valid:
            self.log.success("Todos os campos validados")
        else:
            self.log.warning(f"Campos inválidos: {[k for k, v in results.items() if not v]}")
        
        return results
