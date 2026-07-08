# dixUIAuto - Framework de Automação Android

Framework completo para automação de aplicativos Android usando ADB e UIAutomator.

## 🚀 Recursos Principais

- **Cache Inteligente**: Evita dumps desnecessários detectando mudanças na UI
- **Smart Form Filler**: Preenche formulários automaticamente identificando campos por labels
- **Finder Avançado**: Múltiplas estratégias de busca (texto, ID, content-desc, XPath)
- **Locator Espacial**: Cálculos de posição e relacionamentos entre elementos
- **Flow Engine**: Execução de fluxos definidos em JSON
- **Inspector Inteligente**: Sugere os melhores seletores com scoring
- **Watcher em Tempo Real**: Observa mudanças na interface
- **Validator**: Validações e asserts robustos

## 📁 Estrutura do Projeto

```
dixUIAuto/
├── main.py              # Engine principal
├── config/
│   ├── settings.py      # Configurações globais
│   └── constants.py     # Constantes e padrões
├── lib/
│   ├── adb_bridge.py    # Ponte ADB
│   ├── device.py        # Gerenciador de dispositivos
│   ├── dumper.py        # Dump da UI
│   ├── parser.py        # Parser XML → UINode
│   ├── cache.py         # Cache engine
│   ├── finder.py        # Sistema de busca
│   ├── locator.py       # Localização espacial
│   ├── clicker.py       # Ações de clique
│   ├── keyboard.py      # Entrada de texto
│   ├── gestures.py      # Gestos e scroll
│   ├── watcher.py       # Observer de UI
│   ├── validator.py     # Validações
│   ├── form.py          # Smart Form Filler
│   ├── actions.py       # Sistema de ações
│   ├── flow.py          # Flow Engine
│   ├── inspector.py     # Smart Inspector
│   ├── logs.py          # Logging
│   └── exceptions.py    # Exceções
├── flows/               # Fluxos JSON
├── dumps/               # Dumps XML
├── screenshots/         # Screenshots
├── cache/               # Cache
└── logs/                # Logs
```

## 💻 Instalação

```bash
# Clone o repositório
cd /workspace/dixUIAuto

# Requisitos: Python 3.8+, ADB instalado
```

## 🔧 Uso Básico

```python
from main import DixEngine

engine = DixEngine()
engine.connect()  # Conecta via USB ou TCP

# Abrir app
engine.open("com.meuapp.android")

# Clicar em elemento
engine.click(text="Entrar")

# Preencher formulário
engine.form.fill(label="CPF", value="02959350146")
engine.form.fill(label="Senha", value="minhasenha")

# Scroll
engine.scroll(direction="down")

# Screenshot
engine.screenshot("tela.png")

engine.disconnect()
```

## 📝 Uso com Flows JSON

```python
engine = DixEngine()
engine.connect()
engine.open("com.meuapp.android")

# Executar fluxo
success = engine.flow.run("login_flow.json")

# Ver estatísticas
stats = engine.flow.get_stats()
print(f"Sucesso: {stats['successful']}/{stats['total_steps']}")
```

### Exemplo de Flow JSON

```json
{
  "steps": [
    {"action": "wait", "seconds": 2},
    {"action": "click", "text": "Entrar"},
    {"action": "fill", "label": "CPF", "value": "02959350146"},
    {"action": "fill", "label": "Senha", "value": "senha123"},
    {"action": "click", "text": "Acessar"}
  ]
}
```

## 🎯 Estratégias de Busca

| Estratégia | Descrição | Score |
|------------|-----------|-------|
| resource_id | ID do recurso Android | 0.95 |
| content_desc | Descrição de acessibilidade | 0.90 |
| text | Texto exato | 0.85 |
| text_contains | Contém texto | 0.60 |
| class + attrs | Combinação classe+atributos | 0.50 |
| xpath | XPath (use com cuidado) | 0.40 |

## 🔍 Smart Inspector

```python
from lib.inspector import SmartInspector

inspector = SmartInspector()
_, root = engine.dumper.dump()

# Detectar framework
framework = inspector.detect_ui_framework(root)
print(f"Framework: {framework}")

# Analisar nó específico
node = engine.finder.find_text("Botão")
suggestions = inspector.analyze_node(node, root.get_all_descendants())
print(f"Melhor seletor: {suggestions[0]}")
```

## 📊 Validações

```python
# Assert existência
assert engine.validator.assert_exists(node)

# Assert visibilidade
assert engine.validator.assert_visible(node)

# Assert texto
assert engine.validator.assert_text(node, "Texto esperado")

# Validar formulário
results = engine.validator.validate_form_filled(fields, values)
```

## ⚙️ Configuração

Edite `config/settings.py` para personalizar:

```python
CACHE_ENABLED = True
CACHE_TTL = 300  # segundos
DEFAULT_TIMEOUT = 10
LOG_LEVEL = "INFO"
```

## 📄 Demo

Execute a demo:
```bash
python /workspace/dixUIAuto_demo/demo_usage.py
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie branch para feature
3. Commit mudanças
4. Push para branch
5. Open Pull Request

## 📝 Licença

MIT License
