"""
Constantes do Framework dixUIAuto
"""

# Tipos de elementos UI
ELEMENT_TYPES = [
    "Button", "TextView", "EditText", "ImageView", "CheckBox",
    "RadioButton", "Spinner", "ListView", "RecyclerView",
    "ScrollView", "ViewPager", "TabLayout", "NavigationBar",
    "Toolbar", "FloatingActionButton", "CardView", "ConstraintLayout",
    "LinearLayout", "RelativeLayout", "FrameLayout"
]

# Estratégias de localização
LOCATOR_STRATEGIES = [
    "text", "text_contains", "text_matches",
    "resource_id", "class_name", "content_desc",
    "xpath", "regex", "bounds", "parent", "child",
    "sibling", "label", "placeholder"
]

# Ações suportadas
ACTIONS = [
    "click", "double_click", "long_click",
    "swipe", "scroll", "drag", "tap",
    "input", "clear", "enter", "backspace",
    "wait", "screenshot", "shell", "assert",
    "fill", "select", "hover", "press_key"
]

# Teclas especiais
KEY_CODES = {
    "ENTER": 66,
    "BACKSPACE": 67,
    "DEL": 67,
    "TAB": 61,
    "SPACE": 62,
    "HOME": 3,
    "END": 123,
    "BACK": 4,
    "MENU": 82,
    "SEARCH": 84
}

# Padrões de validação
PATTERNS = {
    "cpf": r"^\d{3}\.?\d{3}\.?\d{3}-?\d{2}$",
    "cnpj": r"^\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}$",
    "email": r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$",
    "phone": r"^\(?\d{2}\)?\s?\d{4,5}-?\d{4}$",
    "cep": r"^\d{5}-?\d{3}$",
    "date": r"^\d{2}/\d{2}/\d{4}$",
    "time": r"^\d{2}:\d{2}$",
    "currency": r"^R?\$?\s?\d+[,.]?\d*$"
}

# Labels comuns para Smart Form
FORM_LABELS = {
    "cpf": ["CPF", "Número do CPF", "Digite seu CPF"],
    "cnpj": ["CNPJ", "Número do CNPJ"],
    "email": ["Email", "E-mail", "Endereço de email"],
    "password": ["Senha", "Password", "Digite sua senha"],
    "phone": ["Telefone", "Celular", "Número de telefone"],
    "name": ["Nome", "Nome completo", "Seu nome"],
    "cep": ["CEP", "Código Postal"],
    "card_number": ["Número do cartão", "Cartão de crédito"],
    "expiry": ["Validade", "Data de validade"],
    "cvv": ["CVV", "Código de segurança"]
}

# Estados da UI
UI_STATES = ["loading", "error", "success", "empty", "form", "list", "detail"]

# Direções de scroll/gesto
DIRECTIONS = ["up", "down", "left", "right"]
