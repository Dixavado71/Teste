#!/usr/bin/env python3
"""
Launcher para a GUI do dixUIAuto
Inicia a interface gráfica premium dark
"""

import sys
import os

# Adicionar path do projeto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    try:
        from gui.premium_gui import DixUIGUI
        
        print("🚀 Iniciando dixUIAuto - Android Automation Studio")
        print("=" * 60)
        
        app = DixUIGUI()
        app.run()
        
    except ImportError as e:
        print("❌ Erro ao importar módulos da GUI")
        print(f"Detalhes: {e}")
        print("\n💡 Instale as dependências:")
        print("   pip install -r gui/requirements_gui.txt")
        sys.exit(1)
    
    except Exception as e:
        print(f"❌ Erro ao iniciar GUI: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
