"""
Smart Inspector - Inspeção inteligente da UI com geração de seletores
"""
import re
from typing import List, Dict, Optional, Tuple
from lib.parser import UINode, XMLParser
from lib.logs import logger


class SelectorSuggestion:
    """Sugestão de seletor com score de confiança."""
    
    def __init__(self, strategy: str, value: str, score: float, 
                 description: str = ""):
        self.strategy = strategy
        self.value = value
        self.score = score  # 0-1
        self.description = description
    
    def to_dict(self) -> Dict:
        return {
            "strategy": self.strategy,
            "value": self.value,
            "score": round(self.score, 2),
            "description": self.description
        }
    
    def __repr__(self):
        return f"{self.strategy}='{self.value}' (score: {self.score:.2f})"


class SmartInspector:
    """
    Analisa a árvore UI e sugere os melhores seletores.
    Heurísticas incluem: estabilidade, unicidade, semântica.
    """
    
    def __init__(self):
        self.log = logger.get_logger("Inspector")
    
    def analyze_node(self, node: UINode, all_nodes: List[UINode]) -> List[SelectorSuggestion]:
        """Analisa nó e retorna sugestões ordenadas por score."""
        suggestions = []
        
        # 1. resource-id (mais estável)
        if node.resource_id:
            # Verificar unicidade
            matches = [n for n in all_nodes if n.resource_id == node.resource_id]
            uniqueness = 1.0 if len(matches) == 1 else 0.5 / len(matches)
            suggestions.append(SelectorSuggestion(
                "resource_id",
                node.resource_id,
                score=0.95 * uniqueness,
                description="ID do recurso (alto)" if uniqueness == 1 else "ID compartilhado"
            ))
        
        # 2. content-desc (bom para acessibilidade)
        if node.content_desc:
            matches = [n for n in all_nodes if n.content_desc == node.content_desc]
            uniqueness = 1.0 if len(matches) == 1 else 0.5 / len(matches)
            suggestions.append(SelectorSuggestion(
                "content_desc",
                node.content_desc,
                score=0.90 * uniqueness,
                description="Descrição de conteúdo"
            ))
        
        # 3. text (se único e significativo)
        if node.text and len(node.text.strip()) > 2:
            matches = [n for n in all_nodes if n.text == node.text]
            uniqueness = 1.0 if len(matches) == 1 else 0.4 / len(matches)
            suggestions.append(SelectorSuggestion(
                "text",
                node.text,
                score=0.85 * uniqueness,
                description="Texto exato"
            ))
            
            # Text contains (menos específico)
            if len(node.text) > 5:
                suggestions.append(SelectorSuggestion(
                    "text_contains",
                    node.text[:20],
                    score=0.60,
                    description="Contém texto"
                ))
        
        # 4. class + atributos combinados
        class_name = node.class_name.split('.')[-1] if '.' in node.class_name else node.class_name
        
        if node.clickable:
            suggestions.append(SelectorSuggestion(
                "class_clickable",
                class_name,
                score=0.50,
                description=f"{class_name} clicável"
            ))
        
        # 5. XPath para casos complexos
        xpath = self._generate_xpath(node)
        if xpath:
            suggestions.append(SelectorSuggestion(
                "xpath",
                xpath,
                score=0.40,
                description="XPath (use com cuidado)"
            ))
        
        # Ordenar por score
        suggestions.sort(key=lambda s: s.score, reverse=True)
        
        return suggestions
    
    def _generate_xpath(self, node: UINode) -> str:
        """Gera XPath simplificado."""
        class_name = node.class_name.split('.')[-1] if '.' in node.class_name else node.class_name
        
        if node.resource_id:
            short_id = node.resource_id.split('/')[-1]
            return f"//{class_name}[@resource-id='{short_id}']"
        
        if node.text and len(node.text) < 30:
            safe_text = node.text.replace("'", "&apos;")
            return f"//{class_name}[@text='{safe_text}']"
        
        if node.content_desc:
            return f"//{class_name}[@content-desc='{node.content_desc}']"
        
        return f"//{class_name}"
    
    def find_best_selector(self, node: UINode, all_nodes: List[UINode]) -> Optional[SelectorSuggestion]:
        """Retorna o melhor seletor para um nó."""
        suggestions = self.analyze_node(node, all_nodes)
        return suggestions[0] if suggestions else None
    
    def detect_ui_framework(self, root: UINode) -> str:
        """Detecta framework UI usado (Views, Compose, Flutter)."""
        all_nodes = root.get_all_descendants()
        class_names = [n.class_name for n in all_nodes]
        
        # Jetpack Compose
        compose_patterns = ['Compose', 'androidx.compose']
        if any(any(p in c for p in compose_patterns) for c in class_names):
            return "Jetpack Compose"
        
        # Flutter
        flutter_patterns = ['Flutter', 'io.flutter']
        if any(any(p in c for p in flutter_patterns) for c in class_names):
            return "Flutter"
        
        # WebView
        webview_patterns = ['WebView', 'chromium']
        if any(any(p in c for p in webview_patterns) for c in class_names):
            return "WebView"
        
        return "Android Views"
    
    def get_semantic_info(self, node: UINode) -> Dict:
        """Extrai informação semântica do nó."""
        info = {
            "is_button": node.clickable and ('Button' in node.class_name or node.long_clickable),
            "is_input": 'EditText' in node.class_name or node.focusable,
            "is_label": node.text and not node.clickable and len(node.text) < 50,
            "is_image": 'Image' in node.class_name,
            "is_list": 'List' in node.class_name or 'Recycler' in node.class_name,
            "is_scrollable": node.scrollable,
            "is_password": node.password,
            "depth": node.depth,
        }
        info["role"] = self._infer_role(node, info)
        return info
    
    def _infer_role(self, node: UINode, info: Dict) -> str:
        """Inferir papel/função do elemento."""
        if info["is_input"]:
            if node.password:
                return "password_field"
            return "text_input"
        if info["is_button"]:
            return "button"
        if info["is_label"]:
            return "label"
        if info["is_list"]:
            return "list"
        if info["is_image"]:
            return "image"
        return "unknown"
