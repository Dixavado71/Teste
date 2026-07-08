"""
Smart Form - Preenchimento inteligente de formulários
"""
import time
from typing import Optional, Dict, List
from lib.parser import UINode
from lib.logs import logger
from config.constants import FORM_LABELS


class SmartForm:
    """Preenche formulários automaticamente identificando campos por labels."""
    
    def __init__(self, finder, locator, clicker, keyboard):
        self.finder = finder
        self.locator = locator
        self.clicker = clicker
        self.keyboard = keyboard
        self.log = logger.get_logger("Form")
    
    def fill(self, label: str, value: str, field_type: str = None) -> bool:
        """
        Preenche campo identificado por label.
        
        Args:
            label: Texto do label ou nome do campo
            value: Valor a preencher
            field_type: Tipo do campo (cpf, email, phone, etc.)
        """
        self.log.info(f"Preenchendo '{label}' com valor")
        
        # Encontrar label
        label_node = self._find_label(label)
        if not label_node:
            self.log.warning(f"Label '{label}' não encontrado, tentando busca direta")
            return self._fill_direct(value)
        
        # Encontrar campo associado
        all_nodes = label_node.get_all_descendants()
        field_node = self.locator.find_input_field_near_label(label_node, all_nodes)
        
        if not field_node:
            # Buscar em todo o tree
            root = self.finder._get_tree()
            if root:
                all_nodes = root.get_all_descendants()
                field_node = self.locator.find_input_field_near_label(label_node, all_nodes)
        
        if not field_node:
            self.log.error(f"Campo para '{label}' não encontrado")
            return False
        
        # Preencher campo
        return self._fill_field(field_node, value, field_type)
    
    def _find_label(self, label: str) -> Optional[UINode]:
        """Encontra nó de label."""
        # Buscar por texto exato ou parcial
        for variations in FORM_LABELS.values():
            if label.lower() in [v.lower() for v in variations]:
                for v in variations:
                    try:
                        return self.finder.find_text(v, exact=False)
                    except:
                        continue
        
        # Busca genérica
        try:
            return self.finder.find_text(label, exact=False)
        except:
            pass
        
        return None
    
    def _fill_field(self, field_node: UINode, value: str, 
                    field_type: str = None) -> bool:
        """Preenche campo específico."""
        try:
            # Clicar no campo
            self.clicker.click(field_node)
            time.sleep(0.3)
            
            # Limpar se necessário
            if field_node.text:
                self.keyboard.clear(field_node)
                time.sleep(0.2)
            
            # Digitar valor
            self.keyboard.send_keys(value)
            time.sleep(0.3)
            
            self.log.success(f"Campo preenchido: {value[:10]}...")
            return True
            
        except Exception as e:
            self.log.error(f"Falha ao preencher campo: {e}")
            return False
    
    def _fill_direct(self, value: str) -> bool:
        """Tenta preencher campo focado atualmente."""
        try:
            self.keyboard.send_keys(value)
            return True
        except Exception as e:
            self.log.error(f"Falha no fill direto: {e}")
            return False
    
    def fill_multiple(self, fields: Dict[str, str]) -> Dict[str, bool]:
        """Preenche múltiplos campos."""
        results = {}
        for label, value in fields.items():
            results[label] = self.fill(label, value)
            time.sleep(0.2)
        return results
    
    def fill_by_type(self, field_type: str, value: str) -> bool:
        """Preenche campo por tipo conhecido."""
        if field_type not in FORM_LABELS:
            self.log.error(f"Tipo desconhecido: {field_type}")
            return False
        
        for label_variation in FORM_LABELS[field_type]:
            if self.fill(label_variation, value, field_type):
                return True
        
        return False
