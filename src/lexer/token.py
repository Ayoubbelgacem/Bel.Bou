from enum import Enum

class TokenType(Enum):
    # Keywords
    KEYWORD = "KEYWORD"
    IDENTIFIER = "IDENTIFIER"
    NUMBER = "NUMBER"
    REAL = "REAL"
    STRING = "STRING"
    CHAR = "CHAR"
    
    # Symbols
    EQUALS = "EQUALS"
    PLUS = "PLUS"
    MINUS = "MINUS"
    STAR = "STAR"
    SLASH = "SLASH"
    MOD = "MOD"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    LBRACE = "LBRACE"
    RBRACE = "RBRACE"
    LBRACKET = "LBRACKET"
    RBRACKET = "RBRACKET"
    SEMICOLON = "SEMICOLON"
    COLON = "COLON"
    COMMA = "COMMA"
    DOT = "DOT"
    
    # Comparisons
    GREATER = "GREATER"
    LESS = "LESS"
    GREATER_EQUAL = "GREATER_EQUAL"
    LESS_EQUAL = "LESS_EQUAL"
    EQUAL_EQUAL = "EQUAL_EQUAL"
    NOT_EQUAL = "NOT_EQUAL"
    
    # Logical operators
    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    
    # Assignment
    PLUS_EQUALS = "PLUS_EQUALS"
    MINUS_EQUALS = "MINUS_EQUALS"
    STAR_EQUALS = "STAR_EQUALS"
    SLASH_EQUALS = "SLASH_EQUALS"
    
    EOF = "EOF"
    UNKNOWN = "UNKNOWN"

class Token:
    def __init__(self, type, value, line, column):
        self.type = type
        self.value = value
        self.line = line
        self.column = column
    
    def __repr__(self):
        return f"Token({self.type}, '{self.value}', line={self.line}, col={self.column})"
    
    def __str__(self):
        return f"<{self.type.value}: '{self.value}'>"

# Tunisian Arabic keywords
KEYWORDS = {
    "khdem": "VARIABLE",
    "ikteb": "PRINT",
    "iqra": "INPUT",
    "ken": "IF",
    "sinon": "ELSE",
    "sinon_ken": "ELSE_IF",
    "and": "AND",
    "or": "OR",
    "not": "NOT",
    "min": "MIN",
    "men": "FOR",
    "hatta": "TO",
    "7ata": "TO",
    "a3mel": "DO",
    "tawa": "WHILE",
    "dallel": "FUNCTION",          # version tunisienne
    "fonction": "FUNCTION",        # version francisée
    "rejje": "RETURN",             # version tunisienne
    "retourner": "RETURN",         # version francisée
    "class": "CLASS",
    "toroth": "INHERITS",
    "jdid": "NEW",
    "new": "NEW",
    "hetha": "THIS",
    "super": "SUPER",
    "s7i7": "TRUE",
    "ghalet": "FALSE",
    "null": "NULL",
    "jib": "IMPORT",               # import
    "7awel": "TRY",
    "ebsed": "CATCH",
    "akhir": "FINALLY",
    "wakaf": "BREAK",
    "tkhata": "CONTINUE",
    "int": "TYPE_INT",
    "real": "TYPE_REAL",
    "string": "TYPE_STRING",
    "bool": "TYPE_BOOL",
    "char": "TYPE_CHAR",
}