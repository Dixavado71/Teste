# 🖥️ GUI do dixUIAuto - Interface Gráfica Premium

Interface gráfica moderna e estilosa para automação Android com o framework dixUIAuto.

## 🎨 Recursos

### Interface Principal (Premium GUI)

- **Tema Dark Premium**: Design moderno com cores cuidadosamente selecionadas
- **Dashboard Intuitivo**: Visão geral de dispositivos, aplicativos e ações
- **Construtor Visual de Flows**: Crie fluxos de automação sem codificação manual
- **Editor de Ações**: Adicione ações de clique, preenchimento, espera e mais
- **Exportação JSON**: Salve seus flows para execução posterior
- **Logs em Tempo Real**: Acompanhe a execução das ações
- **Gerenciamento de Dispositivos**: Conecte e gerencie múltiplos dispositivos Android

### Live Inspector

- **Árvore de Elementos**: Visualize hierarquicamente todos os elementos da UI
- **Filtros Avançados**: Filtre por texto, ID, classe ou propriedades
- **Score de Seletor**: Avaliação automática da qualidade do seletor (0-1)
- **Detalhes do Elemento**: Veja todas as propriedades de cada elemento
- **Geração de Código**: Gere automaticamente código Python ou JSON Flow
- **Auto Refresh**: Atualização automática da UI a cada 5 segundos
- **Elementos Clicáveis**: Filtro para mostrar apenas elementos interativos

## 📦 Instalação

### Pré-requisitos

- Python 3.8+
- Dispositivo Android com depuração USB habilitada
- ADB configurado no sistema

### Instalar Dependências

```bash
pip install -r gui/requirements_gui.txt
```

## 🚀 Uso

### Iniciar Interface Principal

```bash
python run_gui.py
```

### Iniciar Live Inspector

```bash
python run_inspector.py
```

## 🎯 Funcionalidades da GUI

### Dashboard

O dashboard fornece:
- Cards de status (conexão, aplicativo, ações executadas)
- Campo para informar package do aplicativo
- Botões de ação rápida (Home, Back, Screenshot, Refresh UI)
- Lista de dispositivos conectados com seleção visual

### Construtor de Flows

1. **Selecione o tipo de ação**: click, long_click, fill, swipe, wait, etc.
2. **Escolha o localizador**: text, desc, resource_id, class_name, xpath, regex
3. **Informe o valor**: Texto ou identificador do elemento
4. **Adicione a ação**: Clique em "Adicionar Ação"
5. **Exporte o flow**: Salve como arquivo JSON para execução posterior

### Live Inspector

1. **Capturar UI**: Obtém o dump XML atual da interface
2. **Navegar na árvore**: Expanda/colapse nós para explorar a hierarquia
3. **Aplicar filtros**: Encontre elementos específicos rapidamente
4. **Selecionar elemento**: Clique para ver detalhes completos
5. **Gerar código**: Produz automaticamente código Python ou JSON

## 🎨 Cores do Tema

| Cor | Hex | Uso |
|-----|-----|-----|
| Background Primário | `#1a1a2e` | Fundo principal |
| Background Secundário | `#16213e` | Sidebar, barras |
| Background Terciário | `#0f3460` | Inputs, cards internos |
| Accent | `#e94560` | Botões principais, destaques |
| Success | `#00d26a` | Confirmações, status positivo |
| Warning | `#ffc107` | Alertas, atenção |
| Error | `#dc3545` | Erros, ações destrutivas |

## 📋 Exemplo de Fluxo Criado na GUI

Após criar ações no construtor visual, o JSON exportado será similar a:

```json
[
    {
        "action": "click",
        "text": "Já tenho uma conta",
        "timeout": 10
    },
    {
        "action": "fill",
        "resource_id": "com.app:id/cpf_field",
        "value": "02959350146",
        "timeout": 10
    },
    {
        "action": "fill",
        "desc": "Campo de senha",
        "value": "minhasenha123",
        "timeout": 10
    },
    {
        "action": "click",
        "text": "Entrar",
        "timeout": 10
    }
]
```

## 🔧 Integração com Engine

A GUI integra-se automaticamente com a engine do dixUIAuto:

```python
from main import DixEngine
from gui.premium_gui import DixUIGUI

engine = DixEngine()
engine.connect()

# A GUI usará esta engine para todas as operações
app = DixUIGUI()
app.run()
```

## 💡 Dicas de Uso

1. **Sempre conecte um dispositivo** antes de usar a GUI
2. **Use o Live Inspector** para descobrir os melhores seletores
3. **Prefira resource-id** quando disponível (score mais alto)
4. **Teste ações individualmente** antes de criar flows complexos
5. **Salve seus flows** frequentemente durante o desenvolvimento
6. **Use filtros no inspector** para encontrar elementos em telas complexas

## 🐛 Solução de Problemas

### GUI não inicia

```bash
# Verifique se as dependências estão instaladas
pip install -r gui/requirements_gui.txt

# Execute com verbose
python -v run_gui.py
```

### Dispositivo não aparece

```bash
# Verifique conexão ADB
adb devices

# Reinicie servidor ADB
adb kill-server
adb start-server
```

### Inspector não captura UI

```bash
# Verifique permissões no dispositivo
adb shell pm grant com.example.app android.permission.WRITE_SETTINGS

# Force stop e reabra o app
adb shell am force-stop com.example.app
```

## 📸 Screenshots

A interface possui:
- Layout responsivo e moderno
- Ícones emojis para identificação visual rápida
- Feedback visual para todas as ações
- Temas de cores consistentes
- Tipografia clara e legível

## 🔮 Futuras Melhorias

- [ ] Highlight de elementos no dispositivo real
- [ ] Gravação de ações manuais para gerar flow automático
- [ ] Editor visual de condições e loops
- [ ] Preview de screenshot com overlay de elementos
- [ ] Exportação para formatos adicionais (YAML, CSV)
- [ ] Temas personalizáveis pelo usuário
- [ ] Suporte a múltiplas janelas de inspector

---

**dixUIAuto** - Automação Android inteligente e acessível 🤖
