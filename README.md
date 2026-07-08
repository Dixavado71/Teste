# dixUIAuto - Android UI Automation Framework

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Framework modular e de alta performance para automação de interfaces Android usando ADB e UIAutomator.

## 🚀 Recursos Principais

- **Cache Inteligente**: Evita dumps desnecessários detectando mudanças na UI via hash SHA256
- **Smart Form Filler**: Preenche formulários automaticamente identificando campos por labels
- **Finder Avançado**: Múltiplas estratégias de busca (texto, ID, content-desc, XPath, regex)
- **Locator Espacial**: Cálculos de posição, distância e relacionamentos entre elementos
- **Flow Engine**: Execução de fluxos definidos em JSON ou via Fluent Builder
- **Smart Inspector**: Sugere os melhores seletores com scoring de confiança
- **Watcher em Tempo Real**: Observa mudanças na interface e dispara callbacks
- **Validator Robusto**: Validações e asserts para testes automatizados
- **Code Generator**: Gera código Python/JSON automaticamente a partir de inspeções
- **Gestos Completos**: Swipe, scroll, drag, tap e gestos multi-toque

## 📦 Instalação

### Pré-requisitos

- Python 3.8 ou superior
- ADB (Android Debug Bridge) instalado e configurado
- Dispositivo Android ou emulador conectado

### Configuração

```bash
# Clone o repositório
cd /workspace

# Verifique se o ADB está funcionando
adb devices

# Execute a demo
python main.py
```

## 📁 Estrutura do Projeto

```
/workspace/
├── lib/                      # Biblioteca principal
│   ├── __init__.py          # exports do framework
│   ├── engine.py            # DixEngine - orchestrator principal
│   ├── adb_bridge.py        # Abstração de comandos ADB
│   ├── device.py            # Gerenciamento de dispositivos
│   ├── dumper.py            # Dump da UI via uiautomator
│   ├── parser.py            # Parser XML → UIElement
│   ├── cache.py             # Cache engine com hash
│   ├── finder.py            # Sistema de busca de elementos
│   ├── locator.py           # Localização espacial
│   ├── clicker.py           # Ações de clique
│   ├── keyboard.py          # Entrada de texto
│   ├── gestures.py          # Gestos e scroll
│   ├── form.py              # Smart Form Filler
│   ├── watcher.py           # Observer de UI
│   ├── validator.py         # Validações e asserts
│   ├── flow.py              # Flow Engine
│   ├── flow_builder.py      # Fluent Builder para flows
│   ├── flow_templates.py    # Templates de flows comuns
│   ├── models.py            # Dataclasses UIElement, Bounds
│   ├── exceptions.py        # Exceções customizadas
│   ├── logs.py              # Sistema de logging
│   └── utils.py             # Funções utilitárias
├── config/
│   ├── settings.py          # Configurações globais
│   └── constants.py         # Constantes do framework
├── examples/                # Exemplos de uso
├── tests/                   # Testes unitários
├── flows/                   # Fluxos JSON
└── main.py                  # Entry point
```

## 💻 Uso Básico

### Inicialização

```python
from lib.engine import DixEngine

# Criar e conectar engine
engine = DixEngine()
engine.connect()  # Conecta via USB ou TCP

# Abrir aplicativo
engine.open("com.example.app")

# ... realizar automações ...

engine.disconnect()
```

### Estratégias de Busca

```python
# Por texto exato
element = engine.finder.find_text("Login")

# Por texto parcial
element = engine.finder.find_text("Log", exact=False)

# Por resource-id
element = engine.finder.find_resource("com.app:id/login_button")

# Por content-description
element = engine.finder.find_desc("Botão de login")

# Por classe
element = engine.finder.find_class("Button")

# Por XPath
element = engine.finder.find_xpath("//android.widget.Button[@text='Login']")

# Por regex
element = engine.finder.find_regex(r"Login.*", field="text")
```

### Ações de Clique

```python
# Clique simples
engine.click(text="Entrar")
engine.click(desc="Login button")
engine.click(resource_id="com.app:id/btn_login")

# Clique duplo
engine.double_click(text="Item")

# Long press (1 segundo)
engine.long_click(text="Menu", duration=1.5)
```

### Preenchimento de Formulários

```python
# Preencher campo por label
engine.form.fill(label="CPF", value="029.593.501-46")
engine.form.fill(label="Senha", value="minhasenha")
engine.form.fill(label="Email", value="usuario@email.com")

# Preencher múltiplos campos
form_data = {
    "Nome": "João Silva",
    "Email": "joao@email.com",
    "Telefone": "(11) 99999-9999"
}
engine.form.fill_multiple(form_data)
```

### Gestos

```python
# Scroll
engine.scroll(direction="down")
engine.scroll(direction="up", steps=3)

# Swipe
engine.swipe(start=(500, 1500), end=(500, 500))

# Swipe entre elementos
start_elem = engine.finder.find_text("Início")
end_elem = engine.finder.find_text("Fim")
engine.swipe_between(start_elem, end_elem)
```

### Validações

```python
# Assert existência
assert engine.validator.assert_exists(text="Home")

# Assert visibilidade
element = engine.finder.find_text("Menu")
assert engine.validator.assert_visible(element)

# Assert texto
assert engine.validator.assert_text(element, "Menu Principal")

# Assert que elemento NÃO existe
assert engine.validator.assert_not_exists(text="Erro")
```

### Watcher (Observer)

```python
# Registrar watcher para mudança de tela
def on_screen_change(old, new):
    print(f"Tela mudou de {old} para {new}")

engine.watcher.register_screen_change_callback(on_screen_change)
engine.watcher.start()

# ... realizar automações ...

engine.watcher.stop()
```

## 🔄 Flow Engine

### Usando Fluent Builder

```python
from lib.flow_builder import FlowBuilder

flow = (FlowBuilder(name="login_flow")
    .open_app("com.example.app")
    .wait(2)
    .click(text="Entrar")
    .fill(label="CPF", value="02959350146")
    .fill(label="Senha", value="123456")
    .click(text="Acessar")
    .wait_for(text="Home", timeout=10)
    .screenshot("home_screen")
    .build())

engine.flow.execute(flow)
```

### Usando JSON

```python
# flows/login.json
{
  "name": "login_flow",
  "steps": [
    {"action": "open_app", "package": "com.example.app"},
    {"action": "wait", "seconds": 2},
    {"action": "click", "text": "Entrar"},
    {"action": "fill", "label": "CPF", "value": "02959350146"},
    {"action": "fill", "label": "Senha", "value": "123456"},
    {"action": "click", "text": "Acessar"},
    {"action": "wait_for", "text": "Home", "timeout": 10},
    {"action": "screenshot", "filename": "home_screen"}
  ]
}
```

```python
# Executar flow JSON
success = engine.flow.run("flows/login.json")

# Ver estatísticas
stats = engine.flow.get_stats()
print(f"Sucesso: {stats['successful']}/{stats['total_steps']}")
```

### Flow Templates

```python
from lib.flow_templates import get_template

# Template de login
login_flow = get_template("login", {
    "package": "com.app",
    "login_button": "Entrar",
    "cpf_label": "CPF",
    "password_label": "Senha",
    "cpf_value": "02959350146",
    "password_value": "senha123"
})

engine.flow.execute(login_flow)
```

## 🔍 Smart Inspector

```python
from lib.inspector import SmartInspector

inspector = SmartInspector()

# Obter árvore UI
_, root = engine.dumper.dump()

# Detectar framework UI
framework = inspector.detect_ui_framework(root)
print(f"Framework: {framework}")  # Android Views, Jetpack Compose, Flutter

# Analisar nó e obter sugestões de seletores
node = engine.finder.find_text("Botão")
suggestions = inspector.analyze_node(node, root.get_all_descendants())

print("Melhores seletores:")
for s in suggestions[:3]:
    print(f"  {s.strategy}='{s.value}' (score: {s.score:.2f})")
```

## ⚙️ Configuração

Edite `config/settings.py`:

```python
# Cache
CACHE_ENABLED = True
CACHE_TTL = 300  # segundos

# Timeouts
DEFAULT_TIMEOUT = 10
ELEMENT_POLL_INTERVAL = 0.5

# Logging
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR

# Screenshots
SCREENSHOT_ON_ERROR = True
```

## 📊 Estratégias de Busca (Scoring)

| Estratégia | Descrição | Score | Uso Recomendado |
|------------|-----------|-------|-----------------|
| resource_id | ID do recurso Android | 0.95 | ✅ Primeiro choice |
| content_desc | Descrição de acessibilidade | 0.90 | ✅ Excelente |
| text | Texto exato | 0.85 | ✅ Bom para botões |
| text_contains | Contém texto | 0.60 | ⚠️ Use com cuidado |
| class + attrs | Combinação classe+atributos | 0.50 | ⚠️ Pouco específico |
| xpath | XPath | 0.40 | ❌ Último recurso |

## 🧪 Testes

```bash
# Rodar testes
python -m pytest tests/ -v
```

## 📝 Exemplos

Veja a pasta `examples/` para casos de uso completos:

- `examples/basic_usage.py` - Uso básico da engine
- `examples/form_filling.py` - Preenchimento de formulários
- `examples/flow_execution.py` - Execução de flows
- `examples/inspector_demo.py` - Demo do Smart Inspector

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📄 Licença

MIT License - veja o arquivo LICENSE para detalhes.

## 🔗 Links Úteis

- [Documentação ADB](https://developer.android.com/studio/command-line/adb)
- [UIAutomator](https://developer.android.com/training/testing/ui-automator)
- [Guia de Acessibilidade Android](https://developer.android.com/guide/topics/ui/accessibility)