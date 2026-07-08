"""
dixUIAuto - Code Generator para Flows e Seletores
Geração automática de código Python e JSON a partir de inspeção
"""
import json
from typing import List, Dict, Optional
from pathlib import Path
from lib.logs import logger
from lib.inspector import SelectorSuggestion


class CodeGenerator:
    """
    Gera código Python e JSON automaticamente a partir de seletores e ações.
    
    Recursos:
    - Geração de código Python executável
    - Geração de JSON flows
    - Templates customizáveis
    - Formatação automática
    """
    
    def __init__(self):
        self.log = logger.get_logger("CodeGenerator")
    
    def generate_python(self, actions: List[Dict], 
                       include_imports: bool = True,
                       include_engine_init: bool = True) -> str:
        """
        Gera código Python a partir de lista de ações.
        
        Args:
            actions: Lista de dicionários com ações
            include_imports: Incluir imports no início
            include_engine_init: Incluir inicialização da engine
        
        Returns:
            Código Python formatado
        """
        lines = []
        
        # Imports
        if include_imports:
            lines.extend([
                '"""',
                'Flow gerado automaticamente pelo dixUIAuto',
                '"""',
                'from main import DixEngine',
                '',
                '',
                'def run_flow():',
                '    # Inicializar engine',
                '    engine = DixEngine()',
                '    engine.connect()',
                '',
            ])
        
        # Gerar ações
        for i, action in enumerate(actions, 1):
            action_type = action.get("action", "")
            code = self._generate_action_code(action_type, action)
            if code:
                lines.append(f"    # Passo {i}")
                lines.append(f"    {code}")
                lines.append("")
        
        # Finalização
        if include_engine_init:
            lines.extend([
                '    # Concluir',
                '    engine.disconnect()',
                '',
                '',
                'if __name__ == "__main__":',
                '    run_flow()',
            ])
        
        return "\n".join(lines)
    
    def _generate_action_code(self, action_type: str, params: Dict) -> str:
        """Gera código para uma ação específica."""
        
        if action_type == "click":
            args = []
            if params.get("text"):
                args.append(f'text="{params["text"]}"')
            if params.get("desc"):
                args.append(f'desc="{params["desc"]}"')
            if params.get("resource_id"):
                args.append(f'resource_id="{params["resource_id"]}"')
            
            args_str = ", ".join(args) if args else "**criteria"
            return f'engine.click({args_str})'
        
        elif action_type == "fill":
            label = params.get("label", "")
            value = params.get("value", "")
            return f'engine.form.fill(label="{label}", value="{value}")'
        
        elif action_type == "wait":
            if params.get("text"):
                return f'engine.wait(text="{params["text"]}", timeout={params.get("timeout", 10)})'
            else:
                seconds = params.get("seconds", 1)
                return f'import time; time.sleep({seconds})'
        
        elif action_type == "scroll":
            direction = params.get("direction", "down")
            steps = params.get("steps", 1)
            return f'engine.scroll(direction="{direction}", steps={steps})'
        
        elif action_type == "input":
            text = params.get("text", "")
            return f'engine.input("{text}")'
        
        elif action_type == "screenshot":
            filename = params.get("filename", "")
            if filename:
                return f'engine.screenshot("{filename}")'
            return 'engine.screenshot()'
        
        elif action_type == "assert":
            text = params.get("text", "")
            exists = params.get("exists", True)
            return f'assert engine.validator.exists(text="{text}") == {exists}'
        
        elif action_type == "open":
            package = params.get("package", "")
            return f'engine.open("{package}")'
        
        elif action_type == "close":
            package = params.get("package", "")
            return f'engine.close("{package}")'
        
        return f'# Ação não suportada: {action_type}'
    
    def generate_json(self, actions: List[Dict], pretty: bool = True) -> str:
        """
        Gera JSON flow a partir de lista de ações.
        
        Args:
            actions: Lista de dicionários com ações
            pretty: Format JSON com indentação
        
        Returns:
            JSON string
        """
        if pretty:
            return json.dumps(actions, indent=2, ensure_ascii=False)
        return json.dumps(actions, ensure_ascii=False)
    
    def generate_selector_code(self, suggestion: SelectorSuggestion, 
                               action: str = "click") -> str:
        """
        Gera código Python para usar um seletor sugerido.
        
        Args:
            suggestion: Sugestão de seletor
            action: Tipo de ação (click, wait, etc.)
        
        Returns:
            Código Python
        """
        strategy = suggestion.strategy
        value = suggestion.value.replace('"', '\\"')
        
        if strategy == "resource_id":
            call = f'engine.{action}(resource_id="{value}")'
        elif strategy == "content_desc":
            call = f'engine.{action}(desc="{value}")'
        elif strategy == "text":
            call = f'engine.{action}(text="{value}")'
        elif strategy == "text_contains":
            call = f'# Usar find_text com contains\nnode = engine.finder.find_text("{value}")\nif node: engine.clicker.click(node)'
        elif strategy == "xpath":
            call = f'# XPath (use com cuidado)\n# node = engine.finder.find_xpath("{value}")'
        elif strategy == "class_clickable":
            call = f'# Combinar classe com outros atributos\nnode = engine.finder.find_first(class_name="{value}", clickable=True)'
        else:
            call = f'# Seletor customizado para {strategy}'
        
        # Adicionar comentário com score
        score_emoji = "🟢" if suggestion.score >= 0.7 else "🟡" if suggestion.score >= 0.4 else "🔴"
        comment = f"  # Score: {suggestion.score:.2f} {score_emoji} - {suggestion.description}"
        
        return call + comment
    
    def generate_page_object(self, page_name: str, elements: List[Dict]) -> str:
        """
        Gera classe Page Object a partir de elementos identificados.
        
        Args:
            page_name: Nome da página/classe
            elements: Lista de elementos com nome e seletor
        
        Returns:
            Código Python da classe Page Object
        """
        lines = [
            f'"""',
            f'Page Object: {page_name}',
            f'Gerado automaticamente pelo dixUIAuto',
            f'"""',
            f'from main import DixEngine',
            f'',
            f'',
            f'class {page_name}:',
            f'    """Page Object para {page_name}."""',
            f'',
            f'    def __init__(self, engine: DixEngine):',
            f'        self.engine = engine',
            f'',
        ]
        
        # Adicionar seletores como atributos
        for elem in elements:
            name = elem.get("name", "element")
            selector_type = elem.get("selector_type", "text")
            selector_value = elem.get("selector_value", "")
            
            lines.append(f'        # {name}')
            lines.append(f'        self.{name}_selector = {{')
            lines.append(f'            "{selector_type}": "{selector_value}"')
            lines.append(f'        }}')
            lines.append(f'')
        
        # Adicionar métodos
        lines.append(f'')
        lines.append(f'    def is_visible(self) -> bool:')
        lines.append(f'        """Verifica se a página está visível."""')
        lines.append(f'        # Implementar verificação específica')
        lines.append(f'        return True')
        lines.append(f'')
        
        lines.append(f'    def perform_actions(self, **kwargs):')
        lines.append(f'        """Executa ações na página."""')
        lines.append(f'        # Implementar ações específicas')
        lines.append(f'        pass')
        lines.append(f'')
        
        return "\n".join(lines)
    
    def save_file(self, content: str, filepath: str, mode: str = 'w'):
        """Salva conteúdo em arquivo."""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, mode, encoding='utf-8') as f:
            f.write(content)
        
        self.log.info(f"Arquivo salvo: {path}")
        return str(path)
    
    def generate_from_inspection(self, inspection_data: Dict) -> Dict:
        """
        Gera múltiplos formatos a partir de dados de inspeção.
        
        Args:
            inspection_data: Dados da inspeção contendo:
                - selected_element: Elemento selecionado
                - suggestions: Sugestões de seletores
                - action: Ação desejada
        
        Returns:
            Dicionário com códigos gerados (python, json, markdown)
        """
        element = inspection_data.get("selected_element", {})
        suggestions = inspection_data.get("suggestions", [])
        action = inspection_data.get("action", "click")
        
        result = {
            "python": "",
            "json": "",
            "markdown": "",
        }
        
        # Gerar Python
        if suggestions:
            best_suggestion = suggestions[0]
            result["python"] = self.generate_selector_code(best_suggestion, action)
        
        # Gerar JSON
        json_action = {"action": action}
        if element.get("text"):
            json_action["text"] = element["text"]
        if element.get("content_desc"):
            json_action["desc"] = element["content_desc"]
        if element.get("resource_id"):
            json_action["resource_id"] = element["resource_id"]
        
        result["json"] = self.generate_json([json_action])
        
        # Gerar Markdown documentation
        md_lines = [
            f"## Elemento: {element.get('text', 'Sem texto')}",
            f"",
            f"**Classe:** `{element.get('class_name', '')}`",
            f"**Resource ID:** `{element.get('resource_id', 'N/A')}`",
            f"**Content Desc:** `{element.get('content_desc', 'N/A')}`",
            f"",
            f"### Seletores Sugeridos:",
            f"",
        ]
        
        for i, sug in enumerate(suggestions[:5], 1):
            emoji = "🟢" if sug.score >= 0.7 else "🟡" if sug.score >= 0.4 else "🔴"
            md_lines.append(f"{i}. {emoji} `{sug.strategy}='{sug.value}'` (score: {sug.score:.2f})")
        
        result["markdown"] = "\n".join(md_lines)
        
        return result


# Export
__all__ = ['CodeGenerator']
