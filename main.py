"""
dixUIAuto - Android UI Automation Framework

Main entry point for the dixUIAuto framework.
"""

from lib.engine import DixEngine

__version__ = "0.1.0"
__all__ = ['DixEngine']


def create_engine() -> DixEngine:
    """
    Create and return a new DixEngine instance.
    
    Returns:
        DixEngine instance
    """
    return DixEngine()


# Convenience function for quick usage
engine = create_engine
