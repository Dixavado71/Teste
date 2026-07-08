#!/usr/bin/env python3
"""
Launcher para a GUI Premium do dixUIAuto.
"""

import sys
from pathlib import Path

# Adicionar root ao path
sys.path.insert(0, str(Path(__file__).parent))

from gui.premium_gui import main

if __name__ == "__main__":
    main()
