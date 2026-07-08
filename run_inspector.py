#!/usr/bin/env python3
"""
Launcher para o Live Inspector do dixUIAuto.
"""

import sys
from pathlib import Path

# Adicionar root ao path
sys.path.insert(0, str(Path(__file__).parent))

from gui.live_inspector import main

if __name__ == "__main__":
    main()
