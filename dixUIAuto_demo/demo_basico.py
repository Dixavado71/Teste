"""
Demo Básico - dixUIAuto

Este script demonstra as funcionalidades básicas do framework:
- Conexão com dispositivo
- Listagem de dispositivos
- Abrir aplicativo
- Localizar e clicar em elementos
- Esperar por elementos na tela
"""

import sys
import os

# Adiciona o diretório pai ao path para importar o dixUIAuto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import DixEngine
from config import (
    APP_PACKAGE,
    DEVICE_ID,
    DEFAULT_TIMEOUT,
    ELEMENT_WAIT_TIMEOUT,
    DEBUG_MODE
)


def listar_dispositivos(engine: DixEngine):
    """Lista todos os dispositivos conectados."""
    print("\n" + "="*50)
    print("📱 DISPOSITIVOS CONECTADOS")
    print("="*50)
    
    devices = engine.device.list_devices()
    
    if not devices:
        print("❌ Nenhum dispositivo encontrado!")
        print("\nVerifique:")
        print("  1. O dispositivo está conectado via USB?")
        print("  2. A depuração USB está ativada?")
        print("  3. O adb está instalado e no PATH?")
        return False
    
    for i, device in enumerate(devices, 1):
        status = "✅" if device.get('status') == 'device' else "⚠️"
        print(f"  {i}. {status} {device.get('id', 'N/A')} - {device.get('status', 'unknown')}")
    
    return True


def conectar_dispositivo(engine: DixEngine):
    """Conecta ao dispositivo Android."""
    print("\n" + "="*50)
    print("🔌 CONECTANDO AO DISPOSITIVO")
    print("="*50)
    
    try:
        if DEVICE_ID:
            print(f"Conectando ao dispositivo: {DEVICE_ID}")
            engine.connect(device_id=DEVICE_ID)
        else:
            print("Conectando ao primeiro dispositivo disponível...")
            engine.connect()
        
        print("✅ Conexão estabelecida com sucesso!")
        
        # Informações do dispositivo
        info = engine.device.get_device_info()
        print(f"\n📱 Informações do dispositivo:")
        print(f"   Modelo: {info.get('model', 'N/A')}")
        print(f"   Versão Android: {info.get('version', 'N/A')}")
        print(f"   Serial: {info.get('serial', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na conexão: {str(e)}")
        return False


def abrir_aplicativo(engine: DixEngine, package: str):
    """Abre um aplicativo no dispositivo."""
    print("\n" + "="*50)
    print(f"🚀 ABRINDO APLICATIVO: {package}")
    print("="*50)
    
    try:
        engine.open(package)
        print(f"✅ Aplicativo {package} iniciado!")
        return True
    except Exception as e:
        print(f"⚠️ Erro ao abrir aplicativo: {str(e)}")
        print("   Continuando com a demonstração...")
        return False


def esperar_elemento(engine: DixEngine, **kwargs):
    """Espera por um elemento na tela."""
    print(f"\n⏳ Aguardando elemento: {kwargs}")
    
    try:
        found = engine.wait(**kwargs, timeout=ELEMENT_WAIT_TIMEOUT)
        if found:
            print(f"✅ Elemento encontrado!")
            return True
        else:
            print(f"⚠️ Elemento não encontrado no tempo limite")
            return False
    except Exception as e:
        print(f"❌ Erro ao esperar elemento: {str(e)}")
        return False


def clicar_elemento(engine: DixEngine, **kwargs):
    """Clica em um elemento na tela."""
    print(f"\n👆 Clicando em elemento: {kwargs}")
    
    try:
        result = engine.click(**kwargs)
        if result:
            print(f"✅ Clique realizado com sucesso!")
            return True
        else:
            print(f"⚠️ Elemento não encontrado para clique")
            return False
    except Exception as e:
        print(f"❌ Erro ao clicar: {str(e)}")
        return False


def capturar_screenshot(engine: DixEngine, nome: str):
    """Captura uma screenshot da tela atual."""
    print(f"\n📸 Capturando screenshot: {nome}")
    
    try:
        caminho = engine.screenshot(nome)
        print(f"✅ Screenshot salva em: {caminho}")
        return True
    except Exception as e:
        print(f"❌ Erro ao capturar screenshot: {str(e)}")
        return False


def obter_xml_atual(engine: DixEngine):
    """Obtém o XML da interface atual."""
    print("\n" + "="*50)
    print("📄 OBTENDO XML DA INTERFACE")
    print("="*50)
    
    try:
        xml = engine.dump()
        print(f"✅ XML obtido com sucesso!")
        print(f"   Tamanho: {len(xml)} bytes")
        
        # Mostra primeiros 500 caracteres como exemplo
        print(f"\n📋 Preview do XML (primeiros 500 chars):")
        print("-" * 50)
        print(xml[:500])
        print("-" * 50)
        print("...")
        
        return True
    except Exception as e:
        print(f"❌ Erro ao obter XML: {str(e)}")
        return False


def buscar_elementos(engine: DixEngine):
    """Demonstra diferentes estratégias de busca."""
    print("\n" + "="*50)
    print("🔍 ESTRATÉGIAS DE BUSCA")
    print("="*50)
    
    estrategias = [
        ("find_text", {"text": "OK"}),
        ("find_desc", {"desc": "Back"}),
        ("find_class", {"className": "android.widget.Button"}),
        ("find_resource", {"resourceId": "android:id/button1"}),
    ]
    
    for metodo, params in estrategias:
        print(f"\n  Testando {metodo}({params})...")
        try:
            finder = getattr(engine.finder, metodo)
            elementos = finder(**params)
            if elementos:
                print(f"    ✅ {len(elementos)} elemento(s) encontrado(s)")
            else:
                print(f"    ⚠️ Nenhum elemento encontrado")
        except Exception as e:
            print(f"    ❌ Erro: {str(e)}")


def main():
    """Função principal do demo básico."""
    print("\n" + "="*60)
    print("🤖 DIXUIAUTO - DEMO BÁSICO")
    print("="*60)
    print("Este demo mostra as funcionalidades básicas do framework")
    
    # Inicializa a engine
    engine = DixEngine(debug=DEBUG_MODE)
    
    # 1. Lista dispositivos
    if not listar_dispositivos(engine):
        print("\n⚠️  Sem dispositivos disponíveis. Conecte um dispositivo e tente novamente.")
        return
    
    # 2. Conecta ao dispositivo
    if not conectar_dispositivo(engine):
        return
    
    # 3. Abre aplicativo (exemplo com package genérico)
    # Substitua pelo package do seu aplicativo
    app_package = APP_PACKAGE if APP_PACKAGE != "com.example.app" else "com.android.settings"
    print(f"\n💡 Usando package: {app_package}")
    abrir_aplicativo(engine, app_package)
    
    # Pequeno delay para o app carregar
    import time
    time.sleep(2)
    
    # 4. Captura screenshot inicial
    capturar_screenshot(engine, "tela_inicial")
    
    # 5. Obtém XML da interface
    obter_xml_atual(engine)
    
    # 6. Demonstra estratégias de busca
    buscar_elementos(engine)
    
    # 7. Exemplo de espera por elemento
    # Tenta encontrar elementos comuns
    esperar_elemento(engine, text="OK")
    esperar_elemento(engine, className="android.widget.Button")
    
    # 8. Exemplo de clique (se encontrar)
    clicar_elemento(engine, text="OK")
    
    # 9. Captura screenshot final
    capturar_screenshot(engine, "tela_final")
    
    print("\n" + "="*60)
    print("✅ DEMO BÁSICO CONCLUÍDO!")
    print("="*60)
    print("\nPróximos passos:")
    print("  • Execute demo_formulario.py para ver preenchimento automático")
    print("  • Execute demo_fluxo_json.py para ver execução de fluxos")
    print("  • Execute demo_avancado.py para recursos avançados")
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
