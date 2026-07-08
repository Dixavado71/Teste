# 🚀 Guia de Início Rápido - GUI dixUIAuto

## Instalação e Configuração

### 1. Instalar Dependências

```bash
cd /workspace/dixUIAuto
pip install -r gui/requirements_gui.txt
```

### 2. Verificar Dispositivo Android

```bash
# Conectar dispositivo via USB
adb devices

# Deve aparecer algo como:
# List of devices attached
# ABC123456789    device
```

### 3. Iniciar a Interface

```bash
# Interface principal (Dashboard + Construtor de Flows)
python run_gui.py

# OU Live Inspector (Inspeção de elementos em tempo real)
python run_inspector.py
```

---

## 📋 Usando a Interface Principal

### Passo 1: Conectar Dispositivo

1. Na sidebar esquerda, clique em **"🔄 Atualizar"**
2. Seu dispositivo aparecerá como um card
3. Clique em **"Selecionar"** no card do dispositivo
4. Aguarde a confirmação de conexão

### Passo 2: Abrir Aplicativo

1. No campo **"Package do App"**, digite o package (ex: `com.whatsapp`)
2. Clique em **"🚀 Abrir App"**
3. O aplicativo será aberto no dispositivo conectado

### Passo 3: Ações Rápidas

Use os botões no Dashboard:
- **🏠 Home**: Volta para tela inicial do Android
- **↩️ Back**: Volta uma tela
- **📸 Screenshot**: Captura tela atual
- **🔄 Refresh UI**: Atualiza cache da interface

### Passo 4: Criar Flow Visualmente

1. Vá para aba **"Construtor de Flows"**
2. No lado esquerdo (**Construtor de Ações**):
   - Selecione tipo de ação (click, fill, wait, etc.)
   - Escolha como localizar (text, desc, resource_id)
   - Digite o valor (ex: "Entrar")
   - Clique em **"➕ Adicionar Ação"**

3. No lado direito (**Editor de Flow**):
   - Veja a lista de ações adicionadas
   - Clique em **"💾 Exportar JSON"** para salvar

### Exemplo: Criar Flow de Login

| Passo | Ação | Localizador | Valor | Extra |
|-------|------|-------------|-------|-------|
| 1 | click | text | Já tenho uma conta | - |
| 2 | click | desc | CPF | - |
| 3 | fill | text | Número de CPF | 02959350146 |
| 4 | fill | text | Senha | 123456 |
| 5 | click | text | Entrar | - |

Exporte o JSON e execute depois com:

```python
from main import DixEngine

engine = DixEngine()
engine.connect()
engine.execute_flow("login_flow.json")
```

---

## 🔍 Usando o Live Inspector

### Passo 1: Capturar UI

1. Com o aplicativo aberto no dispositivo
2. Clique em **"📸 Capturar UI"**
3. A árvore de elementos será carregada

### Passo 2: Explorar Elementos

- **Expanda/Colapse**: Clique nas setas para navegar na hierarquia
- **Colunas**:
  - Elemento: Nome da classe + profundidade
  - Texto: Conteúdo de texto do elemento
  - Resource ID: Identificador único
  - Classe: Tipo do widget
  - Score: Qualidade do seletor (0.00 a 1.00)

### Passo 3: Aplicar Filtros

Na barra de filtros:
- Digite texto para buscar em todos os campos
- Marque **"Apenas Clicáveis"** para ver só elementos interativos

### Passo 4: Selecionar Elemento

1. Clique em qualquer elemento na árvore
2. Painel direito mostrará:
   - Todas as propriedades
   - Score do seletor (verde = bom, amarelo = médio, vermelho = ruim)
   - Botões para gerar código

### Passo 5: Gerar Código

Clique em:
- **🐍 Python**: Gera código Python para clicar/preencher
- **📄 JSON Flow**: Gera ação em formato JSON

**Exemplo de código gerado:**

```python
# Código Python generado
engine.click(resource_id="com.app:id/login_button")
```

ou

```json
[
    {
        "action": "click",
        "resource_id": "com.app:id/login_button"
    }
]
```

---

## 🎯 Melhores Práticas

### Seletores Prioritários (ordem de preferência)

1. **resource-id** (score 0.4) - Mais estável
2. **content-desc** (score 0.3) - Muito bom
3. **text** (score 0.2) - Bom para textos únicos
4. **class_name** (score 0.1) - Use como fallback

### Dicas para Flows Robustos

✅ **Faça:**
- Use resource-id sempre que disponível
- Adicione waits entre ações críticas
- Teste cada ação individualmente antes de criar o flow completo
- Salve versões diferentes dos flows durante desenvolvimento

❌ **Não faça:**
- Não confie apenas em texto (pode mudar com internacionalização)
- Não use XPath complexo sem necessidade
- Não esqueça de tratar erros e timeouts

### Workflow Recomendado

1. **Descobrir**: Use Live Inspector para encontrar elementos
2. **Testar**: Teste seletores individualmente no Dashboard
3. **Construir**: Crie flow completo no Construtor
4. **Exportar**: Salve como JSON
5. **Executar**: Rode o flow com engine
6. **Refinar**: Ajuste baseado nos resultados

---

## 🛠️ Solução de Problemas Comuns

### "Nenhum dispositivo encontrado"

```bash
# Verifique cabo USB e depuração
adb devices

# Se não listar, tente:
adb kill-server
adb start-server
adb devices
```

### "Falha ao capturar UI"

```bash
# Force stop no app e reabra
adb shell am force-stop com.seu.app

# Ou reinicie o servidor uiautomator
adb shell uiautomator dump
```

### GUI lenta ou travando

- Feche outras aplicações pesadas
- Reduza frequência de auto-refresh no inspector
- Use filtros para diminuir quantidade de elementos na árvore

### Erro ao importar customtkinter

```bash
pip uninstall customtkinter
pip install customtkinter==5.2.0
```

---

## 📊 Entendendo o Score de Seletor

O score varia de **0.00** a **1.00**:

| Score | Cor | Significado | Ação |
|-------|-----|-------------|------|
| 0.70 - 1.00 | 🟢 Verde | Excelente | Use com confiança |
| 0.40 - 0.69 | 🟡 Amarelo | Regular | Funciona, mas pode quebrar |
| 0.00 - 0.39 | 🔴 Vermelho | Ruim | Evite, procure alternativa |

**Como é calculado:**
- resource-id presente: +0.4
- content-desc presente: +0.3
- texto não vazio: +0.2
- classe específica: +0.1

---

## 🎨 Personalização

### Modificar Cores do Tema

Edite `gui/premium_gui.py`, classe `ThemeColors`:

```python
class ThemeColors:
    BG_PRIMARY = "#1a1a2e"      # Fundo principal
    ACCENT = "#e94560"          # Cor de destaque
    SUCCESS = "#00d26a"         # Sucesso
    # ... modifique conforme desejado
```

### Adicionar Novas Ações

No `ActionBuilder`, adicione à lista `ACTION_TYPES`:

```python
ACTION_TYPES = [
    "click", "long_click", 
    "nova_acao",  # Sua ação aqui
    # ...
]
```

---

## 📞 Suporte

Para dúvidas ou problemas:

1. Consulte logs na aba **"Logs"** da GUI
2. Verifique console do terminal para erros detalhados
3. Revise documentação principal em `README.md`

---

**dixUIAuto** - Automação Android simplificada! 🤖
