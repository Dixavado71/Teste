"""
dixUIAuto - Flow Templates e Gerador de Flows Dinâmicos
Templates reutilizáveis e geração inteligente de fluxos
"""
import json
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path
from lib.logs import logger


class FlowTemplate:
    """Template de flow reutilizável com parâmetros dinâmicos."""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.steps: List[Dict] = []
        self.params: Dict[str, Any] = {}
        self.log = logger.get_logger("FlowTemplate")
    
    def add_step(self, action: str, **kwargs) -> 'FlowTemplate':
        """Adiciona passo ao template."""
        step = {"action": action}
        step.update(kwargs)
        self.steps.append(step)
        return self
    
    def set_params(self, **params) -> 'FlowTemplate':
        """Define parâmetros do template."""
        self.params.update(params)
        return self
    
    def resolve(self, **overrides) -> List[Dict]:
        """
        Resolve template substituindo variáveis.
        
        Args:
            **overrides: Valores para substituir nos templates
        
        Returns:
            Lista de passos resolvidos
        """
        params = {**self.params, **overrides}
        resolved_steps = []
        
        for step in self.steps:
            resolved_step = {}
            for key, value in step.items():
                if isinstance(value, str):
                    # Substituir {{param}} pelos valores
                    resolved_value = value
                    for param_name, param_value in params.items():
                        resolved_value = resolved_value.replace(
                            f"{{{{{param_name}}}}}", 
                            str(param_value)
                        )
                    resolved_step[key] = resolved_value
                else:
                    resolved_step[key] = value
            resolved_steps.append(resolved_step)
        
        return resolved_steps
    
    def save(self, filepath: str) -> str:
        """Salva template como JSON."""
        path = Path(filepath)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump({
                "name": self.name,
                "description": self.description,
                "params": self.params,
                "steps": self.steps
            }, f, indent=2, ensure_ascii=False)
        
        self.log.info(f"Template salvo: {path}")
        return str(path)
    
    @classmethod
    def load(cls, filepath: str) -> 'FlowTemplate':
        """Carrega template de JSON."""
        path = Path(filepath)
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        template = cls(data.get("name", "template"), data.get("description", ""))
        template.steps = data.get("steps", [])
        template.params = data.get("params", {})
        
        return template


class TemplateLibrary:
    """Biblioteca de templates pré-definidos."""
    
    def __init__(self):
        self.log = logger.get_logger("TemplateLibrary")
        self._templates: Dict[str, FlowTemplate] = {}
        self._register_builtin_templates()
    
    def _register_builtin_templates(self):
        """Registra templates built-in."""
        
        # Template de Login
        login = FlowTemplate("login", "Login com credenciais")
        login.add_step("wait", text="{{login_button_text}}", timeout=10)
        login.add_step("click", text="{{login_button_text}}")
        login.add_step("fill", label="{{username_label}}", value="{{username}}")
        login.add_step("fill", label="{{password_label}}", value="{{password}}")
        login.add_step("click", text="{{submit_button_text}}")
        login.set_params(
            login_button_text="Entrar",
            username_label="Usuário ou Email",
            password_label="Senha",
            submit_button_text="Acessar"
        )
        self.register("login", login)
        
        # Template de Cadastro
        cadastro = FlowTemplate("cadastro", "Cadastro de usuário")
        cadastro.add_step("click", text="{{register_button_text}}")
        cadastro.add_step("fill", label="{{name_label}}", value="{{full_name}}")
        cadastro.add_step("fill", label="{{email_label}}", value="{{email}}")
        cadastro.add_step("fill", label="{{cpf_label}}", value="{{cpf}}")
        cadastro.add_step("fill", label="{{phone_label}}", value="{{phone}}")
        cadastro.add_step("fill", label="{{password_label}}", value="{{password}}")
        cadastro.add_step("fill", label="{{confirm_password_label}}", value="{{password}}")
        cadastro.add_step("click", text="{{submit_button_text}}")
        cadastro.set_params(
            register_button_text="Criar conta",
            name_label="Nome completo",
            email_label="E-mail",
            cpf_label="CPF",
            phone_label="Telefone",
            password_label="Senha",
            confirm_password_label="Confirmar senha",
            submit_button_text="Cadastrar"
        )
        self.register("cadastro", cadastro)
        
        # Template de Navegação
        nav = FlowTemplate("navigation", "Navegação entre telas")
        nav.add_step("wait", text="{{screen_title}}", timeout=5)
        nav.add_step("scroll", direction="{{scroll_direction}}", steps=2)
        nav.add_step("click", text="{{target_text}}")
        nav.add_step("wait", seconds=2)
        nav.set_params(
            screen_title="",
            scroll_direction="down",
            target_text=""
        )
        self.register("navigation", nav)
        
        # Template de Formulário Genérico
        form = FlowTemplate("form_fill", "Preenchimento de formulário")
        form.add_step("wait", text="{{form_title}}", timeout=5)
        form.add_step("fill", label="{{field_1_label}}", value="{{field_1_value}}")
        form.add_step("fill", label="{{field_2_label}}", value="{{field_2_value}}")
        form.add_step("fill", label="{{field_3_label}}", value="{{field_3_value}}")
        form.add_step("click", text="{{submit_button_text}}")
        form.set_params(
            form_title="",
            field_1_label="",
            field_1_value="",
            field_2_label="",
            field_2_value="",
            field_3_label="",
            field_3_value="",
            submit_button_text="Enviar"
        )
        self.register("form_fill", form)
        
        # Template de Validação
        validation = FlowTemplate("validation", "Validação de tela")
        validation.add_step("assert", text="{{expected_text}}", exists=True)
        validation.add_step("screenshot", filename="{{screenshot_name}}")
        validation.set_params(
            expected_text="",
            screenshot_name="validation.png"
        )
        self.register("validation", validation)
        
        # Template de Logout
        logout = FlowTemplate("logout", "Logout do aplicativo")
        logout.add_step("click", desc="{{menu_button_desc}}")
        logout.add_step("click", text="{{logout_button_text}}")
        logout.add_step("wait", text="{{login_screen_text}}", timeout=5)
        logout.set_params(
            menu_button_desc="Menu",
            logout_button_text="Sair",
            login_screen_text="Entrar"
        )
        self.register("logout", logout)
    
    def register(self, name: str, template: FlowTemplate):
        """Registra template na biblioteca."""
        self._templates[name] = template
        self.log.info(f"Template registrado: {name}")
    
    def get(self, name: str) -> Optional[FlowTemplate]:
        """Obtém template por nome."""
        return self._templates.get(name)
    
    def list_templates(self) -> List[str]:
        """Lista todos os templates disponíveis."""
        return list(self._templates.keys())
    
    def create_flow(self, template_name: str, **params) -> List[Dict]:
        """
        Cria flow a partir de template.
        
        Args:
            template_name: Nome do template
            **params: Parâmetros para resolver o template
        
        Returns:
            Lista de passos do flow
        """
        template = self.get(template_name)
        if not template:
            raise ValueError(f"Template não encontrado: {template_name}")
        
        return template.resolve(**params)
    
    def combine_flows(self, *template_names: str, **all_params) -> List[Dict]:
        """
        Combina múltiplos templates em um único flow.
        
        Args:
            *template_names: Nomes dos templates
            **all_params: Parâmetros para todos os templates
        
        Returns:
            Flow combinado
        """
        combined = []
        for name in template_names:
            flow = self.create_flow(name, **all_params)
            combined.extend(flow)
        return combined


class FlowBuilder:
    """Construtor fluente de flows."""
    
    def __init__(self, name: str = "flow"):
        self.name = name
        self.steps: List[Dict] = []
        self.log = logger.get_logger("FlowBuilder")
    
    def click(self, text: str = None, desc: str = None, 
              resource_id: str = None, **kwargs) -> 'FlowBuilder':
        """Adiciona ação de clique."""
        step = {"action": "click"}
        if text:
            step["text"] = text
        if desc:
            step["desc"] = desc
        if resource_id:
            step["resource_id"] = resource_id
        step.update(kwargs)
        self.steps.append(step)
        return self
    
    def fill(self, label: str, value: str) -> 'FlowBuilder':
        """Adiciona ação de preenchimento."""
        self.steps.append({
            "action": "fill",
            "label": label,
            "value": value
        })
        return self
    
    def wait(self, seconds: int = 1, text: str = None) -> 'FlowBuilder':
        """Adiciona ação de espera."""
        step = {"action": "wait"}
        if text:
            step["text"] = text
        else:
            step["seconds"] = seconds
        self.steps.append(step)
        return self
    
    def scroll(self, direction: str = "down", steps: int = 1) -> 'FlowBuilder':
        """Adiciona ação de scroll."""
        self.steps.append({
            "action": "scroll",
            "direction": direction,
            "steps": steps
        })
        return self
    
    def assert_exists(self, text: str, exists: bool = True) -> 'FlowBuilder':
        """Adiciona validação."""
        self.steps.append({
            "action": "assert",
            "text": text,
            "exists": exists
        })
        return self
    
    def screenshot(self, filename: str = None) -> 'FlowBuilder':
        """Adiciona screenshot."""
        self.steps.append({
            "action": "screenshot",
            "filename": filename
        })
        return self
    
    def custom(self, action: str, **kwargs) -> 'FlowBuilder':
        """Adiciona ação customizada."""
        step = {"action": action}
        step.update(kwargs)
        self.steps.append(step)
        return self
    
    def build(self) -> List[Dict]:
        """Retorna flow construído."""
        return self.steps.copy()
    
    def save(self, filepath: str) -> str:
        """Salva flow como JSON."""
        path = Path(filepath)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.steps, f, indent=2, ensure_ascii=False)
        
        self.log.info(f"Flow salvo: {path}")
        return str(path)
    
    def execute(self, engine) -> bool:
        """Executa flow diretamente."""
        return engine.flow.execute(self.steps)


# Export
__all__ = ['FlowTemplate', 'TemplateLibrary', 'FlowBuilder']
