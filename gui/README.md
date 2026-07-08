# 🎨 GUI Premium - dixUIAuto

Interfaces gráficas modernas e estilizosas para o framework de automação Android **dixUIAuto**.

## 📋 Requisitos

### Dependências Python

```bash
pip install -r gui/requirements_gui.txt
```

**Ou instale manualmente:**

```bash
pip install customtkinter Pillow requests uiautomator2
```

### Dependências do Sistema (Linux)

```bash
# Ubuntu/Debian
sudo apt-get install python3-tk tk

# Fedora/RHEL
sudo dnf install python3-tkinter tkinter

# Arch Linux
sudo pacman -S tk
```

### Windows/macOS

Tkinter já vem pré-instalado com Python. Apenas instale as dependências Python acima.

---

## 🚀 Interfaces Disponíveis

### 1. Premium GUI (`run_gui.py`)

Interface principal completa com:

- **📱 Painel de Dispositivos**: Gerencia conexões USB/TCP
- **📊 Dashboard**: Status em tempo real, métricas e atividades
- **🔧 Construtor de Flows**: Crie automações visualmente sem código
- **⚡ Ações Rápidas**: Botões para comandos frequentes

**Executar:**
```bash
python run_gui.py
```

### 2. Live Inspector (`run_inspector.py`)

Ferramenta de inspeção da UI Android com:

- **🌳 Árvore Hierárquica**: Visualização completa dos elementos
- **🎯 Score de Seletor**: Avaliação automática (0.00-1.00) da qualidade do seletor
- **🔍 Filtros Avançados**: Filtra por texto, ID, classe, etc.
- **💻 Geração de Código**: Exporta código Python ou JSON automaticamente
- **📊 Estatísticas**: Total de elementos, clicáveis, etc.

**Executar:**
```bash
python run_inspector.py
```

---

## 🎯 Funcionalidades da GUI

### Construtor de Flows

Crie fluxos de automação visualmente:

1. Selecione o tipo de ação (click, fill, wait, swipe, etc.)
2. Preencha os parâmetros (texto, description, resource-id, valor)
3. Clique em "➕ Adicionar Ação"
4. Repita para todas as ações do fluxo
5. Clique em "💾 Exportar JSON" para salvar

**Ações Suportadas:**
- `click` - Clica em elemento
- `fill` - Preenche campo com valor
- `wait` - Aguarda elemento aparecer
- `swipe` - Desliza tela
- `scroll` - Rola lista
- `screenshot` - Captura tela
- `open_app` - Abre aplicativo
- `press_back` - Volta tela
- `press_home` - Vai para home

### Live Inspector - Scores de Seletor

O inspector avalia automaticamente a qualidade de cada seletor:

| Score | Cor | Significado |
|-------|-----|-------------|
| 0.70 - 1.00 | 🟢 Verde | **Excelente** - Use este seletor |
| 0.40 - 0.69 | 🟡 Amarelo | **Regular** - Funciona, mas pode melhorar |
| 0.00 - 0.39 | 🔴 Vermelho | **Ruim** - Evite, muito genérico |

**Critérios de Avaliação:**
- ✅ Resource ID único (+0.4 pontos)
- ✅ Content description significativo (+0.3 pontos)
- ✅ Texto descritivo (+0.2 pontos)
- ✅ Classe específica (+0.1 pontos)
- ✅ Elemento clicável (+0.05 pontos)

---

## 💡 Workflow Recomendado

### Para Criar Novas Automações:

1. **Inspecionar**
   ```bash
   python run_inspector.py
   ```
   - Carregue o dump XML do seu app
   - Navegue pela árvore de elementos
   - Identifique os elementos-alvo
   - Anote os scores dos seletores

2. **Construir Flow**
   ```bash
   python run_gui.py
   ```
   - Use o Construtor de Flows
   - Adicione ações baseadas na inspeção
   - Exporte como JSON

3. **Executar**
   ```python
   from main import DixEngine
   
   engine = DixEngine()
   engine.connect()
   engine.execute_flow("meu_flow.json")
   ```

---

## 🖼️ Recursos Visuais

### Tema Dark Premium

- Cores cuidadosamente selecionadas para conforto visual
- Contraste otimizado para longas sessões
- Elementos destacados com cores semânticas

### Componentes

- **Cards de Status**: Informações organizadas em cards
- **Botões com Ícones Emojis**: Interface amigável e intuitiva
- **Textbox com Syntax Highlight**: Código colorido
- **Scrollable Frames**: Navegação suave em listas longas

---

## 🔧 Integração com Engine

As interfaces estão totalmente integradas com a engine do dixUIAuto:

```python
# Settings compartilhados
from config.settings import settings

print(f"Tema GUI: {settings.GUI_THEME}")
print(f"Refresh Interval: {settings.GUI_REFRESH_INTERVAL}s")
```

---

## 📝 Exemplo de Uso do Inspector

1. Conecte seu dispositivo Android
2. Gere um dump da UI:
   ```bash
   adb shell uiautomator dump /sdcard/window_dump.xml
   adb pull /sdcard/window_dump.xml
   ```
3. Abra o Live Inspector:
   ```bash
   python run_inspector.py
   ```
4. Clique em "📁 Carregar XML" e selecione `window_dump.xml`
5. Navegue pela árvore e clique em elementos
6. Veja o score do seletor e o código gerado
7. Copie o código ou exporte como JSON

---

## ⚠️ Notas Importantes

- **Tkinter Requerido**: As interfaces usam tkinter/CustomTkinter
- **Display Necessário**: Requer ambiente gráfico (não funciona em headless)
- **Python 3.8+**: Compatível com Python 3.8 a 3.12

---

## 🐛 Solução de Problemas

### Erro: "No module named 'customtkinter'"
```bash
pip install customtkinter
```

### Erro: "ImportError: libtk8.6.so"
```bash
# Linux
sudo apt-get install python3-tk tk
```

### Erro: "_tkinter.TclError: no display name"
- Você está em um servidor sem interface gráfica
- Use X11 forwarding ou execute localmente

---

## 📄 Licença

Mesma licença do projeto dixUIAuto.

---

**dixUIAuto GUI** - Automação Android com estilo! 🚀
