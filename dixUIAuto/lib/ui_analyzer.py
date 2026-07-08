"""
dixUIAuto - UI Analyzer Avançado
Análise semântica, detecção de padrões e resolução de ambiguidades
"""
import re
from typing import List, Dict, Optional, Tuple, Set
from collections import defaultdict
from lib.parser import UINode
from lib.logs import logger


class UIAnalyzer:
    """
    Analisador avançado de UI para detecção de padrões e resolução de ambiguidades.
    
    Recursos:
    - Detecção de listas/scrollables
    - Mapeamento de campos relacionados (label + input)
    - Identificação de padrões repetitivos
    - Resolução de seletores ambíguos
    - Análise de contexto semântico
    """
    
    def __init__(self):
        self.log = logger.get_logger("UIAnalyzer")
    
    def analyze_structure(self, root: UINode) -> Dict:
        """
        Analisa estrutura completa da UI.
        
        Returns:
            Dicionário com análise estrutural
        """
        all_nodes = root.get_all_descendants()
        
        analysis = {
            "total_nodes": len(all_nodes),
            "clickable_count": sum(1 for n in all_nodes if n.clickable),
            "input_count": sum(1 for n in all_nodes if 'EditText' in n.class_name or n.focusable),
            "button_count": sum(1 for n in all_nodes if n.clickable and ('Button' in n.class_name or n.long_clickable)),
            "list_count": sum(1 for n in all_nodes if n.scrollable or 'List' in n.class_name or 'Recycler' in n.class_name),
            "image_count": sum(1 for n in all_nodes if 'Image' in n.class_name),
            "text_count": sum(1 for n in all_nodes if n.text and len(n.text.strip()) > 0),
            "max_depth": max((n.depth for n in all_nodes), default=0),
            "framework": self._detect_framework(all_nodes),
        }
        
        return analysis
    
    def _detect_framework(self, nodes: List[UINode]) -> str:
        """Detecta framework UI usado."""
        class_names = [n.class_name for n in nodes]
        
        # Jetpack Compose
        if any('Compose' in c or 'androidx.compose' in c for c in class_names):
            return "Jetpack Compose"
        
        # Flutter
        if any('Flutter' in c or 'io.flutter' in c for c in class_names):
            return "Flutter"
        
        # WebView
        if any('WebView' in c or 'chromium' in c for c in class_names):
            return "WebView"
        
        return "Android Views"
    
    def find_lists(self, root: UINode) -> List[Dict]:
        """
        Encontra todas as listas/scrollables na tela.
        
        Returns:
            Lista de dicionários com informações das listas
        """
        all_nodes = root.get_all_descendants()
        lists = []
        
        for node in all_nodes:
            if node.scrollable or 'List' in node.class_name or 'Recycler' in node.class_name:
                list_info = {
                    "node": node,
                    "resource_id": node.resource_id,
                    "class": node.class_name,
                    "bounds": node.bounds,
                    "item_count": len(node.children) if node.children else 0,
                    "scrollable": node.scrollable,
                }
                lists.append(list_info)
        
        self.log.debug(f"Encontradas {len(lists)} listas")
        return lists
    
    def find_form_fields(self, root: UINode) -> List[Dict]:
        """
        Encontra campos de formulário e seus labels associados.
        
        Returns:
            Lista de campos com labels mapeados
        """
        all_nodes = root.get_all_descendants()
        fields = []
        
        # Encontrar todos os inputs
        inputs = [n for n in all_nodes if 'EditText' in n.class_name or n.focusable]
        
        for input_node in inputs:
            field_info = {
                "input_node": input_node,
                "input_id": input_node.resource_id,
                "input_bounds": input_node.bounds,
                "label": None,
                "label_node": None,
                "placeholder": input_node.content_desc if not input_node.text else None,
            }
            
            # Tentar encontrar label próximo
            label = self._find_associated_label(input_node, all_nodes)
            if label:
                field_info["label"] = label.text if label else None
                field_info["label_node"] = label
            
            fields.append(field_info)
        
        self.log.debug(f"Encontrados {len(fields)} campos de formulário")
        return fields
    
    def _find_associated_label(self, input_node: UINode, all_nodes: List[UINode]) -> Optional[UINode]:
        """
        Encontra label associado a um campo de input.
        
        Estratégias:
        1. Irmão anterior mais próximo
        2. Pai com texto
        3. Nó acima na hierarquia com proximidade vertical
        """
        # Estratégia 1: Irmão anterior
        if input_node.parent and input_node.parent.children:
            siblings = input_node.parent.children
            idx = siblings.index(input_node) if input_node in siblings else -1
            
            if idx > 0:
                # Verificar irmãos anteriores
                for i in range(idx - 1, -1, -1):
                    sibling = siblings[i]
                    if sibling.text and len(sibling.text.strip()) > 0 and not sibling.clickable:
                        # Verificar se está acima verticalmente
                        if sibling.bounds[1] < input_node.bounds[1]:
                            return sibling
        
        # Estratégia 2: Buscar por proximidade vertical
        input_top = input_node.bounds[1]
        candidates = []
        
        for node in all_nodes:
            if node == input_node:
                continue
            if node.text and len(node.text.strip()) > 0 and not node.clickable:
                # Deve estar acima do input
                if node.bounds[3] <= input_top:
                    distance = input_top - node.bounds[3]
                    # Dentro de um limite razoável (100px)
                    if distance < 100:
                        candidates.append((distance, node))
        
        if candidates:
            candidates.sort(key=lambda x: x[0])
            return candidates[0][1]
        
        return None
    
    def detect_repeating_patterns(self, root: UINode) -> List[Dict]:
        """
        Detecta padrões repetitivos na UI (útil para listas dinâmicas).
        
        Returns:
            Lista de padrões encontrados
        """
        all_nodes = root.get_all_descendants()
        
        # Agrupar por classe + estrutura
        patterns = defaultdict(list)
        
        for node in all_nodes:
            # Criar assinatura do padrão
            signature = f"{node.class_name}|{node.clickable}|{node.scrollable}"
            patterns[signature].append(node)
        
        repeating = []
        for signature, nodes in patterns.items():
            if len(nodes) > 1:
                repeating.append({
                    "signature": signature,
                    "count": len(nodes),
                    "nodes": nodes,
                    "sample_resource_id": nodes[0].resource_id,
                })
        
        # Ordenar por count decrescente
        repeating.sort(key=lambda x: x["count"], reverse=True)
        
        return repeating
    
    def resolve_ambiguous_selector(self, criteria: Dict, all_nodes: List[UINode]) -> Optional[UINode]:
        """
        Resolve seletor ambíguo quando múltiplos nós correspondem.
        
        Estratégias:
        1. Preferir nó mais visível (maior área)
        2. Preferir nó mais profundo (mais específico)
        3. Preferir nó com mais atributos preenchidos
        4. Usar contexto espacial
        """
        matches = self._find_matches(criteria, all_nodes)
        
        if not matches:
            return None
        
        if len(matches) == 1:
            return matches[0]
        
        self.log.warning(f"Seletor ambíguo: {len(matches)} matches, resolvendo...")
        
        # Score cada nó
        scored = []
        for node in matches:
            score = self._score_node(node, criteria)
            scored.append((score, node))
        
        # Retornar melhor score
        scored.sort(key=lambda x: x[0], reverse=True)
        best_node = scored[0][1]
        
        self.log.info(f"Selecionado nó com score {scored[0][0]:.2f}")
        return best_node
    
    def _find_matches(self, criteria: Dict, all_nodes: List[UINode]) -> List[UINode]:
        """Encontra todos os nós que correspondem aos critérios."""
        matches = []
        
        for node in all_nodes:
            match = True
            
            if "text" in criteria and criteria["text"]:
                if node.text != criteria["text"]:
                    match = False
            
            if "text_contains" in criteria and criteria["text_contains"]:
                if not criteria["text_contains"] in (node.text or ""):
                    match = False
            
            if "desc" in criteria and criteria["desc"]:
                if node.content_desc != criteria["desc"]:
                    match = False
            
            if "resource_id" in criteria and criteria["resource_id"]:
                if not criteria["resource_id"] in (node.resource_id or ""):
                    match = False
            
            if "class" in criteria and criteria["class"]:
                if criteria["class"] not in node.class_name:
                    match = False
            
            if "clickable" in criteria and criteria["clickable"] is not None:
                if node.clickable != criteria["clickable"]:
                    match = False
            
            if match:
                matches.append(node)
        
        return matches
    
    def _score_node(self, node: UINode, criteria: Dict) -> float:
        """Calcula score de relevância para um nó."""
        score = 0.0
        
        # Área maior = mais visível
        area = (node.bounds[2] - node.bounds[0]) * (node.bounds[3] - node.bounds[1])
        score += min(area / 100000, 0.3)  # Max 0.3
        
        # Profundidade maior = mais específico
        score += min(node.depth * 0.05, 0.2)  # Max 0.2
        
        # Mais atributos preenchidos = melhor
        attr_count = sum([
            1 if node.text else 0,
            1 if node.content_desc else 0,
            1 if node.resource_id else 0,
            1 if node.class_name else 0,
        ])
        score += min(attr_count * 0.1, 0.3)  # Max 0.3
        
        # É clicável (se relevante)
        if node.clickable:
            score += 0.2
        
        return min(score, 1.0)
    
    def get_context_around(self, node: UINode, radius: int = 2) -> Dict:
        """
        Obtém contexto ao redor de um nó (irmãos, pai, filhos).
        
        Args:
            node: Nó de referência
            radius: Quantos níveis subir/descer
        
        Returns:
            Dicionário com contexto
        """
        context = {
            "target": {
                "text": node.text,
                "desc": node.content_desc,
                "resource_id": node.resource_id,
                "class": node.class_name,
            },
            "parent": None,
            "siblings": [],
            "children": [],
        }
        
        # Pai
        if node.parent:
            context["parent"] = {
                "text": node.parent.text,
                "desc": node.parent.content_desc,
                "resource_id": node.parent.resource_id,
                "class": node.parent.class_name,
            }
        
        # Irmãos
        if node.parent and node.parent.children:
            for sibling in node.parent.children:
                if sibling != node:
                    context["siblings"].append({
                        "text": sibling.text,
                        "desc": sibling.content_desc,
                        "resource_id": sibling.resource_id,
                        "class": sibling.class_name,
                        "clickable": sibling.clickable,
                    })
        
        # Filhos
        if node.children:
            for child in node.children[:10]:  # Limitar a 10
                context["children"].append({
                    "text": child.text,
                    "desc": child.content_desc,
                    "resource_id": child.resource_id,
                    "class": child.class_name,
                })
        
        return context


# Export
__all__ = ['UIAnalyzer']
