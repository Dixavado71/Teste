"""
Demo Avançado - dixUIAuto

Este script demonstra recursos avançados do framework:
- Gestos complexos (scroll, swipe, pinch, zoom)
- Watcher para monitoramento de mudanças de tela
- Validator para validações avançadas
- Múltiplas estratégias de busca combinadas
- Screenshots com marcações
- Trabalho com cache de UI
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
    ENABLE_CACHE,
    WATCHER_INTERVAL
)


def demonstrar_gestos(engine: DixEngine):
    """Demonstra todos os gestos suportados."""
    print("\n" + "="*60)
    print("👆 GESTOS SUPORTADOS")
    print("="*60)
    
    # Swipe (deslizar)
    print("\n1. SWIPE (Deslizar)")
    print("   • Direções: up, down, left, right")
    print("   • Percentual: 0.1 a 1.0")
    
    try:
        # Exemplo de swipe para cima (50% da tela)
        print("   → Executando swipe up...")
        engine.gestures.swipe(direction='up', percent=0.5)
        print("   ✅ Swipe executado")
        time.sleep(0.5)
    except Exception as e:
        print(f"   ⚠️ Swipe: {str(e)}")
    
    # Scroll
    print("\n2. SCROLL (Rolar)")
    print("   • Para listas e ScrollView")
    print("   • Steps: quantidade de passos")
    
    try:
        print("   → Executando scroll down...")
        engine.gestures.scroll(direction='down', steps=5)
        print("   ✅ Scroll executado")
        time.sleep(0.5)
    except Exception as e:
        print(f"   ⚠️ Scroll: {str(e)}")
    
    # Drag (arrastar)
    print("\n3. DRAG (Arrastar)")
    print("   • Move elemento de uma posição para outra")
    
    try:
        print("   → Exemplo de drag (teórico)...")
        print("      engine.gestures.drag(start_x, start_y, end_x, end_y)")
    except Exception as e:
        print(f"   ⚠️ Drag: {str(e)}")
    
    # Pinch (pinça)
    print("\n4. PINCH (Pinça)")
    print("   • Zoom in/out com dois dedos")
    
    try:
        print("   → Exemplo de pinch (teórico)...")
        print("      engine.gestures.pinch(scale=0.5)  # Zoom out")
        print("      engine.gestures.pinch(scale=2.0)  # Zoom in")
    except Exception as e:
        print(f"   ⚠️ Pinch: {str(e)}")
    
    # Multi-touch
    print("\n5. MULTI-TOUCH")
    print("   • Múltiplos toques simultâneos")
    
    try:
        print("   → Exemplo de multi-touch (teórico)...")
        print("      engine.gestures.multi_touch([(x1,y1), (x2,y2)])")
    except Exception as e:
        print(f"   ⚠️ Multi-touch: {str(e)}")


def demonstrar_watcher(engine: DixEngine):
    """Demonstra o sistema de watcher."""
    print("\n" + "="*60)
    print("👁️ WATCHER (Observador de Tela)")
    print("="*60)
    
    print("""
O Watcher monitora mudanças na interface em tempo real:

• Detecta quando a tela muda
• Atualiza cache automaticamente
• Notifica a engine sobre mudanças
• Evita polling desnecessário

Funcionamento:
  Tela mudou? 
    ↓ SIM
  Atualiza XML → Atualiza Cache → Notifica Engine
    ↓ NÃO
  Mantém cache atual
    """)
    
    try:
        # Inicia watcher
        print("🔍 Iniciando watcher...")
        engine.watcher.start(interval=WATCHER_INTERVAL)
        print("✅ Watcher iniciado")
        
        # Aguarda brevemente para demonstração
        time.sleep(1)
        
        # Verifica se há mudanças
        mudou = engine.watcher.has_changed()
        print(f"📊 Mudanças detectadas: {mudou}")
        
        # Para watcher
        engine.watcher.stop()
        print("⏹️ Watcher parado")
        
    except Exception as e:
        print(f"⚠️ Erro no watcher: {str(e)}")


def demonstrar_validator(engine: DixEngine):
    """Demonstra o sistema de validação."""
    print("\n" + "="*60)
    print("✓ VALIDATOR (Validador)")
    print("="*60)
    
    print("""
O Validator confirma operações e estados:

• Valida se elemento existe
• Confirma texto em elemento
• Verifica atributos específicos
• Valida formulários preenchidos
• Detecta popups e erros
    """)
    
    # Tipos de validação
    print("\n📋 TIPOS DE VALIDAÇÃO:")
    
    validations = [
        ("validate_exists", "Verifica se elemento existe"),
        ("validate_text", "Confirma texto do elemento"),
        ("validate_attribute", "Valida atributo específico"),
        ("validate_field", "Valida campo preenchido"),
        ("validate_screen", "Valida tela atual"),
        ("validate_popup", "Detecta popups"),
        ("validate_error", "Detecta mensagens de erro"),
    ]
    
    for metodo, descricao in validations:
        print(f"  • {metodo:20} - {descricao}")
    
    # Exemplo prático
    print("\n🔍 Exemplo de uso:")
    print("""
    # Validar que elemento existe
    result = engine.validator.validate_exists(text="OK")
    
    # Validar texto específico
    result = engine.validator.validate_text(
        resourceId="com.app:id/title",
        expected_text="Home"
    )
    
    # Validar campo preenchido
    result = engine.validator.validate_field(
        label="CPF",
        expected_value="029.593.501-46"
    )
    """)


def demonstrar_busca_avancada(engine: DixEngine):
    """Demonstra estratégias avançadas de busca."""
    print("\n" + "="*60)
    print("🔍 BUSCA AVANÇADA DE ELEMENTOS")
    print("="*60)
    
    print("""
Estratégias de busca disponíveis:
    """)
    
    estrategias = [
        ("find_text()", "Busca por texto exato ou parcial"),
        ("find_desc()", "Busca por content-description"),
        ("find_resource()", "Busca por resource-id"),
        ("find_class()", "Busca por classe Android"),
        ("find_xpath()", "Busca por XPath"),
        ("find_regex()", "Busca por expressão regular"),
        ("find_multiple()", "Combina múltiplos critérios"),
        ("find_first()", "Retorna primeiro resultado"),
        ("find_visible()", "Filtra apenas elementos visíveis"),
        ("find_clickable()", "Filtra apenas elementos clicáveis"),
    ]
    
    for metodo, descricao in estrategias:
        print(f"  • {metodo:20} - {descricao}")
    
    # Exemplos de combinações
    print("\n📋 EXEMPLOS DE COMBINAÇÕES:")
    print("""
    # Buscar botão clicável com texto específico
    elementos = engine.finder.find_multiple(
        text="Entrar",
        className="android.widget.Button",
        clickable=True
    )
    
    # Buscar por regex
    elementos = engine.finder.find_regex(
        textRegex=".*Login.*",
        className=".*Button.*"
    )
    
    # Buscar primeiro elemento visível
    elemento = engine.finder.find_first(
        text="OK",
        visible=True
    )
    
    # XPath complexo
    elemento = engine.finder.find_xpath(
        "//android.widget.Button[@text='Entrar']"
    )
    """)
    
    # Tenta buscar elementos reais
    print("\n🔎 Buscando elementos na tela atual...")
    
    try:
        # Busca por classe comum
        botoes = engine.finder.find_class("android.widget.Button")
        if botoes:
            print(f"   ✅ Encontrados {len(botoes)} botão(ões)")
        else:
            print("   ⚠️ Nenhum botão encontrado")
        
        # Busca textos
        textos = engine.finder.find_text("")
        if textos:
            print(f"   ✅ Encontrados {len(textos)} elemento(s) com texto")
            # Mostra alguns exemplos
            for t in textos[:3]:
                texto = t.get('text', '')[:30]
                print(f"      • '{texto}'")
                
    except Exception as e:
        print(f"   ⚠️ Erro na busca: {str(e)}")


def demonstrar_locator(engine: DixEngine):
    """Demonstra recursos de localização espacial."""
    print("\n" + "="*60)
    print("📍 LOCATOR (Localização Espacial)")
    print("="*60)
    
    print("""
O Locator calcula relações espaciais entre elementos:

• Centro do elemento
• Distância entre elementos
• Proximidade
• Sobreposição
• Relações hierárquicas (pai, filho, irmão)
    """)
    
    print("📋 MÉTODOS DISPONÍVEIS:")
    
    metodos = [
        ("get_center()", "Calcula centro do elemento"),
        ("get_bounds()", "Obtém limites (bounds)"),
        ("distance_to()", "Distância até outro elemento"),
        ("is_near()", "Verifica proximidade"),
        ("overlaps()", "Verifica sobreposição"),
        ("get_parent()", "Obtém elemento pai"),
        ("get_children()", "Obtém elementos filhos"),
        ("get_siblings()", "Obtém elementos irmãos"),
        ("find_nearest()", "Encontra elemento mais próximo"),
    ]
    
    for metodo, descricao in metodos:
        print(f"  • {metodo:20} - {descricao}")
    
    print("\n📋 EXEMPLO DE USO:")
    print("""
    # Localizar campo próximo a um label
    label = engine.finder.find_text("CPF")
    campo = engine.locator.find_nearest(
        element=label,
        target_class="android.widget.EditText"
    )
    
    # Calcular distância entre elementos
    distancia = engine.locator.distance_to(elem1, elem2)
    
    # Verificar se elementos estão próximos
    proximo = engine.locator.is_near(elem1, elem2, threshold=50)
    """)


def demonstrar_cache(engine: DixEngine):
    """Demonstra o sistema de cache."""
    print("\n" + "="*60)
    print("💾 CACHE ENGINE")
    print("="*60)
    
    print("""
O cache evita dumps XML desnecessários:

1. Dump XML inicial
2. Calcula hash SHA256
3. Próxima verificação:
   • Hash igual? Usa cache
   • Hash diferente? Atualiza
   
Benefícios:
• Reduz latência
• Diminui consumo de CPU
• Acelera automação
    """)
    
    try:
        # Status do cache
        status = engine.cache.get_status()
        print(f"📊 Status do cache:")
        print(f"   Habilitado: {status.get('enabled', False)}")
        print(f"   Entries: {status.get('entries', 0)}")
        print(f"   Hits: {status.get('hits', 0)}")
        print(f"   Misses: {status.get('misses', 0)}")
        
        # Limpa cache (demonstração)
        print("\n🧹 Limpando cache...")
        engine.cache.clear()
        print("   ✅ Cache limpo")
        
    except Exception as e:
        print(f"⚠️ Erro ao acessar cache: {str(e)}")


def demonstrar_screenshots(engine: DixEngine):
    """Demonstra captura de screenshots."""
    print("\n" + "="*60)
    print("📸 SCREENSHOTS")
    print("="*60)
    
    try:
        # Screenshot simples
        print("\n📷 Capturando screenshot...")
        caminho = engine.screenshot("demo_avancado")
        print(f"   ✅ Salvo em: {caminho}")
        
        # Screenshot com região específica
        print("\n📷 Screenshot com região (exemplo teórico):")
        print("   engine.screenshot('regiao', bounds=(x, y, width, height))")
        
        # Screenshot de elemento específico
        print("\n📷 Screenshot de elemento (exemplo teórico):")
        print("   element = engine.finder.find_text('Logo')")
        print("   engine.screenshot_element(element, 'logo')")
        
    except Exception as e:
        print(f"⚠️ Erro ao capturar screenshot: {str(e)}")


def demonstrar_dumper_parser(engine: DixEngine):
    """Demonstra dump e parse de XML."""
    print("\n" + "="*60)
    print("📄 DUMPER & PARSER XML")
    print("="*60)
    
    try:
        # Obtém XML atual
        print("\n📋 Obtendo XML da interface...")
        xml_content = engine.dump()
        
        print(f"   ✅ XML obtido ({len(xml_content)} bytes)")
        
        # Parseia XML
        print("\n🔍 Parseando XML...")
        arvore = engine.parser.parse(xml_content)
        
        print(f"   ✅ Árvore parseada")
        print(f"   Profundidade máxima: {arvore.get('max_depth', 'N/A')}")
        print(f"   Total de elementos: {arvore.get('total_elements', 'N/A')}")
        
        # Mostra estrutura resumida
        print("\n📊 Estrutura da UI (resumo):")
        elementos_comuns = {}
        
        for elem in arvore.get('elements', [])[:20]:  # Primeiros 20
            classe = elem.get('class', 'unknown')
            elementos_comuns[classe] = elementos_comuns.get(classe, 0) + 1
        
        for classe, count in sorted(elementos_comuns.items(), key=lambda x: -x[1])[:5]:
            print(f"   • {classe}: {count} elemento(s)")
            
    except Exception as e:
        print(f"⚠️ Erro no dump/parser: {str(e)}")


def main():
    """Função principal do demo avançado."""
    print("\n" + "="*70)
    print("🤖 DIXUIAUTO - DEMO AVANÇADO")
    print("="*70)
    print("Este demo mostra recursos avançados do framework")
    
    # Inicializa a engine
    engine = DixEngine(debug=DEBUG_MODE, enable_cache=ENABLE_CACHE)
    
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
        return
    
    # Abre aplicativo de exemplo
    app_package = APP_PACKAGE if APP_PACKAGE != "com.example.app" else "com.android.settings"
    print(f"\n🚀 Abrindo aplicativo: {app_package}")
    try:
        engine.open(app_package)
        time.sleep(2)
    except Exception as e:
        print(f"⚠️ Erro ao abrir app: {str(e)}")
    
    # Executa todas as demonstrações
    print("\n" + "="*70)
    print("INICIANDO DEMONSTRAÇÕES")
    print("="*70)
    
    # 1. Gestos
    demonstrar_gestos(engine)
    
    # 2. Watcher
    demonstrar_watcher(engine)
    
    # 3. Validator
    demonstrar_validator(engine)
    
    # 4. Busca avançada
    demonstrar_busca_avancada(engine)
    
    # 5. Locator
    demonstrar_locator(engine)
    
    # 6. Cache
    demonstrar_cache(engine)
    
    # 7. Screenshots
    demonstrar_screenshots(engine)
    
    # 8. Dumper & Parser
    demonstrar_dumper_parser(engine)
    
    # Resumo final
    print("\n" + "="*70)
    print("✅ DEMO AVANÇADO CONCLUÍDO!")
    print("="*70)
    print("""
Recursos demonstrados:
  ✅ Gestos (swipe, scroll, drag, pinch, multi-touch)
  ✅ Watcher (monitoramento de mudanças)
  ✅ Validator (validações avançadas)
  ✅ Busca avançada (múltiplas estratégias)
  ✅ Locator (localização espacial)
  ✅ Cache engine (otimização)
  ✅ Screenshots
  ✅ Dumper & Parser XML

Próximos passos:
  • Combine recursos para criar automações complexas
  • Use watcher + validator para fluxos robustos
  • Aproveite o cache para melhor performance
  • Crie seus próprios módulos customizados
    """)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Execução interrompida pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro fatal: {str(e)}")
        import traceback
        traceback.print_exc()
