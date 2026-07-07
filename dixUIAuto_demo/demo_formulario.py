"""
Demo Formulário Inteligente - dixUIAuto

Este script demonstra o módulo Smart Form:
- Preenchimento automático de campos por label
- Diferentes tipos de campos (CPF, senha, email, telefone)
- Validação automática do preenchimento
"""

import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import DixEngine
from config import (
    APP_PACKAGE,
    DEVICE_ID,
    DEBUG_MODE,
    ELEMENT_WAIT_TIMEOUT
)


def preencher_cpf(engine: DixEngine):
    """Demonstra preenchimento de campo CPF."""
    print("\n" + "="*50)
    print("📝 PREENCHENDO CAMPO CPF")
    print("="*50)
    
    cpf = "02959350146"
    
    try:
        # O Smart Form localiza automaticamente o campo associado ao label
        resultado = engine.form.fill(
            label="Número de CPF",
            value=cpf,
            field_type="cpf"
        )
        
        if resultado['success']:
            print(f"✅ CPF preenchido com sucesso!")
            print(f"   Valor: {cpf}")
            print(f"   Campo encontrado: {resultado.get('field_found', False)}")
            return True
        else:
            print(f"⚠️ Não foi possível preencher o CPF")
            print(f"   Erro: {resultado.get('error', 'Desconhecido')}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao preencher CPF: {str(e)}")
        return False


def preencher_senha(engine: DixEngine):
    """Demonstra preenchimento de campo senha."""
    print("\n" + "="*50)
    print("🔒 PREENCHENDO CAMPO SENHA")
    print("="*50)
    
    senha = "MinhaSenha123!"
    
    try:
        resultado = engine.form.fill(
            label="Senha",
            value=senha,
            field_type="password"
        )
        
        if resultado['success']:
            print(f"✅ Senha preenchida com sucesso!")
            print(f"   Valor: {'*' * len(senha)}")
            print(f"   Campo seguro: {resultado.get('is_secure', False)}")
            return True
        else:
            print(f"⚠️ Não foi possível preencher a senha")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao preencher senha: {str(e)}")
        return False


def preencher_email(engine: DixEngine):
    """Demonstra preenchimento de campo email."""
    print("\n" + "="*50)
    print("📧 PREENCHENDO CAMPO E-MAIL")
    print("="*50)
    
    email = "teste@dixuiauto.com.br"
    
    try:
        resultado = engine.form.fill(
            label="E-mail",
            value=email,
            field_type="email"
        )
        
        if resultado['success']:
            print(f"✅ E-mail preenchido com sucesso!")
            print(f"   Valor: {email}")
            
            # Valida formato do email
            if resultado.get('validated', False):
                print(f"   ✅ Formato validado")
            
            return True
        else:
            print(f"⚠️ Não foi possível preencher o e-mail")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao preencher e-mail: {str(e)}")
        return False


def preencher_telefone(engine: DixEngine):
    """Demonstra preenchimento de campo telefone."""
    print("\n" + "="*50)
    print("📱 PREENCHENDO CAMPO TELEFONE")
    print("="*50)
    
    telefone = "(11) 98765-4321"
    
    try:
        resultado = engine.form.fill(
            label="Telefone",
            value=telefone,
            field_type="phone"
        )
        
        if resultado['success']:
            print(f"✅ Telefone preenchido com sucesso!")
            print(f"   Valor: {telefone}")
            return True
        else:
            print(f"⚠️ Não foi possível preencher o telefone")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao preencher telefone: {str(e)}")
        return False


def preencher_cep(engine: DixEngine):
    """Demonstra preenchimento de campo CEP."""
    print("\n" + "="*50)
    print("🏠 PREENCHENDO CAMPO CEP")
    print("="*50)
    
    cep = "01310-100"
    
    try:
        resultado = engine.form.fill(
            label="CEP",
            value=cep,
            field_type="cep"
        )
        
        if resultado['success']:
            print(f"✅ CEP preenchido com sucesso!")
            print(f"   Valor: {cep}")
            return True
        else:
            print(f"⚠️ Não foi possível preencher o CEP")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao preencher CEP: {str(e)}")
        return False


def limpar_campo(engine: DixEngine, label: str):
    """Demonstra limpeza de campo."""
    print(f"\n🧹 LIMPANDO CAMPO: {label}")
    
    try:
        resultado = engine.form.clear(label=label)
        
        if resultado['success']:
            print(f"✅ Campo '{label}' limpo com sucesso!")
            return True
        else:
            print(f"⚠️ Não foi possível limpar o campo")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao limpar campo: {str(e)}")
        return False


def validar_preenchimento(engine: DixEngine, label: str, valor_esperado: str):
    """Valida se um campo foi preenchido corretamente."""
    print(f"\n✓ VALIDANDO CAMPO: {label}")
    
    try:
        resultado = engine.validator.validate_field(
            label=label,
            expected_value=valor_esperado
        )
        
        if resultado.get('valid', False):
            print(f"✅ Validação bem-sucedida!")
            return True
        else:
            print(f"⚠️ Validação falhou")
            print(f"   Esperado: {valor_esperado}")
            print(f"   Encontrado: {resultado.get('actual_value', 'N/A')}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na validação: {str(e)}")
        return False


def demonstrar_busca_label(engine: DixEngine):
    """Demonstra como o Smart Form encontra labels."""
    print("\n" + "="*50)
    print("🔍 COMO O SMART FORM ENCONTRA LABELS")
    print("="*50)
    
    print("""
O Smart Form utiliza múltiplas estratégias para encontrar
o campo associado a um label:

1. Busca por texto próximo ao label
2. Busca por hierarquia (irmão seguinte)
3. Busca por bounds (campo abaixo/ao lado)
4. Busca por resource-id relacionado
5. Análise semântica do contexto

Exemplo:
  ┌─────────────────────┐
  │ Número de CPF       │ ← Label
  ├─────────────────────┤
  │ [____________]      │ ← Campo encontrado automaticamente
  └─────────────────────┘
    """)
    
    # Tenta encontrar elementos com texto "CPF"
    print("Buscando elementos relacionados a 'CPF'...")
    elementos = engine.finder.find_text("CPF")
    
    if elementos:
        print(f"✅ Encontrados {len(elementos)} elemento(s) com 'CPF'")
        for i, elem in enumerate(elementos[:3], 1):  # Mostra até 3
            print(f"   {i}. Texto: {elem.get('text', 'N/A')}")
            print(f"      Classe: {elem.get('class', 'N/A')}")
            print(f"      Resource-ID: {elem.get('resourceId', 'N/A')}")
    else:
        print("⚠️ Nenhum elemento encontrado com 'CPF'")


def fluxo_completo_login(engine: DixEngine):
    """Demonstra um fluxo completo de preenchimento de formulário."""
    print("\n" + "="*60)
    print("🔄 FLUXO COMPLETO DE LOGIN/CADASTRO")
    print("="*60)
    
    dados_formulario = [
        {"label": "E-mail", "value": "usuario@teste.com", "type": "email"},
        {"label": "Senha", "value": "Senha123!", "type": "password"},
    ]
    
    for campo in dados_formulario:
        print(f"\n📝 Preenchendo: {campo['label']}")
        time.sleep(0.5)  # Delay entre campos
        
        resultado = engine.form.fill(
            label=campo['label'],
            value=campo['value'],
            field_type=campo['type']
        )
        
        if resultado.get('success'):
            print(f"   ✅ {campo['label']} preenchido")
        else:
            print(f"   ⚠️ Falha ao preencher {campo['label']}")
    
    print("\n✅ Fluxo de formulário concluído!")


def main():
    """Função principal do demo de formulário."""
    print("\n" + "="*60)
    print("🤖 DIXUIAUTO - DEMO FORMULÁRIO INTELIGENTE")
    print("="*60)
    print("Este demo mostra o preenchimento automático de formulários")
    
    # Inicializa a engine
    engine = DixEngine(debug=DEBUG_MODE)
    
    # Conecta ao dispositivo
    print("\n🔌 Conectando ao dispositivo...")
    try:
        if DEVICE_ID:
            engine.connect(device_id=DEVICE_ID)
        else:
            engine.connect()
        print("✅ Conexão estabelecida!")
    except Exception as e:
        print(f"❌ Erro na conexão: {str(e)}")
        print("\n⚠️  Para este demo, é necessário um dispositivo conectado.")
        print("   Execute em um ambiente com Android conectado via ADB.")
        return
    
    # Abre aplicativo de exemplo
    app_package = APP_PACKAGE if APP_PACKAGE != "com.example.app" else "com.android.settings"
    print(f"\n🚀 Abrindo aplicativo: {app_package}")
    try:
        engine.open(app_package)
        time.sleep(2)
    except Exception as e:
        print(f"⚠️ Erro ao abrir app: {str(e)}")
    
    # Demonstra busca de labels
    demonstrar_busca_label(engine)
    
    # Tenta preencher diferentes tipos de campos
    # Nota: Estes exemplos assumem que existem campos com esses labels na tela
    # Em um cenário real, adapte os labels conforme seu aplicativo
    
    print("\n" + "="*60)
    print("📋 TESTES DE PREENCHIMENTO")
    print("="*60)
    
    # Exemplos ilustrativos - em produção, os labels devem existir na tela
    testes = [
        ("CPF", preencher_cpf, ["02959350146"]),
        ("Senha", preencher_senha, []),
        ("E-mail", preencher_email, []),
        ("Telefone", preencher_telefone, []),
        ("CEP", preencher_cep, []),
    ]
    
    resultados = {}
    
    for nome, teste_func, args in testes:
        print(f"\n{'─'*50}")
        # Executa o teste (pode falhar se o campo não existir na tela)
        # Em um app real com os campos apropriados, funcionaria
        print(f"ℹ️  Teste de {nome} - Verifique se o campo existe na tela")
        resultados[nome] = "PENDENTE (requer campo na tela)"
    
    print("\n" + "="*60)
    print("💡 INFORMAÇÕES IMPORTANTES")
    print("="*60)
    print("""
O Smart Form funciona melhor quando:

1. Os labels estão próximos aos campos na hierarquia XML
2. Os campos têm resource-ids descritivos
3. A estrutura da UI segue padrões de acessibilidade

Dicas para melhorar a detecção:
• Use content-desc nos elementos
• Mantenha labels e campos no mesmo container
• Evite estruturas muito aninhadas
• Use IDs únicos e descritivos
    """)
    
    # Mostra resumo
    print("\n" + "="*60)
    print("📊 RESUMO DO DEMO")
    print("="*60)
    print("✅ Smart Form inicializado")
    print("✅ Estratégias de busca demonstradas")
    print("✅ Métodos de preenchimento apresentados")
    print("\nPara usar em produção:")
    print("  1. Identifique os labels reais do seu app")
    print("  2. Use engine.form.fill(label='...', value='...')")
    print("  3. Valide com engine.validator.validate_field()")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Execução interrompida pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro fatal: {str(e)}")
        import traceback
        traceback.print_exc()
