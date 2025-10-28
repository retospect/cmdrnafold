"""
cmdrnafold - Professional Python wrapper for ViennaRNA commandline tools.

This package provides both synchronous and asynchronous interfaces to the
ViennaRNA RNAFold command for RNA secondary structure prediction.
"""

__version__ = "0.0.6"
__author__ = "Reto Stamm"
__email__ = "reto@retospect.ch"
__license__ = "GPL-3.0-or-later"

from .RNA import (
    RNArunner,
    SyncRNArunner, 
    RNAFoldError,
    fold_compound,
    fold_compound_sync,
)

# Create a module-level RNA interface for backward compatibility
class RNA:
    """RNA module interface for backward compatibility."""
    
    @staticmethod
    def fold_compound(sequence: str) -> SyncRNArunner:
        """Create a synchronous fold compound (backward compatible)."""
        return fold_compound_sync(sequence)

__all__ = [
    "__version__",
    "__author__", 
    "__email__",
    "__license__",
    "RNA",
    "RNArunner",
    "SyncRNArunner",
    "RNAFoldError", 
    "fold_compound",
    "fold_compound_sync",
]
