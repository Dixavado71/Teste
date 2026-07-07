# Demo de Uso do Framework dixUIAuto

Este projeto demonstra como utilizar a biblioteca **dixUIAuto** para automação Android.

## Estrutura do Projeto Demo

```
dixUIAuto_demo/
├── requirements.txt          # Dependências do projeto
├── config.py                 # Configurações do demo
├── demo_basico.py            # Exemplos básicos de uso
├── demo_formulario.py        # Preenchimento inteligente de formulários
├── demo_fluxo_json.py        # Execução de fluxos via JSON
├── demo_avancado.py          # Recursos avançados (gestos, watcher, validator)
└── flows/
    └── login_flow.json       # Exemplo de fluxo em JSON
```

## Instalação

```bash
# Instalar dependências
pip install -r requirements.txt

# Certifique-se que o adb está instalado e no PATH
# No Android: ativar Depuração USB nas opções de desenvolvedor
```

## Pré-requisitos

1. **ADB instalado** no sistema
2. **Dispositivo Android** conectado via USB ou TCP/IP
3. **Depuração USB ativada** no dispositivo
4. **uiautomator2 server** instalado automaticamente na primeira conexão

## Exemplos de Uso

### 1. Demo Básico

```bash
python demo_basico.py
```

Demonstra:
- Conexão com dispositivo
- Listar dispositivos
- Abrir aplicativo
- Clicar em elementos
- Esperar por elementos

### 2. Demo de Formulário

```bash
python demo_formulario.py
```

Demonstra:
- Preenchimento inteligente por label
- Campos de CPF, senha, email, telefone
- Validação automática

### 3. Demo de Fluxo JSON

```bash
python demo_fluxo_json.py
```

Demonstra:
- Carregar fluxo de arquivo JSON
- Executar sequência de ações automaticamente
- Tratamento de erros no fluxo

### 4. Demo Avançado

```bash
python demo_avancado.py
```

Demonstra:
- Gestos (scroll, swipe)
- Watcher para mudanças de tela
- Validator para confirmações
- Screenshots
- Múltiplas estratégias de busca

## Configuração

Edite o arquivo `config.py` para ajustar:

```python
# Package do aplicativo a ser testado
APP_PACKAGE = "com.seu.app"

# Dispositivo (None usa o primeiro disponível)
DEVICE_ID = None  # ou "serial_number"

# Timeout padrão em segundos
DEFAULT_TIMEOUT = 10
```

## Estratégias de Localização Suportadas

```python
# Por texto
engine.click(text="Entrar")

# Por description
engine.click(desc="CPF")

# Por resource-id
engine.click(resourceId="com.app:id/login_button")

# Por classe
engine.click(className="android.widget.Button")

# Por XPath
engine.click(xpath="//android.widget.Button[@text='Entrar']")

# Por regex
engine.click(textRegex=".*Login.*")

# Combinando critérios
engine.click(text="OK", className="android.widget.Button")
```

## Smart Form

O módulo de formulário inteligente localiza automaticamente o campo associado a um label:

```python
# Preenche campo associado ao label "Número de CPF"
engine.form.fill(label="Número de CPF", value="02959350146")

# Preenche senha
engine.form.fill(label="Senha", value="minha_senha", field_type="password")

# Preenche email
engine.form.fill(label="E-mail", value="teste@email.com", field_type="email")
```

## Fluxos JSON

Crie arquivos JSON com sequências de ações:

```json
[
    {"action": "click", "text": "Já tenho uma conta"},
    {"action": "fill", "label": "CPF", "value": "02959350146"},
    {"action": "fill", "label": "Senha", "value": "123456"},
    {"action": "click", "text": "Entrar"}
]
```

Execute com:

```python
engine.flow.execute("flows/login_flow.json")
```

## Troubleshooting

### Dispositivo não detectado
```bash
adb devices
# Verifique se o dispositivo aparece
```

### Permissão negada
```bash
# No Linux/Mac
chmod +x adb
# No Windows, execute como administrador
```

### uiautomator2 server não inicia
```python
engine.device.shell("pm uninstall com.github.uiautomator")
engine.device.shell("pm uninstall com.github.uiautomator.test")
# Reconecte o dispositivo
```

## Próximos Passos

1. Explore os exemplos no diretório demo
2. Adapte os fluxos JSON para seu aplicativo
3. Crie seus próprios módulos customizados
4. Integre com seus testes automatizados

## Documentação Completa

Consulte o código-fonte da biblioteca `dixUIAuto` para detalhes de cada módulo e API completa.
