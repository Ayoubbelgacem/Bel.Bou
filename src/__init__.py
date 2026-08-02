# Bou.Bel - Main package
__version__ = "2.0.0"
__author__ = "Bou.Bel Team"

# Imports nécessaires pour le package
from src.lexer.lexer import Lexer
from src.parser.parser import Parser
from src.interpreter.interpreter import Interpreter
from src.cli.repl import REPL

# Exporter les symboles principaux
__all__ = [
    'Lexer', 
    'Parser', 
    'Interpreter', 
    'REPL',
    '__version__',
    '__author__'
]