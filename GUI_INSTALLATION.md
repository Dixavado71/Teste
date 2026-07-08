# 🚀 GUI Premium - Instalação e Uso

## ✅ Status da Instalação

Todos os módulos da GUI foram instalados com sucesso!

**Arquivos criados:**
- `gui/premium_gui.py` (20.671 bytes) - Interface principal
- `gui/live_inspector.py` (24.213 bytes) - Live Inspector  
- `gui/requirements_gui.txt` - Dependências
- `gui/README.md` - Documentação completa
- `run_gui.py` - Launcher da GUI principal
- `run_inspector.py` - Launcher do Live Inspector
- `config/settings.py` - Atualizado com classe `Settings`

---

## 📦 Dependências Instaladas

✅ customtkinter
✅ Pillow  
✅ tkinter (sistema)

---

## 🎯 Como Usar

### No Seu Computador (Windows/macOS/Linux com Desktop)

1. **Instale as dependências** (se ainda não fez):
   ```bash
   pip install -r gui/requirements_gui.txt
   ```

2. **Execute a interface principal**:
   ```bash
   python run_gui.py
   ```

3. **Ou execute o Live Inspector**:
   ```bash
   python run_inspector.py
   ```

---

## 🖥️ Recursos da GUI

### Premium GUI (`run_gui.py`)

- **📱 Painel de Dispositivos**: Lista e conecta dispositivos Android
- **📊 Dashboard**: Cards de status (conexão, app, ações)
- **🔧 Construtor de Flows**: Crie automações visualmente
  - 9 tipos de ações: click, fill, wait, swipe, scroll, screenshot, open_app, press_back, press_home
  - Exportação automática para JSON
- **⚡ Ações Rápidas**: Home, Back, Screenshot, Refresh, etc.
- **📝 Log de Atividades**: Histórico em tempo real

### Live Inspector (`run_inspector.py`)

- **🌳 Árvore Hierárquica**: Visualização completa da UI
- **🎯 Score de Seletor**: Avaliação automática (0.00-1.00)
  - 🟢 Verde (0.70-1.00): Excelente
  - 🟡 Amarelo (0.40-0.69): Regular
  - 🔴 Vermelho (0.00-0.39): Ruim
- **🔍 Filtros**: Texto, Resource ID, Content Desc, Classe, Clicáveis
- **💻 Geração de Código**: Python ou JSON automático
- **📊 Estatísticas**: Total de elementos, clicáveis

---

## 💡 Workflow Completo

### Passo 1: Inspecionar a UI
```bash
python run_inspector.py
```
- Carregue um dump XML do seu app Android
- Navegue pela árvore de elementos
- Identifique elementos com bom score (>0.7)
- Copie o código gerado

### Passo 2: Criar Flow
```bash
python run_gui.py
```
- Use o Construtor de Flows
- Adicione ações baseadas na inspeção
- Exporte como JSON

### Passo 3: Executar
```python
from main import DixEngine

engine = DixEngine()
engine.connect()
engine.execute_flow("flow_exportado.json")
```

---

## ⚠️ Ambiente Headless (Servidor sem Display)

Se você está em um servidor sem interface gráfica, terá o erro:
```
_tkinter.TclError: no display name and no $DISPLAY environment variable
```

**Soluções:**

1. **Use X11 Forwarding** (SSH):
   ```bash
   ssh -X usuario@servidor
   python run_gui.py
   ```

2. **Use VNC/RDP** para acessar o desktop remoto

3. **Execute localmente** no seu computador Windows/macOS

4. **Use apenas via código** sem GUI:
   ```python
   from main import DixEngine
   engine = DixEngine()
   # Use a engine diretamente sem interface gráfica
   ```

---

## 🎨 Tema e Customização

O tema dark-blue premium está configurado em `config/settings.py`:

```python
settings.GUI_THEME = "dark-blue"  # Opções: dark-blue, green, blue
settings.GUI_REFRESH_INTERVAL = 5  # segundos
```

---

## 📋 Exemplo de Flow Criado na GUI

No Construtor de Flows, você pode criar algo como:

```json
[
    {
        "action": "click",
        "text": "Já tenho uma conta"
    },
    {
        "action": "fill",
        "text": "Número de CPF",
        "value": "02959350146"
    },
    {
        "action": "fill",
        "text": "Senha",
        "value": "123456"
    },
    {
        "action": "click",
        "text": "Entrar"
    }
]
```

---

## 🔗 Links Úteis

- [Documentação Completa](gui/README.md)
- [Settings](config/settings.py)
- [Main Engine](main.py)

---

**dixUIAuto GUI** - Pronta para usar! 🎉
