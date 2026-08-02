"""
Modules LLVM pour Bou.Bel - Version décomposée
Génération de code natif via LLVM
"""

import sys
import os

# Ajouter le chemin du projet pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from .runtime import RuntimeHelper
from .utils import UtilsHelper
from .types import TypesHelper
from .arrays import ArraysHelper
from .strings import StringsHelper
from .expressions import ExpressionsHelper
from .statements import StatementsHelper
from .builtins import BuiltinsHelper
from .oop import OOPHelper
from .files import FilesHelper
from .control_flow import ControlFlowHelper

__all__ = [
    'RuntimeHelper',
    'UtilsHelper',
    'TypesHelper',
    'ArraysHelper',
    'StringsHelper',
    'ExpressionsHelper',
    'StatementsHelper',
    'BuiltinsHelper',
    'OOPHelper',
    'FilesHelper',
    'ControlFlowHelper',
]