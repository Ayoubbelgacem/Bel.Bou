from src.lexer.token import Token, TokenType, KEYWORDS

class Lexer:
    def __init__(self, code):
        self.code = code
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens = []
        self.debug = False
    
    def tokenize(self, debug=False):
        self.debug = debug
        while self.position < len(self.code):
            char = self.current_char()
            
            if char.isspace():
                self.advance()
                continue
            if char == '#':
                self.skip_comment()
                continue
            if char.isdigit():
                if self.is_digit_led_word():
                    self.read_identifier()
                else:
                    self.read_number()
                continue
            if char == "'":
                self.read_char()
                continue
            if char == '"':
                self.read_string()
                continue
            if char.isalpha() or char == '_':
                self.read_identifier()
                continue
            self.read_symbol()
        
        self.tokens.append(Token(TokenType.EOF, "EOF", self.line, self.column))
        
        if self.debug:
            print("\n" + "="*60)
            print("TOKENS GENERATED:")
            print("="*60)
            for i, t in enumerate(self.tokens):
                print(f"  {i:3d}: {t}")
            print("="*60 + "\n")
        
        return self.tokens
    
    def current_char(self):
        if self.position < len(self.code):
            return self.code[self.position]
        return '\0'
    
    def advance(self):
        if self.current_char() == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        self.position += 1
    
    def skip_comment(self):
        while self.position < len(self.code) and self.current_char() != '\n':
            self.advance()
    
    def is_digit_led_word(self):
        i = self.position
        while i < len(self.code) and (self.code[i].isalnum() or self.code[i] == '_'):
            if self.code[i].isalpha() or self.code[i] == '_':
                return True
            i += 1
        return False
    
    def read_number(self):
        start_line = self.line
        start_col = self.column
        number = ""
        is_real = False
        
        while self.position < len(self.code):
            char = self.current_char()
            if char.isdigit():
                number += char
                self.advance()
            elif char == '.' and not is_real:
                is_real = True
                number += char
                self.advance()
            else:
                break
        
        token_type = TokenType.REAL if is_real else TokenType.NUMBER
        value = float(number) if is_real else int(number)
        self.tokens.append(Token(token_type, value, start_line, start_col))
    
    def read_string(self):
        start_line = self.line
        start_col = self.column
        self.advance()
        string = ""
        
        while self.position < len(self.code):
            char = self.current_char()
            if char == '"':
                self.advance()
                break
            if char == '\\':
                self.advance()
                if self.position < len(self.code):
                    escape = self.current_char()
                    if escape == 'n':
                        string += '\n'
                    elif escape == 't':
                        string += '\t'
                    elif escape == '\\':
                        string += '\\'
                    elif escape == '"':
                        string += '"'
                    else:
                        string += escape
                    self.advance()
            else:
                string += char
                self.advance()
        
        self.tokens.append(Token(TokenType.STRING, string, start_line, start_col))
    
    def read_char(self):
        start_line = self.line
        start_col = self.column
        self.advance()
        char = self.current_char()
        self.advance()
        if self.current_char() == "'":
            self.advance()
        self.tokens.append(Token(TokenType.CHAR, char, start_line, start_col))
    
    def read_identifier(self):
        start_line = self.line
        start_col = self.column
        identifier = ""
        
        while self.position < len(self.code):
            char = self.current_char()
            if char.isalnum() or char == '_':
                identifier += char
                self.advance()
            else:
                break
        
        if identifier in KEYWORDS:
            token_type = TokenType.KEYWORD
            value = KEYWORDS[identifier]
        else:
            token_type = TokenType.IDENTIFIER
            value = identifier
        
        self.tokens.append(Token(token_type, value, start_line, start_col))
    
    def read_symbol(self):
        start_line = self.line
        start_col = self.column
        char = self.current_char()
        
        # Double symbols
        if char == '=' and self.peek() == '=':
            self.advance()
            self.advance()
            self.tokens.append(Token(TokenType.EQUAL_EQUAL, "==", start_line, start_col))
            return
        
        if char == '!' and self.peek() == '=':
            self.advance()
            self.advance()
            self.tokens.append(Token(TokenType.NOT_EQUAL, "!=", start_line, start_col))
            return
        
        if char == '>' and self.peek() == '=':
            self.advance()
            self.advance()
            self.tokens.append(Token(TokenType.GREATER_EQUAL, ">=", start_line, start_col))
            return
        
        if char == '<' and self.peek() == '=':
            self.advance()
            self.advance()
            self.tokens.append(Token(TokenType.LESS_EQUAL, "<=", start_line, start_col))
            return
        
        # Compound assignments
        if char == '+' and self.peek() == '=':
            self.advance()
            self.advance()
            self.tokens.append(Token(TokenType.PLUS_EQUALS, "+=", start_line, start_col))
            return
        
        if char == '-' and self.peek() == '=':
            self.advance()
            self.advance()
            self.tokens.append(Token(TokenType.MINUS_EQUALS, "-=", start_line, start_col))
            return
        
        if char == '*' and self.peek() == '=':
            self.advance()
            self.advance()
            self.tokens.append(Token(TokenType.STAR_EQUALS, "*=", start_line, start_col))
            return
        
        if char == '/' and self.peek() == '=':
            self.advance()
            self.advance()
            self.tokens.append(Token(TokenType.SLASH_EQUALS, "/=", start_line, start_col))
            return
        
        # Single symbols
        symbols = {
            '=': TokenType.EQUALS,
            '+': TokenType.PLUS,
            '-': TokenType.MINUS,
            '*': TokenType.STAR,
            '/': TokenType.SLASH,
            '!': TokenType.NOT,
            '%': TokenType.MOD,
            '(': TokenType.LPAREN,
            ')': TokenType.RPAREN,
            '{': TokenType.LBRACE,
            '}': TokenType.RBRACE,
            '[': TokenType.LBRACKET,
            ']': TokenType.RBRACKET,
            ';': TokenType.SEMICOLON,
            ':': TokenType.COLON,
            ',': TokenType.COMMA,
            '.': TokenType.DOT,
            '>': TokenType.GREATER,
            '<': TokenType.LESS,
        }
        
        if char in symbols:
            self.tokens.append(Token(symbols[char], char, start_line, start_col))
            self.advance()
        else:
            self.tokens.append(Token(TokenType.UNKNOWN, char, start_line, start_col))
            self.advance()
    
    def peek(self):
        if self.position + 1 < len(self.code):
            return self.code[self.position + 1]
        return '\0'