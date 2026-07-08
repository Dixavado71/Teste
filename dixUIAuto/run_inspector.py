#!/usr/bin/env python3
"""
Launcher para o Live Inspector do dixUIAuto
Ferramenta de inspeção em tempo real da UI Android
"""

import sys
import os

# Adicionar path do projeto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    try:
        from gui.live_inspector import LiveInspector
        
        print("🔍 Iniciando dixUIAuto - Live Inspector")
        print("=" * 60)
        print("\n💡 Dicas de uso:")
        print("   1. Conecte seu dispositivo Android via USB")
        print("   2. Habilite a depuração USB no dispositivo")
        print("   3. Clique em 'Capturar UI' para ver a árvore de elementos")
        print("   4. Selecione um elemento para ver detalhes e gerar código")
        print("   5. Use filtros para encontrar elementos específicos")
        print("=" * 60)
        
        # Tentar inicializar com engine
        try:
            from main import DixEngine
            engine = DixEngine()
            engine.connect()
            app = LiveInspector(engine)
        except Exception as e:
            print(f"⚠️  Aviso: Não foi possível conectar à engine ({e})")
            print("   O inspector funcionará sem conexão automática")
            app = LiveInspector()
        
        app.mainloop()
        
    except ImportError as e:
        print("❌ Erro ao importar módulos do Inspector")
        print(f"Detalhes: {e}")
        print("\n💡 Instale as dependências:")
        print("   pip install -r gui/requirements_gui.txt")
        sys.exit(1)
    
    except Exception as e:
        print(f"❌ Erro ao iniciar Inspector: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
