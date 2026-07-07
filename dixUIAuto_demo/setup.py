"""
Script de inicialização rápida - dixUIAuto Demo

Execute este script para verificar se tudo está configurado corretamente.
"""

import sys
import os

def verificar_pre_requisitos():
    """Verifica se todos os pré-requisitos estão instalados."""
    print("="*60)
    print("🔍 VERIFICANDO PRÉ-REQUISITOS")
    print("="*60)
    
    erros = []
    
    # Verificar Python
    print(f"\n✓ Python: {sys.version.split()[0]}")
    
    # Verificar módulos do dixUIAuto
    print("\n📦 Verificando módulos do dixUIAuto...")
    
    modulos = [
        'main',
        'config.settings',
        'lib.adb_bridge',
        'lib.device',
        'lib.cache',
        'lib.parser',
        'lib.dumper',
        'lib.finder',
        'lib.locator',
        'lib.clicker',
        'lib.keyboard',
        'lib.gestures',
        'lib.watcher',
        'lib.validator',
        'lib.form',
        'lib.flow',
        'lib.engine',
    ]
    
    workspace = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    sys.path.insert(0, workspace)
    
    for modulo in modulos:
        try:
            __import__(modulo.replace('/', '.'))
            print(f"   ✅ {modulo}")
        except ImportError as e:
            print(f"   ❌ {modulo} - {str(e)}")
            erros.append(modulo)
    
    # Verificar dependências externas
    print("\n📦 Verificando dependências externas...")
    
    dependencias = [
        ('uiautomator2', 'uiautomator2'),
        ('PIL', 'Pillow'),
        ('requests', 'requests'),
    ]
    
    for import_name, package_name in dependencias:
        try:
            __import__(import_name)
            print(f"   ✅ {package_name}")
        except ImportError:
            print(f"   ❌ {package_name} - Não instalado")
            erros.append(package_name)
    
    # Verificar ADB
    print("\n🔌 Verificando ADB...")
    try:
        import subprocess
        result = subprocess.run(['adb', 'version'], 
                              capture_output=True, 
                              text=True, 
                              timeout=5)
        if result.returncode == 0:
            versao = result.stdout.split('\n')[0]
            print(f"   ✅ {versao}")
        else:
            print(f"   ⚠️ ADB instalado mas com problemas")
            erros.append('ADB')
    except FileNotFoundError:
        print(f"   ❌ ADB não encontrado no PATH")
        erros.append('ADB')
    except Exception as e:
        print(f"   ⚠️ Erro ao verificar ADB: {str(e)}")
        erros.append('ADB')
    
    # Resumo
    print("\n" + "="*60)
    if not erros:
        print("✅ TODOS OS PRÉ-REQUISITOS ESTÃO OK!")
        print("\nPróximos passos:")
        print("  1. Conecte um dispositivo Android via USB")
        print("  2. Ative a Depuração USB no dispositivo")
        print("  3. Execute: python demo_basico.py")
    else:
        print("⚠️ ALGUNS PRÉ-REQUISITOS FALTANDO:")
        for erro in erros:
            print(f"   • {erro}")
        print("\nPara instalar dependências Python:")
        print("   pip install -r requirements.txt")
        print("\nPara instalar ADB:")
        print("   Linux: sudo apt-get install adb")
        print("   Mac: brew install adb")
        print("   Windows: Baixe em https://developer.android.com/studio/releases/platform-tools")
    
    print("="*60)
    
    return len(erros) == 0


def testar_conexao():
    """Testa conexão com dispositivo Android."""
    print("\n" + "="*60)
    print("🔌 TESTANDO CONEXÃO COM DISPOSITIVO")
    print("="*60)
    
    try:
        import subprocess
        
        # Lista dispositivos
        result = subprocess.run(['adb', 'devices'], 
                              capture_output=True, 
                              text=True, 
                              timeout=5)
        
        linhas = result.stdout.strip().split('\n')
        
        if len(linhas) <= 1:
            print("\n❌ Nenhum dispositivo encontrado!")
            print("\nVerifique:")
            print("  1. Dispositivo conectado via USB")
            print("  2. Depuração USB ativada")
            print("  3. Driver USB instalado (Windows)")
            return False
        
        dispositivos = []
        for linha in linhas[1:]:
            if linha.strip():
                partes = linha.split()
                if len(partes) >= 2:
                    dispositivos.append({
                        'id': partes[0],
                        'status': partes[1]
                    })
        
        print(f"\n📱 Dispositivos encontrados: {len(dispositivos)}")
        
        for dev in dispositivos:
            status_icon = "✅" if dev['status'] == 'device' else "⚠️"
            print(f"   {status_icon} {dev['id']} - {dev['status']}")
        
        if any(d['status'] == 'device' for d in dispositivos):
            print("\n✅ Dispositivo disponível para testes!")
            return True
        else:
            print("\n⚠️ Dispositivos encontrados mas não prontos")
            return False
            
    except Exception as e:
        print(f"\n❌ Erro ao testar conexão: {str(e)}")
        return False


def mostrar_exemplos():
    """Mostra exemplos de uso rápido."""
    print("\n" + "="*60)
    print("📚 EXEMPLOS DE USO RÁPIDO")
    print("="*60)
    
    print("""
# Inicializar engine
from main import DixEngine
engine = DixEngine()

# Conectar
engine.connect()  # ou engine.connect(device_id="serial")

# Abrir aplicativo
engine.open("com.whatsapp")

# Clicar em elemento
engine.click(text="Aceitar")
engine.click(desc="Menu")
engine.click(resourceId="com.app:id/button")

# Esperar elemento
engine.wait(text="Home", timeout=10)

# Preencher formulário
engine.form.fill(label="CPF", value="02959350146")
engine.form.fill(label="Senha", value="123456")

# Gestos
engine.gestures.swipe(direction='up', percent=0.5)
engine.gestures.scroll(direction='down', steps=10)

# Screenshot
engine.screenshot("tela_login")

# Executar fluxo JSON
engine.flow.execute("flows/login_flow.json")
    """)


def main():
    """Função principal."""
    print("\n" + "="*60)
    print("🤖 DIXUIAUTO - SETUP INICIAL")
    print("="*60)
    
    # Verificar pré-requisitos
    ok = verificar_pre_requisitos()
    
    if ok:
        # Testar conexão
        testar_conexao()
        
        # Mostrar exemplos
        mostrar_exemplos()
        
        print("\n" + "="*60)
        print("✅ SETUP CONCLUÍDO!")
        print("="*60)
        print("\nExecute os demos:")
        print("  python demo_basico.py       - Funcionalidades básicas")
        print("  python demo_formulario.py   - Preenchimento de formulários")
        print("  python demo_fluxo_json.py   - Execução de fluxos JSON")
        print("  python demo_avancado.py     - Recursos avançados")
        print()
    else:
        print("\n⚠️  Complete a instalação antes de prosseguir.")
        print()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Erro: {str(e)}")
        import traceback
        traceback.print_exc()
