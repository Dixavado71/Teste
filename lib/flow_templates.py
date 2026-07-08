"""
Flow Templates - Common flow patterns and templates for reuse.

Provides pre-built flow templates for common automation scenarios.
"""

from typing import List, Dict, Any, Optional


# === Login Templates ===

def login_flow(package: str,
               cpf: str,
               password: str,
               login_button: str = "Entrar",
               cpf_label: str = "Número de CPF",
               password_label: str = "Senha") -> List[Dict[str, Any]]:
    """
    Standard login flow with CPF and password.
    
    Args:
        package: App package name
        cpf: CPF value
        password: Password value
        login_button: Text on login button
        cpf_label: Label for CPF field
        password_label: Label for password field
    
    Returns:
        Flow as list of action dictionaries
    """
    return [
        {'action': 'open_app', 'package': package},
        {'action': 'wait_for', 'text': 'Já tenho uma conta', 'timeout': 10},
        {'action': 'click', 'text': 'Já tenho uma conta'},
        {'action': 'wait_for', 'text': 'Forma de entrar', 'timeout': 5},
        {'action': 'click', 'desc': 'CPF'},
        {'action': 'wait_for', 'label': cpf_label, 'timeout': 5},
        {'action': 'fill', 'label': cpf_label, 'value': cpf, 'field_type': 'cpf'},
        {'action': 'fill', 'label': password_label, 'value': password, 'field_type': 'password'},
        {'action': 'screenshot', 'name': 'pre_login'},
        {'action': 'click', 'text': login_button},
        {'action': 'wait_for', 'text': 'Home', 'timeout': 10},
        {'action': 'screenshot', 'name': 'post_login'}
    ]


def login_with_email(package: str,
                     email: str,
                     password: str,
                     login_button: str = "Entrar") -> List[Dict[str, Any]]:
    """Login flow with email and password."""
    return [
        {'action': 'open_app', 'package': package},
        {'action': 'wait_for', 'text': 'E-mail', 'timeout': 10},
        {'action': 'fill', 'label': 'E-mail', 'value': email},
        {'action': 'fill', 'label': 'Senha', 'value': password, 'field_type': 'password'},
        {'action': 'click', 'text': login_button},
        {'action': 'wait_for', 'timeout': 5}
    ]


# === Registration Templates ===

def basic_registration(full_name: str,
                       email: str,
                       phone: str,
                       password: str,
                       confirm_password: str,
                       package: str = "com.default.app") -> List[Dict[str, Any]]:
    """Basic registration flow."""
    return [
        {'action': 'open_app', 'package': package},
        {'action': 'wait_for', 'text': 'Criar conta', 'timeout': 10},
        {'action': 'click', 'text': 'Criar conta'},
        {'action': 'fill', 'label': 'Nome completo', 'value': full_name},
        {'action': 'fill', 'label': 'E-mail', 'value': email},
        {'action': 'fill', 'label': 'Telefone', 'value': phone, 'field_type': 'phone'},
        {'action': 'fill', 'label': 'Senha', 'value': password, 'field_type': 'password'},
        {'action': 'fill', 'label': 'Confirmar senha', 'value': confirm_password, 'field_type': 'password'},
        {'action': 'click', 'text': 'Cadastrar'},
        {'action': 'wait_for', 'timeout': 5}
    ]


def registration_with_cpf(cpf: str,
                          full_name: str,
                          email: str,
                          phone: str,
                          password: str,
                          package: str = "com.default.app") -> List[Dict[str, Any]]:
    """Registration flow with CPF validation."""
    return [
        {'action': 'open_app', 'package': package},
        {'action': 'click', 'text': 'Criar conta'},
        {'action': 'fill', 'label': 'CPF', 'value': cpf, 'field_type': 'cpf'},
        {'action': 'wait', 'seconds': 1},
        {'action': 'fill', 'label': 'Nome completo', 'value': full_name},
        {'action': 'fill', 'label': 'E-mail', 'value': email},
        {'action': 'fill', 'label': 'Celular', 'value': phone},
        {'action': 'fill', 'label': 'Senha', 'value': password},
        {'action': 'click', 'text': 'Continuar'},
        {'action': 'wait_for', 'timeout': 5}
    ]


# === Payment Templates ===

def credit_card_payment(package: str,
                        card_number: str,
                        card_holder: str,
                        expiry_date: str,
                        cvv: str,
                        installments: int = 1) -> List[Dict[str, Any]]:
    """Credit card payment flow."""
    return [
        {'action': 'wait_for', 'text': 'Pagamento', 'timeout': 10},
        {'action': 'click', 'text': 'Cartão de crédito'},
        {'action': 'fill', 'label': 'Número do cartão', 'value': card_number},
        {'action': 'fill', 'label': 'Nome no cartão', 'value': card_holder},
        {'action': 'fill', 'label': 'Validade', 'value': expiry_date},
        {'action': 'fill', 'label': 'CVV', 'value': cvv},
        {'action': 'wait', 'seconds': 0.5},
        {'action': 'click', 'text': 'Parcelas'},
        {'action': 'click', 'text': f'{installments}x'},
        {'action': 'click', 'text': 'Confirmar pagamento'},
        {'action': 'wait_for', 'timeout': 5}
    ]


def pix_payment(package: str) -> List[Dict[str, Any]]:
    """PIX payment flow (copies QR code)."""
    return [
        {'action': 'wait_for', 'text': 'Pagamento', 'timeout': 10},
        {'action': 'click', 'text': 'PIX'},
        {'action': 'wait_for', 'text': 'QR Code', 'timeout': 5},
        {'action': 'click', 'text': 'Copiar código PIX'},
        {'action': 'wait', 'seconds': 2},
        {'action': 'screenshot', 'name': 'pix_qrcode'}
    ]


# === Navigation Templates ===

def scroll_to_and_click(text: str,
                        direction: str = 'down',
                        max_swipes: int = 10) -> List[Dict[str, Any]]:
    """Scroll until finding text and click it."""
    return [
        {'action': 'scroll_to', 'text': text, 'direction': direction, 'max_swipes': max_swipes},
        {'action': 'click', 'text': text}
    ]


def navigate_through_screens(screen_texts: List[str]) -> List[Dict[str, Any]]:
    """Navigate through multiple screens by clicking texts in sequence."""
    flow = []
    for text in screen_texts:
        flow.append({'action': 'wait_for', 'text': text, 'timeout': 5})
        flow.append({'action': 'click', 'text': text})
    return flow


# === Form Templates ===

def fill_personal_data(full_name: str,
                       cpf: str,
                       email: str,
                       phone: str,
                       birthdate: str,
                       cep: str) -> List[Dict[str, Any]]:
    """Fill complete personal data form."""
    return [
        {'action': 'fill', 'label': 'Nome completo', 'value': full_name},
        {'action': 'fill', 'label': 'CPF', 'value': cpf},
        {'action': 'fill', 'label': 'E-mail', 'value': email},
        {'action': 'fill', 'label': 'Telefone', 'value': phone},
        {'action': 'fill', 'label': 'Data de nascimento', 'value': birthdate},
        {'action': 'fill', 'label': 'CEP', 'value': cep},
        {'action': 'wait', 'seconds': 1}  # Wait for address lookup
    ]


def fill_address(cep: str,
                 number: str,
                 complement: Optional[str] = None) -> List[Dict[str, Any]]:
    """Fill address form using CEP auto-complete."""
    flow = [
        {'action': 'fill', 'label': 'CEP', 'value': cep},
        {'action': 'wait', 'seconds': 2},  # Wait for auto-complete
        {'action': 'fill', 'label': 'Número', 'value': number}
    ]
    if complement:
        flow.append({'action': 'fill', 'label': 'Complemento', 'value': complement})
    return flow


# === Verification Templates ===

def verify_login_success(home_text: str = "Home") -> List[Dict[str, Any]]:
    """Verify successful login."""
    return [
        {'action': 'assert_exists', 'text': home_text},
        {'action': 'screenshot', 'name': 'login_success'}
    ]


def verify_form_filled(label: str, expected_value: str) -> List[Dict[str, Any]]:
    """Verify a form field is correctly filled."""
    return [
        {'action': 'validate_field', 'label': label, 'expected_value': expected_value}
    ]


def assert_no_errors() -> List[Dict[str, Any]]:
    """Assert no error messages are visible."""
    return [
        {'action': 'assert_not_exists', 'text': 'Erro'},
        {'action': 'assert_not_exists', 'text': 'Falha'},
        {'action': 'assert_not_exists', 'text': 'Inválido'}
    ]


# === Error Recovery Templates ===

def retry_on_error(max_retries: int = 3) -> List[Dict[str, Any]]:
    """Template for retry configuration."""
    return [
        {'action': 'config', 'retry_count': max_retries}
    ]


def handle_popup(popup_text: str,
                 action: str = 'close') -> List[Dict[str, Any]]:
    """Handle popup dialogs."""
    if action == 'close':
        return [
            {'action': 'click_if_exists', 'text': popup_text},
            {'action': 'click_if_exists', 'text': 'Fechar'},
            {'action': 'click_if_exists', 'text': 'OK'}
        ]
    elif action == 'accept':
        return [
            {'action': 'click_if_exists', 'text': popup_text},
            {'action': 'click_if_exists', 'text': 'Aceitar'},
            {'action': 'click_if_exists', 'text': 'Sim'}
        ]
    return []


# === Utility Templates ===

def setup_app(package: str,
              clear_data: bool = True,
              permissions: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """Setup app for testing."""
    flow = []
    
    if clear_data:
        flow.append({'action': 'shell', 'command': f'pm clear {package}'})
    
    flow.append({'action': 'open_app', 'package': package})
    
    if permissions:
        for perm in permissions:
            flow.append({
                'action': 'set_permission',
                'permission': perm,
                'value': True
            })
    
    return flow


def teardown_app(package: str,
                 clear_data: bool = True) -> List[Dict[str, Any]]:
    """Teardown app after testing."""
    flow = [
        {'action': 'back'},
        {'action': 'home'}
    ]
    
    if clear_data:
        flow.append({'action': 'shell', 'command': f'pm clear {package}'})
    
    return flow


# === Template Registry ===

TEMPLATES = {
    'login': login_flow,
    'login_email': login_with_email,
    'registration': basic_registration,
    'registration_cpf': registration_with_cpf,
    'payment_card': credit_card_payment,
    'payment_pix': pix_payment,
    'scroll_click': scroll_to_and_click,
    'navigate': navigate_through_screens,
    'personal_data': fill_personal_data,
    'address': fill_address,
    'verify_login': verify_login_success,
    'verify_field': verify_form_filled,
    'no_errors': assert_no_errors,
    'setup_app': setup_app,
    'teardown_app': teardown_app,
    'handle_popup': handle_popup
}


def get_template(name: str, *args, **kwargs) -> Optional[List[Dict[str, Any]]]:
    """
    Get a flow template by name.
    
    Args:
        name: Template name
        *args: Positional arguments for the template
        **kwargs: Keyword arguments for the template
    
    Returns:
        Flow as list of action dictionaries, or None if not found
    """
    template_func = TEMPLATES.get(name)
    if template_func:
        # Filter out 'name' from kwargs to avoid conflict
        filtered_kwargs = {k: v for k, v in kwargs.items() if k != 'name'}
        return template_func(*args, **filtered_kwargs)
    return None


def list_templates() -> List[str]:
    """List all available template names."""
    return list(TEMPLATES.keys())


def register_template(name: str, func) -> None:
    """Register a custom template."""
    TEMPLATES[name] = func
