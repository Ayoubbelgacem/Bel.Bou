# src/parser/parser.py
from src.lexer.token import TokenType
from src.parser.ast import *

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0
    
    def current_token(self):
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return None
    
    def peek_token(self):
        if self.position + 1 < len(self.tokens):
            return self.tokens[self.position + 1]
        return None
    
    def match(self, token_type, offset=0):
        pos = self.position + offset
        return pos < len(self.tokens) and self.tokens[pos].type == token_type
    
    def advance(self):
        self.position += 1
    
    def expect(self, token_type):
        token = self.current_token()
        if token and token.type == token_type:
            self.advance()
            return token
        raise Exception(f"Expected {token_type}, got {token.type if token else 'EOF'}")
    
    def parse(self):
        statements = []
        while self.current_token() and self.current_token().type != TokenType.EOF:
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        return ProgramNode(statements)
    
    def parse_statement(self):
        token = self.current_token()
        
        if not token:
            return None
        
        if token.type == TokenType.EOF:
            self.advance()
            return None
        
        # ===== SKIP LES TOKENS VIDES =====
        while self.current_token() and self.current_token().type == TokenType.SEMICOLON:
            self.advance()
            token = self.current_token()
            if not token:
                return None
        
        # ===== PROTECTION CONTRE LES TOKENS INVALIDES =====
        if self.current_token() and self.current_token().type == TokenType.RBRACE:
            return None
        
        token = self.current_token()
        
        # ===== DETECTER LES CAS SPÉCIAUX =====
        
        # 1. LOOP pattern: i men ... (identifier + FOR keyword)
        if token.type == TokenType.IDENTIFIER and self.peek_token() and self.peek_token().type == TokenType.KEYWORD and self.peek_token().value == "FOR":
            return self.parse_for()
        
        # ===== KEYWORDS =====
        if token.type == TokenType.KEYWORD:
            if token.value == "VARIABLE":
                return self.parse_variable()
            elif token.value == "PRINT":
                return self.parse_print()
            elif token.value == "INPUT":
                return self.parse_input()
            elif token.value == "IF":
                return self.parse_if()
            elif token.value == "ELSE_IF":
                raise Exception("ELSE_IF (sinon_ken) must appear after an IF or ELSE block")
            elif token.value == "FOR":
                return self.parse_for()
            elif token.value == "WHILE":
                return self.parse_while()
            elif token.value == "FUNCTION":
                return self.parse_function()
            elif token.value == "RETURN":
                return self.parse_return()
            elif token.value == "CLASS":
                return self.parse_class()
            elif token.value == "NEW":
                return self.parse_new()
            elif token.value == "TRY":
                return self.parse_try()
            elif token.value == "IMPORT":
                return self.parse_import()
            elif token.value == "BREAK" or token.value == "CONTINUE":
                self.advance()
                self.expect(TokenType.SEMICOLON)
                return None
            elif token.value == "THIS":
                return self.parse_this_expression()
            elif token.value == "SUPER":
                return self.parse_super_expression()
        
        # Check for file I/O functions (identifiers)
        if token.type == TokenType.IDENTIFIER:
            if token.value == "ikteb_fi_mlf":
                return self.parse_file_write()
            elif token.value == "iqra_mlf":
                return self.parse_file_read()
        
        # ===== IDENTIFIER HANDLING =====
        if token.type == TokenType.IDENTIFIER:
            # Assignment simple: obj = value
            if self.peek_token() and self.peek_token().type == TokenType.EQUALS:
                node = self.parse_assignment()
                return node
            
            # Expression statement: obj.method(), obj.prop, obj[0], etc.
            node = self.safe_parse_expression()
            
            # Consommer le ';' s'il est présent
            if self.current_token() and self.current_token().type == TokenType.SEMICOLON:
                self.advance()
            
            return node
        
        # ===== EXPRESSION STATEMENT FALLBACK =====
        if token.type not in [TokenType.KEYWORD, TokenType.IDENTIFIER, TokenType.SEMICOLON, TokenType.RBRACE]:
            node = self.safe_parse_expression()
            
            # Consommer le ';' s'il est présent
            if self.current_token() and self.current_token().type == TokenType.SEMICOLON:
                self.advance()
            
            return node
        
        raise Exception(f"Unknown statement at token {token} (line {token.line}, col {token.column})")
    
    # ===== EXPRESSION PARSING =====
    
    def safe_parse_expression(self):
        """Parse une expression et lève une erreur si elle est None"""
        expr = self.parse_expression()
        if expr is None:
            token = self.current_token()
            if token:
                raise Exception(f"Invalid expression at token {token} (line {token.line}, col {token.column})")
            else:
                raise Exception("Invalid expression: unexpected EOF")
        return expr
    
    def parse_expression(self):
        """Parse une expression avec opérateurs binaires et postfix"""
        # Protection: ne pas parser sur un ';'
        if self.current_token() and self.current_token().type == TokenType.SEMICOLON:
            return None
        
        left = self.parse_or()
        if left is None:
            return None
        
        while self.current_token() and self.current_token().type in [TokenType.PLUS, TokenType.MINUS]:
            op = self.current_token().type
            self.advance()
            right = self.parse_or()
            if right is None:
                raise Exception("Invalid expression: missing right operand")
            left = BinOpNode(left, op, right)
        
        return left
    
    def parse_or(self):
        left = self.parse_and()
        if left is None:
            return None
        
        while self.current_token() and self.current_token().type == TokenType.OR:
            op = self.current_token().type
            self.advance()
            right = self.parse_and()
            if right is None:
                raise Exception("Invalid expression: missing right operand for OR")
            left = BinOpNode(left, op, right)
        
        return left
    
    def parse_and(self):
        left = self.parse_comparison()
        if left is None:
            return None
        
        while self.current_token() and self.current_token().type == TokenType.AND:
            op = self.current_token().type
            self.advance()
            right = self.parse_comparison()
            if right is None:
                raise Exception("Invalid expression: missing right operand for AND")
            left = BinOpNode(left, op, right)
        
        return left
    
    def parse_comparison(self):
        left = self.parse_term()
        if left is None:
            return None
        
        while self.current_token() and self.current_token().type in [TokenType.GREATER, TokenType.LESS, TokenType.GREATER_EQUAL, TokenType.LESS_EQUAL, TokenType.EQUAL_EQUAL, TokenType.NOT_EQUAL]:
            op = self.current_token().type
            self.advance()
            right = self.parse_term()
            if right is None:
                raise Exception("Invalid expression: missing right operand for comparison")
            left = BinOpNode(left, op, right)
        
        return left
    
    def parse_term(self):
        left = self.parse_unary()
        if left is None:
            return None
        
        while self.current_token() and self.current_token().type in [TokenType.STAR, TokenType.SLASH, TokenType.MOD]:
            op = self.current_token().type
            self.advance()
            right = self.parse_unary()
            if right is None:
                raise Exception("Invalid expression: missing right operand")
            left = BinOpNode(left, op, right)
        
        return left
    
    def parse_unary(self):
        token = self.current_token()
        if token and token.type == TokenType.MINUS:
          op = token.type
          self.advance()
          right = self.parse_unary()
          if right is None:
              raise Exception("Invalid expression: missing operand for unary minus")
          return UnaryOpNode(op, right)
        return self.parse_postfix()
    
    def parse_postfix(self):
        """Parse une expression primaire avec chaînage postfix (.field, [index], (args))"""
        node = self.parse_primary()
        
        while True:
            token = self.current_token()
            
            # obj.field or obj.field = value
            if token and token.type == TokenType.DOT:
                self.advance()
                name = self.expect(TokenType.IDENTIFIER).value
                
                # Vérifier si c'est une assignation de propriété
                if self.current_token() and self.current_token().type == TokenType.EQUALS:
                    self.advance()
                    value = self.safe_parse_expression()
                    node = PropertyNode(name, value, is_assignment=True)
                else:
                    node = PropertyNode(name, node, is_assignment=False)
                continue
            
            # obj[expr] or obj[expr] = value
            elif token and token.type == TokenType.LBRACKET:
                self.advance()
                index = self.safe_parse_expression()
                self.expect(TokenType.RBRACKET)
                
                # Vérifier si c'est une assignation de tableau
                if self.current_token() and self.current_token().type == TokenType.EQUALS:
                    self.advance()
                    value = self.safe_parse_expression()
                    node = ArrayAccessNode(node, index, value, is_assignment=True)
                else:
                    node = ArrayAccessNode(node, index, None, is_assignment=False)
                continue
            
            # obj(args) - appel de fonction/méthode
            elif token and token.type == TokenType.LPAREN:
                self.advance()
                args = []
                if self.current_token() and self.current_token().type != TokenType.RPAREN:
                    while self.current_token() and self.current_token().type != TokenType.RPAREN:
                        args.append(self.safe_parse_expression())
                        if self.current_token() and self.current_token().type == TokenType.COMMA:
                            self.advance()
                self.expect(TokenType.RPAREN)
                node = CallNode(node, args)
                continue
            
            else:
                break
        
        return node
    
    def parse_primary(self):
        """Parse une expression primaire (nombre, string, identifiant, parenthèses)"""
        token = self.current_token()
        
        if token.type == TokenType.NUMBER:
            self.advance()
            return NumberNode(token.value)
        elif token.type == TokenType.REAL:
            self.advance()
            return NumberNode(token.value)
        elif token.type == TokenType.STRING:
            self.advance()
            # Gérer les chaînes vides
            if token.value is None:
                return StringNode("")
            return StringNode(token.value)
        elif token.type == TokenType.CHAR:
            self.advance()
            if token.value is None:
                return StringNode("")
            return StringNode(token.value)
        elif token.type == TokenType.LBRACKET:
            self.advance()
            elements = []
            while self.current_token() and self.current_token().type != TokenType.RBRACKET:
                if self.current_token() is None:
                    raise Exception("Unexpected EOF in array literal")
                if self.current_token().type == TokenType.COMMA:
                    self.advance()
                    continue
                elements.append(self.safe_parse_expression())
            self.expect(TokenType.RBRACKET)
            return ArrayLiteralNode(elements)
        elif token.type == TokenType.IDENTIFIER:
            if token.value == "s7i7":
                self.advance()
                return BooleanNode(True)
            elif token.value == "ghalet":
                self.advance()
                return BooleanNode(False)
            elif token.value == "null":
                self.advance()
                return NullNode()
            
            self.advance()
            return IdentifierNode(token.value)
        elif token.type == TokenType.KEYWORD:
            if token.value == "TRUE":
                self.advance()
                return BooleanNode(True)
            elif token.value == "FALSE":
                self.advance()
                return BooleanNode(False)
            elif token.value == "NEW":
                return self.parse_new_expression()
            elif token.value == "THIS":
                return self.parse_this_expression()
            elif token.value == "SUPER":
                return self.parse_super_expression()
            else:
                raise Exception(f"Unexpected keyword in expression: {token} (line {token.line}, col {token.column})")
        elif token.type == TokenType.LPAREN:
            self.advance()
            expr = self.safe_parse_expression()
            self.expect(TokenType.RPAREN)
            return expr
        else:
            raise Exception(f"Unexpected token in expression: {token} (line {token.line}, col {token.column})")
    
    def parse_this_expression(self):
        """Parse hetha.prop comme expression"""
        self.advance()  # THIS
        self.expect(TokenType.DOT)
        prop_name = self.expect(TokenType.IDENTIFIER).value
        
        # Vérifier si c'est une assignation
        if self.current_token() and self.current_token().type == TokenType.EQUALS:
            self.advance()
            value = self.safe_parse_expression()
            self.expect(TokenType.SEMICOLON)
            return PropertyNode(prop_name, value, is_assignment=True)
        
        return PropertyNode(prop_name, None, is_assignment=False)
    
    def parse_super_expression(self):
        """Parse super(args) comme expression"""
        self.advance()  # SUPER
        self.expect(TokenType.LPAREN)
        args = []
        if self.current_token() and self.current_token().type != TokenType.RPAREN:
            while self.current_token() and self.current_token().type != TokenType.RPAREN:
                args.append(self.safe_parse_expression())
                if self.current_token() and self.current_token().type == TokenType.COMMA:
                    self.advance()
        self.expect(TokenType.RPAREN)
        return SuperNode(args)
    
    def parse_new_expression(self):
        """Parse new ClassName(args) comme expression"""
        self.advance()  # NEW
        class_name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.LPAREN)
        args = []
        if self.current_token() and self.current_token().type != TokenType.RPAREN:
            while self.current_token() and self.current_token().type != TokenType.RPAREN:
                args.append(self.safe_parse_expression())
                if self.current_token() and self.current_token().type == TokenType.COMMA:
                    self.advance()
        self.expect(TokenType.RPAREN)
        return NewNode(class_name, args)
    
    def parse_variable(self):
        self.advance()
        name = self.expect(TokenType.IDENTIFIER).value
        
        type_name = None
        
        if self.current_token() and self.current_token().type == TokenType.COLON:
            self.advance()
            type_name = self.expect(TokenType.IDENTIFIER).value
        
        self.expect(TokenType.EQUALS)
        
        if self.current_token() and self.current_token().type == TokenType.LBRACKET:
            self.advance()
            elements = []
            while self.current_token() and self.current_token().type != TokenType.RBRACKET:
                if self.current_token() is None:
                    raise Exception("Unexpected EOF in array literal")
                if self.current_token().type == TokenType.COMMA:
                    self.advance()
                    continue
                elements.append(self.safe_parse_expression())
            self.expect(TokenType.RBRACKET)
            value = ArrayLiteralNode(elements)
        else:
            value = self.safe_parse_expression()
        
        self.expect(TokenType.SEMICOLON)
        return VariableNode(name, type_name, value)
    
    def parse_assignment(self):
        name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.EQUALS)
        value = self.safe_parse_expression()
        self.expect(TokenType.SEMICOLON)
        return AssignmentNode(name, value)
    
    def parse_array_access_statement(self, name):
        self.advance()
        self.expect(TokenType.LBRACKET)
        index = self.safe_parse_expression()
        self.expect(TokenType.RBRACKET)
        
        if self.current_token() and self.current_token().type == TokenType.EQUALS:
            self.advance()
            value = self.safe_parse_expression()
            self.expect(TokenType.SEMICOLON)
            return ArrayAccessNode(name, index, value, is_assignment=True)
        else:
            self.expect(TokenType.SEMICOLON)
            return ArrayAccessNode(name, index, None, is_assignment=False)
    
    def parse_print(self):
        self.advance()
        self.expect(TokenType.LPAREN)
        value = self.safe_parse_expression()
        self.expect(TokenType.RPAREN)
        self.expect(TokenType.SEMICOLON)
        return PrintNode(value)
    
    def parse_input(self):
        self.advance()
        self.expect(TokenType.LPAREN)
        prompt = self.safe_parse_expression()
        self.expect(TokenType.RPAREN)
        self.expect(TokenType.SEMICOLON)
        return InputNode(prompt)
    
    def parse_file_write(self):
        self.advance()
        self.expect(TokenType.LPAREN)
        filename = self.safe_parse_expression()
        self.expect(TokenType.COMMA)
        content = self.safe_parse_expression()
        self.expect(TokenType.RPAREN)
        self.expect(TokenType.SEMICOLON)
        return FileWriteNode(filename, content)
    
    def parse_file_read(self):
        self.advance()
        self.expect(TokenType.LPAREN)
        filename = self.safe_parse_expression()
        self.expect(TokenType.RPAREN)
        self.expect(TokenType.SEMICOLON)
        return FileReadNode(filename)
    
    def parse_if(self):
        self.advance()
        
        condition = self.safe_parse_expression()
        
        # Skip DO / a3mel
        if self.current_token() and self.current_token().type == TokenType.KEYWORD:
            if self.current_token().value == "DO":
                self.advance()
        
        self.expect(TokenType.LBRACE)
        
        then_body = []
        while self.current_token() and self.current_token().type != TokenType.RBRACE:
            stmt = self.parse_statement()
            if stmt:
                then_body.append(stmt)
        
        self.expect(TokenType.RBRACE)
        
        # ===== ELSE / ELSE_IF CHAIN =====
        else_body = None
        
        while self.current_token() and self.current_token().type == TokenType.KEYWORD:
            # ELSE_IF (sinon_ken)
            if self.current_token().value == "ELSE_IF":
                self.advance()
                elif_condition = self.safe_parse_expression()
                
                # Skip DO / a3mel
                if self.current_token() and self.current_token().type == TokenType.KEYWORD:
                    if self.current_token().value == "DO":
                        self.advance()
                
                self.expect(TokenType.LBRACE)
                
                elif_body = []
                while self.current_token() and self.current_token().type != TokenType.RBRACE:
                    stmt = self.parse_statement()
                    if stmt:
                        elif_body.append(stmt)
                
                self.expect(TokenType.RBRACE)
                
                # Convertir en nested IF
                elif_node = IfNode(elif_condition, elif_body, None)
                
                if else_body is None:
                    else_body = [elif_node]
                else:
                    if isinstance(else_body, list):
                        else_body = [IfNode(elif_condition, elif_body, else_body)]
                    else:
                        else_body = [IfNode(elif_condition, elif_body, else_body)]
            
            # ELSE final
            elif self.current_token().value == "ELSE":
                self.advance()
                self.expect(TokenType.LBRACE)
                
                else_body = []
                while self.current_token() and self.current_token().type != TokenType.RBRACE:
                    stmt = self.parse_statement()
                    if stmt:
                        else_body.append(stmt)
                
                self.expect(TokenType.RBRACE)
                break
            
            else:
                break
        
        # Skip les ';' parasites après un bloc if
        while self.current_token() and self.current_token().type == TokenType.SEMICOLON:
            self.advance()
        
        return IfNode(condition, then_body, else_body)
    
    def parse_for(self):
        # Check if we have identifier + FOR pattern (i men ...)
        if self.current_token() and self.current_token().type == TokenType.IDENTIFIER:
            iterator = self.current_token().value
            self.advance()
            # Skip FOR keyword
            if self.current_token() and self.current_token().type == TokenType.KEYWORD and self.current_token().value == "FOR":
                self.advance()
        else:
            self.advance()
            iterator = self.expect(TokenType.IDENTIFIER).value
        
        start = self.safe_parse_expression()
        
        # '7ata' (TO)
        if self.current_token() and self.current_token().type == TokenType.KEYWORD:
            if self.current_token().value == "7ata":
                self.advance()
            else:
                self.advance()
        else:
            self.expect(TokenType.KEYWORD)
        
        end = self.safe_parse_expression()
        
        # 'a3mel' (DO)
        if self.current_token() and self.current_token().type == TokenType.KEYWORD:
            if self.current_token().value == "DO" or self.current_token().value == "a3mel":
                self.advance()
            else:
                self.advance()
        else:
            self.expect(TokenType.KEYWORD)
        
        self.expect(TokenType.LBRACE)
        body = []
        while self.current_token() and self.current_token().type != TokenType.RBRACE:
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
        self.expect(TokenType.RBRACE)
        
        # Skip les ';' parasites après une boucle for
        while self.current_token() and self.current_token().type == TokenType.SEMICOLON:
            self.advance()
        
        return ForNode(iterator, start, end, body)
    
    def parse_while(self):
        self.advance()
        condition = self.safe_parse_expression()
        
        if self.current_token() and self.current_token().type == TokenType.KEYWORD:
            if self.current_token().value == "DO":
                self.advance()
            else:
                self.advance()
        else:
            self.expect(TokenType.KEYWORD)
        
        self.expect(TokenType.LBRACE)
        body = []
        while self.current_token() and self.current_token().type != TokenType.RBRACE:
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
        self.expect(TokenType.RBRACE)
        
        # Skip les ';' parasites après une boucle while
        while self.current_token() and self.current_token().type == TokenType.SEMICOLON:
            self.advance()
        
        return WhileNode(condition, body)
    
    def parse_function(self):
        self.advance()
        name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.LPAREN)
        
        params = []
        if self.current_token() and self.current_token().type != TokenType.RPAREN:
            while self.current_token() and self.current_token().type != TokenType.RPAREN:
                param = self.expect(TokenType.IDENTIFIER).value
                params.append(param)
                if self.current_token() and self.current_token().type == TokenType.COMMA:
                    self.advance()
        
        self.expect(TokenType.RPAREN)
        self.expect(TokenType.LBRACE)
        
        body = []
        while self.current_token() and self.current_token().type != TokenType.RBRACE:
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
        self.expect(TokenType.RBRACE)
        
        return FunctionNode(name, params, body)
    
    def parse_return(self):
        if self.current_token() and self.current_token().type == TokenType.KEYWORD and self.current_token().value == "RETURN":
            self.advance()
        else:
            if self.current_token() and self.current_token().type == TokenType.IDENTIFIER and self.current_token().value == "rejje":
                self.advance()
            else:
                self.advance()
        
        value = self.safe_parse_expression()
        self.expect(TokenType.SEMICOLON)
        return ReturnNode(value)
    
    def parse_class(self):
        self.advance()
        name = self.expect(TokenType.IDENTIFIER).value
        
        parent = None
        if self.current_token() and self.current_token().type == TokenType.KEYWORD and self.current_token().value == "INHERITS":
            self.advance()
            parent = self.expect(TokenType.IDENTIFIER).value
        
        self.expect(TokenType.LBRACE)
        
        properties = []
        methods = []
        
        while self.current_token() and self.current_token().type != TokenType.RBRACE:
            token = self.current_token()
            
            is_method = False
            
            if token.type == TokenType.KEYWORD and token.value == "FUNCTION":
                is_method = True
            elif token.type == TokenType.KEYWORD and token.value == "NEW":
                if self.peek_token() and self.peek_token().type == TokenType.LPAREN:
                    is_method = True
            elif token.type == TokenType.IDENTIFIER:
                if self.peek_token() and self.peek_token().type == TokenType.LPAREN:
                    is_method = True
            
            if is_method:
                method_node = self.parse_method()
                methods.append(method_node)
            else:
                stmt = self.parse_statement()
                if stmt:
                    if isinstance(stmt, AssignmentNode):
                        properties.append(PropertyNode(stmt.name, stmt.value))
                    elif isinstance(stmt, PropertyNode):
                        properties.append(stmt)
                    else:
                        methods.append(stmt)
        
        self.expect(TokenType.RBRACE)
        return ClassNode(name, parent, methods, properties)
    
    def parse_method(self):
        if self.current_token() and self.current_token().type == TokenType.KEYWORD and self.current_token().value == "FUNCTION":
            self.advance()
            name = self.expect(TokenType.IDENTIFIER).value
        elif self.current_token() and self.current_token().type == TokenType.KEYWORD and self.current_token().value == "NEW":
            self.advance()
            name = "jdid"
        else:
            name = self.expect(TokenType.IDENTIFIER).value
        
        self.expect(TokenType.LPAREN)
        params = []
        if self.current_token() and self.current_token().type != TokenType.RPAREN:
            while self.current_token() and self.current_token().type != TokenType.RPAREN:
                param = self.expect(TokenType.IDENTIFIER).value
                params.append(param)
                if self.current_token() and self.current_token().type == TokenType.COMMA:
                    self.advance()
        self.expect(TokenType.RPAREN)
        
        self.expect(TokenType.LBRACE)
        body = []
        while self.current_token() and self.current_token().type != TokenType.RBRACE:
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
        self.expect(TokenType.RBRACE)
        
        return MethodNode(name, params, body)
    
    def parse_property_assignment(self):
        self.advance()
        self.expect(TokenType.DOT)
        prop_name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.EQUALS)
        value = self.safe_parse_expression()
        self.expect(TokenType.SEMICOLON)
        return PropertyNode(prop_name, value, is_assignment=True)
    
    def parse_method_call_statement(self, object_name):
        self.advance()
        self.expect(TokenType.DOT)
        method_name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.LPAREN)
        args = []
        if self.current_token() and self.current_token().type != TokenType.RPAREN:
            while self.current_token() and self.current_token().type != TokenType.RPAREN:
                args.append(self.safe_parse_expression())
                if self.current_token() and self.current_token().type == TokenType.COMMA:
                    self.advance()
        self.expect(TokenType.RPAREN)
        self.expect(TokenType.SEMICOLON)
        return MethodCallNode(object_name, method_name, args)
    
    def parse_new(self):
        self.advance()
        class_name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.LPAREN)
        
        args = []
        if self.current_token() and self.current_token().type != TokenType.RPAREN:
            while self.current_token() and self.current_token().type != TokenType.RPAREN:
                args.append(self.safe_parse_expression())
                if self.current_token() and self.current_token().type == TokenType.COMMA:
                    self.advance()
        
        self.expect(TokenType.RPAREN)
        self.expect(TokenType.SEMICOLON)
        return NewNode(class_name, args)
    
    def parse_try(self):
        self.advance()
        self.expect(TokenType.LBRACE)
        
        try_body = []
        while self.current_token() and self.current_token().type != TokenType.RBRACE:
            stmt = self.parse_statement()
            if stmt:
                try_body.append(stmt)
        self.expect(TokenType.RBRACE)
        
        catch_var = None
        catch_body = []
        
        if self.current_token() and self.current_token().type == TokenType.KEYWORD and self.current_token().value == "CATCH":
            self.advance()
            self.expect(TokenType.LPAREN)
            catch_var = self.expect(TokenType.IDENTIFIER).value
            self.expect(TokenType.RPAREN)
            self.expect(TokenType.LBRACE)
            
            while self.current_token() and self.current_token().type != TokenType.RBRACE:
                stmt = self.parse_statement()
                if stmt:
                    catch_body.append(stmt)
            self.expect(TokenType.RBRACE)
        
        finally_body = []
        if self.current_token() and self.current_token().type == TokenType.KEYWORD and self.current_token().value == "FINALLY":
            self.advance()
            self.expect(TokenType.LBRACE)
            
            while self.current_token() and self.current_token().type != TokenType.RBRACE:
                stmt = self.parse_statement()
                if stmt:
                    finally_body.append(stmt)
            self.expect(TokenType.RBRACE)
        
        return TryNode(try_body, catch_var, catch_body, finally_body)
    
    def parse_import(self):
        self.advance()
        module = self.expect(TokenType.STRING).value
        self.expect(TokenType.SEMICOLON)
        return ImportNode(module)