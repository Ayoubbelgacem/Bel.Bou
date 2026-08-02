# src/lexer/tokenizer.py
# Alias pour lexer.py - maintient la compatibilité

from .lexer import Lexer as Tokenizer
from .token import Token, TokenType

__all__ = ['Tokenizer', 'Token', 'TokenType']