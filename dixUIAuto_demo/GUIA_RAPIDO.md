# Guia Rápido - dixUIAuto

## Instalação e Configuração

### 1. Instalar dependências

```bash
cd dixUIAuto_demo
pip install -r requirements.txt
```

### 2. Verificar ADB instalado

```bash
adb version
```

Se não estiver instalado:
- **Linux**: `sudo apt-get install adb`
- **Mac**: `brew install adb`
- **Windows**: [Baixar aqui](https://developer.android.com/studio/releases/platform-tools)

### 3. Configurar dispositivo Android

1. Ative as **Opções do Desenvolvedor**:
   - Vá em Configurações → Sobre o telefone
   - Toque 7 vezes em "Número da versão"

2. Ative a **Depuração USB**:
   - Configurações → Opções do desenvolvedor → Depuração USB

3. Conecte via USB ou TCP/IP

### 4. Testar conexão

```bash
adb devices
```

Deve aparecer algo como:
```
List of devices attached
emulator-5554    device
```

## Uso Básico

### Inicializar

```python
from main import DixEngine

engine = DixEngine()
engine.connect()  # Conecta ao primeiro dispositivo
```

### Abrir aplicativo

```python
engine.open("com.whatsapp")
engine.open("com.instagram.android")
```

### Clicar em elementos

```python
# Por texto
engine.click(text="Entrar")
engine.click(text="OK")

# Por descrição
engine.click(desc="Menu principal")

# Por ID
engine.click(resourceId="com.app:id/btn_login")

# Por classe
engine.click(className="android.widget.Button")

# Combinando critérios
engine.click(text="Enviar", className="android.widget.Button")
```

### Esperar elementos

```python
# Espera até 10 segundos por elemento
found = engine.wait(text="Home", timeout=10)

if found:
    print("Tela carregada!")
```

### Preencher formulários

```python
# Smart Form - localiza campo automaticamente pelo label
engine.form.fill(label="CPF", value="02959350146")
engine.form.fill(label="Senha", value="123456", field_type="password")
engine.form.fill(label="E-mail", value="teste@email.com", field_type="email")
engine.form.fill(label="Telefone", value="(11) 98765-4321", field_type="phone")
```

### Gestos

```python
# Swipe (deslizar)
engine.gestures.swipe(direction='up', percent=0.5)
engine.gestures.swipe(direction='down', percent=0.3)
engine.gestures.swipe(direction='left', percent=0.5)

# Scroll (rolar listas)
engine.gestures.scroll(direction='down', steps=10)
engine.gestures.scroll(direction='up', steps=5)
```

### Screenshots

```python
# Capturar tela atual
caminho = engine.screenshot("tela_login")
print(f"Salvo em: {caminho}")
```

## Executar Fluxos JSON

### Criar fluxo

Crie um arquivo `flows/meu_fluxo.json`:

```json
[
    {
        "action": "click",
        "text": "Já tenho uma conta",
        "description": "Ir para login"
    },
    {
        "action": "fill",
        "label": "CPF",
        "value": "02959350146",
        "description": "Preencher CPF"
    },
    {
        "action": "fill",
        "label": "Senha",
        "value": "MinhaSenha123",
        "description": "Preencher senha"
    },
    {
        "action": "click",
        "text": "Entrar",
        "description": "Fazer login"
    }
]
```

### Executar fluxo

```python
engine.flow.execute("flows/meu_fluxo.json")
```

## Estratégias de Busca

### Finder

```python
# Buscar por texto
elementos = engine.finder.find_text("Login")

# Buscar por descrição
elementos = engine.finder.find_desc("Botão enviar")

# Buscar por resource-id
elementos = engine.finder.find_resource("com.app:id/username")

# Buscar por classe
elementos = engine.finder.find_class("android.widget.EditText")

# Buscar por XPath
elementos = engine.finder.find_xpath("//android.widget.Button[@text='OK']")

# Buscar por regex
elementos = engine.finder.find_regex(textRegex=".*Login.*")

# Buscar múltiplos critérios
elementos = engine.finder.find_multiple(
    text="Enviar",
    className="android.widget.Button",
    clickable=True
)

# Primeiro elemento visível
elemento = engine.finder.find_first(text="OK", visible=True)
```

### Locator (localização espacial)

```python
# Encontrar elemento mais próximo
campo = engine.locator.find_nearest(
    element=label,
    target_class="android.widget.EditText"
)

# Calcular distância
distancia = engine.locator.distance_to(elem1, elem2)

# Verificar proximidade
proximo = engine.locator.is_near(elem1, elem2, threshold=50)

# Obter pai/filhos/irmãos
pai = engine.locator.get_parent(elemento)
filhos = engine.locator.get_children(elemento)
irmaos = engine.locator.get_siblings(elemento)
```

## Validações

```python
# Validar se elemento existe
existe = engine.validator.validate_exists(text="Home")

# Validar texto
valido = engine.validator.validate_text(
    resourceId="com.app:id/title",
    expected_text="Página Principal"
)

# Validar campo preenchido
valido = engine.validator.validate_field(
    label="CPF",
    expected_value="029.593.501-46"
)

# Validar tela atual
na_tela = engine.validator.validate_screen(text="Menu Principal")

# Detectar popup
tem_popup = engine.validator.validate_popup(text="Erro")

# Detectar erro
tem_erro = engine.validator.validate_error(text="Falha na conexão")
```

## Watcher (Monitoramento)

```python
# Iniciar watcher
engine.watcher.start(interval=0.5)

# Verificar se tela mudou
if engine.watcher.has_changed():
    print("Tela mudou!")
    xml_atual = engine.dump()

# Parar watcher
engine.watcher.stop()
```

## Cache

```python
# Status do cache
status = engine.cache.get_status()
print(f"Hits: {status['hits']}, Misses: {status['misses']}")

# Limpar cache
engine.cache.clear()

# Habilitar/desabilitar
engine.cache.enable()
engine.cache.disable()
```

## Exemplo Completo

```python
from main import DixEngine

# Inicializar
engine = DixEngine(debug=True)
engine.connect()

# Abrir app
engine.open("com.meuapp")

# Aguardar tela inicial
engine.wait(text="Bem-vindo", timeout=10)

# Fazer login
engine.form.fill(label="E-mail", value="usuario@email.com")
engine.form.fill(label="Senha", value="senha123")
engine.click(text="Entrar")

# Aguardar home
engine.wait(text="Home", timeout=10)

# Navegar
engine.gestures.swipe(direction='up', percent=0.5)
engine.click(text="Perfil")

# Validar
if engine.validator.validate_screen(text="Meu Perfil"):
    print("✅ Navegação bem-sucedida!")
    engine.screenshot("tela_perfil")
else:
    print("❌ Erro na navegação")

# Fechar
engine.device.home()
```

## Troubleshooting

### Dispositivo não detectado

```bash
# Reiniciar servidor ADB
adb kill-server
adb start-server
adb devices
```

### uiautomator2 com problemas

```python
# Reinstalar servidor no dispositivo
engine.device.shell("pm uninstall com.github.uiautomator")
engine.device.shell("pm uninstall com.github.uiautomator.test")
engine.connect()  # Reconecta e reinstala
```

### Permissão negada

```bash
# Linux/Mac
sudo chmod +x /path/to/adb

# Windows: Execute como administrador
```

### App não abre

```python
# Tente forçar parada primeiro
engine.device.shell("am force-stop com.meuapp")
engine.open("com.meuapp")
```

## Dicas

1. **Use content-desc**: Apps com boas práticas de acessibilidade são mais fáceis de automatizar
2. **Evite waits fixos**: Prefira `engine.wait()` com condições
3. **Cache é seu amigo**: Mantenha habilitado para melhor performance
4. **Valide sempre**: Use validator após ações críticas
5. **Screenshots ajudam**: Capture telas para debug
6. **Fluxos JSON**: São mais fáceis de manter que código hard-coded

## Próximos Passos

1. Execute os demos:
   ```bash
   python setup.py              # Verifica instalação
   python demo_basico.py        # Funcionalidades básicas
   python demo_formulario.py    # Formulários
   python demo_fluxo_json.py    # Fluxos JSON
   python demo_avancado.py      # Recursos avançados
   ```

2. Crie seus próprios fluxos na pasta `flows/`

3. Consulte a documentação completa da biblioteca
