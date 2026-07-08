#!/usr/bin/env python3
"""
Exemplo de uso do dixUIAuto
"""
import sys
sys.path.insert(0, '/workspace/dixUIAuto')

from main import DixEngine


def exemplo_basico():
    """Exemplo básico de automação."""
    engine = DixEngine()
    
    try:
        # Conectar ao dispositivo
        engine.connect()  # USB ou TCP
        
        # Abrir aplicativo
        engine.open("com.meuapp.android")
        
        # Aguardar tela carregar
        engine.wait(text="Bem-vindo", timeout=10)
        
        # Clicar em botão por texto
        engine.click(text="Entrar")
        
        # Preencher formulário
        engine.form.fill(label="CPF", value="02959350146")
        engine.form.fill(label="Senha", value="minhasenha123")
        
        # Clicar e aguardar
        engine.click(text="Acessar")
        engine.wait(text="Dashboard", timeout=10)
        
        # Capturar screenshot
        engine.screenshot("dashboard.png")
        
        print("✓ Automação concluída com sucesso!")
        
    except Exception as e:
        print(f"✗ Erro: {e}")
    finally:
        engine.disconnect()


def exemplo_com_flow():
    """Exemplo usando fluxo JSON."""
    engine = DixEngine()
    
    try:
        engine.connect()
        engine.open("com.meuapp.android")
        
        # Executar fluxo definido em JSON
        success = engine.flow.run("login_flow.json")
        
        if success:
            print("✓ Flow executado com sucesso!")
            stats = engine.flow.get_stats()
            print(f"  Passos: {stats['total_steps']}")
            print(f"  Sucesso: {stats['successful']}/{stats['total_steps']}")
        
    except Exception as e:
        print(f"✗ Erro no flow: {e}")
    finally:
        engine.disconnect()


def exemplo_avancado():
    """Exemplo avançado com inspeção e validações."""
    from lib.inspector import SmartInspector
    
    engine = DixEngine()
    
    try:
        engine.connect()
        engine.open("com.meuapp.android")
        
        # Obter árvore UI
        _, root = engine.dumper.dump()
        
        # Analisar elementos
        inspector = SmartInspector()
        framework = inspector.detect_ui_framework(root)
        print(f"Framework detectado: {framework}")
        
        # Resumo da UI
        summary = engine.get_ui_summary()
        print(f"Elementos na tela: {summary.get('total_nodes', 0)}")
        print(f"Botões: {summary.get('buttons', 0)}")
        print(f"Campos de input: {summary.get('edit_texts', 0)}")
        
        # Validar elemento
        node = engine.finder.find_text("Login")
        if engine.validator.assert_visible(node, "Tela de login visível"):
            print("✓ Validação passou")
        
    except Exception as e:
        print(f"✗ Erro: {e}")
    finally:
        engine.disconnect()


if __name__ == "__main__":
    print("=" * 50)
    print("dixUIAuto - Demo de Uso")
    print("=" * 50)
    
    print("\n1. Exemplo Básico:")
    exemplo_basico()
    
    print("\n2. Exemplo com Flow:")
    exemplo_com_flow()
    
    print("\n3. Exemplo Avançado:")
    exemplo_avancado()
