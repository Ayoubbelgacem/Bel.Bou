from src.lexer.token import TokenType
from src.parser.ast import *
from src.utils.errors import BouBelError

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
        raise BouBelError(
            f"Expected {token_type}, got {token.type if token else 'EOF'}",
            token.line if token else None,
            token.column if token else None
        )
    
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
        
        # Skip empty semicolons
        while self.current_token() and self.current_token().type == TokenType.SEMICOLON:
            self.advance()
            token = self.current_token()
            if not token:
                return None
        
        # Protection against invalid tokens
        if self.current_token() and self.current_token().type == TokenType.RBRACE:
            return None
        
        token = self.current_token()
        
        # Keywords
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
                raise BouBelError(
                    "ELSE_IF (sinon_ken) must appear after an IF or ELSE block",
                    token.line, token.column
                )
            elif token.value == "FOR":
                return self.parse_for_keyword_first()
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
            elif token.value == "BREAK":
                self.advance()
                self.expect(TokenType.SEMICOLON)
                return BreakNode()
            elif token.value == "CONTINUE":
                self.advance()
                self.expect(TokenType.SEMICOLON)
                return ContinueNode()
            elif token.value == "TRUE":
                self.advance()
                return BooleanNode(True)
            elif token.value == "FALSE":
                self.advance()
                return BooleanNode(False)
            elif token.value == "NULL":
                self.advance()
                return NullNode()
            elif token.value == "THIS":
                node = self.parse_this_expression()
                if self.current_token() and self.current_token().type == TokenType.SEMICOLON:
                    self.advance()
                return node
            elif token.value == "SUPER":
                node = self.parse_super_expression()
                if self.current_token() and self.current_token().type == TokenType.SEMICOLON:
                    self.advance()
                return node
        
        # File I/O functions - priorité
        if token.type == TokenType.IDENTIFIER:
            if token.value == "ikteb_fi_mlf":
                return self.parse_file_write()
            elif token.value == "iqra_mlf":
                return self.parse_file_read()
        
        # Identifier handling
        if token.type == TokenType.IDENTIFIER:
            # Détection de la boucle FOR avec identifiant en premier
            if (self.peek_token() and 
                self.peek_token().type == TokenType.KEYWORD and 
                self.peek_token().value == "FOR"):
                return self.parse_for_identifier_first()
            
            # Assignment
            if self.peek_token() and self.peek_token().type == TokenType.EQUALS:
                return self.parse_assignment()
            
            # Compound assignment
            if self.peek_token() and self.peek_token().type in [
                TokenType.PLUS_EQUALS, TokenType.MINUS_EQUALS,
                TokenType.STAR_EQUALS, TokenType.SLASH_EQUALS
            ]:
                return self.parse_compound_assignment()
            
            # Expression statement
            node = self.safe_parse_expression()
            
            if self.current_token() and self.current_token().type == TokenType.SEMICOLON:
                self.advance()
            
            return node
        
        # Expression statement fallback
        if token.type not in [TokenType.KEYWORD, TokenType.IDENTIFIER, 
                              TokenType.SEMICOLON, TokenType.RBRACE]:
            node = self.safe_parse_expression()
            
            if self.current_token() and self.current_token().type == TokenType.SEMICOLON:
                self.advance()
            
            return node
        
        raise BouBelError(
            f"Unknown statement at token {token}",
            token.line, token.column
        )
    
    def safe_parse_expression(self):
        expr = self.parse_expression()
        if expr is None:
            token = self.current_token()
            if token:
                raise BouBelError(
                    f"Invalid expression at token {token}",
                    token.line, token.column
                )
            else:
                raise BouBelError("Invalid expression: unexpected EOF")
        return expr
    
    def parse_expression(self):
        if self.current_token() and self.current_token().type == TokenType.SEMICOLON:
            return None
        
        left = self.parse_or()
        if left is None:
            return None
        
        while self.current_token() and self.current_token().type in [
            TokenType.PLUS, TokenType.MINUS
        ]:
            op = self.current_token().type
            self.advance()
            right = self.parse_or()
            if right is None:
                raise BouBelError("Invalid expression: missing right operand")
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
                raise BouBelError("Invalid expression: missing right operand for OR")
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
                raise BouBelError("Invalid expression: missing right operand for AND")
            left = BinOpNode(left, op, right)
        
        return left
    
    def parse_comparison(self):
        left = self.parse_term()
        if left is None:
            return None
        
        while self.current_token() and self.current_token().type in [
            TokenType.GREATER, TokenType.LESS, 
            TokenType.GREATER_EQUAL, TokenType.LESS_EQUAL,
            TokenType.EQUAL_EQUAL, TokenType.NOT_EQUAL
        ]:
            op = self.current_token().type
            self.advance()
            right = self.parse_term()
            if right is None:
                raise BouBelError("Invalid expression: missing right operand for comparison")
            left = BinOpNode(left, op, right)
        
        return left
    
    def parse_term(self):
        left = self.parse_unary()
        if left is None:
            return None
        
        while self.current_token() and self.current_token().type in [
            TokenType.STAR, TokenType.SLASH, TokenType.MOD
        ]:
            op = self.current_token().type
            self.advance()
            right = self.parse_unary()
            if right is None:
                raise BouBelError("Invalid expression: missing right operand")
            left = BinOpNode(left, op, right)
        
        return left
    
    def parse_unary(self):
        token = self.current_token()
        
        if token and token.type == TokenType.MINUS:
            op = token.type
            self.advance()
            right = self.parse_unary()
            if right is None:
                raise BouBelError("Invalid expression: missing operand for unary minus")
            return UnaryOpNode(op, right)
        
        if token and token.type == TokenType.NOT:
            op = token.type
            self.advance()
            right = self.parse_unary()
            if right is None:
                raise BouBelError("Invalid expression: missing operand for NOT")
            return UnaryOpNode(op, right)
        
        return self.parse_postfix()
    
    def parse_postfix(self):
        node = self.parse_primary()
        
        while True:
            token = self.current_token()
            
            if token and token.type == TokenType.DOT:
                self.advance()
                name = self.expect(TokenType.IDENTIFIER).value
                
                if self.current_token() and self.current_token().type == TokenType.EQUALS:
                    self.advance()
                    value = self.safe_parse_expression()
                    node = PropertyNode(name, value, is_assignment=True)
                else:
                    node = PropertyNode(name, node, is_assignment=False)
                continue
            
            elif token and token.type == TokenType.LBRACKET:
                self.advance()
                index = self.safe_parse_expression()
                self.expect(TokenType.RBRACKET)
                
                if self.current_token() and self.current_token().type == TokenType.EQUALS:
                    self.advance()
                    value = self.safe_parse_expression()
                    node = ArrayAccessNode(node, index, value, is_assignment=True)
                else:
                    node = ArrayAccessNode(node, index, None, is_assignment=False)
                continue
            
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
        token = self.current_token()
        
        if token.type == TokenType.NUMBER:
            self.advance()
            return NumberNode(token.value)
        elif token.type == TokenType.REAL:
            self.advance()
            return NumberNode(token.value)
        elif token.type == TokenType.STRING:
            self.advance()
            return StringNode(token.value if token.value is not None else "")
        elif token.type == TokenType.CHAR:
            self.advance()
            return StringNode(token.value if token.value is not None else "")
        elif token.type == TokenType.LBRACKET:
            self.advance()
            elements = []
            while self.current_token() and self.current_token().type != TokenType.RBRACKET:
                if self.current_token() is None:
                    raise BouBelError("Unexpected EOF in array literal")
                if self.current_token().type == TokenType.COMMA:
                    self.advance()
                    continue
                elements.append(self.safe_parse_expression())
            self.expect(TokenType.RBRACKET)
            return ArrayLiteralNode(elements)
        elif token.type == TokenType.IDENTIFIER:
            self.advance()
            return IdentifierNode(token.value)
        elif token.type == TokenType.KEYWORD:
            if token.value == "TRUE":
                self.advance()
                return BooleanNode(True)
            elif token.value == "FALSE":
                self.advance()
                return BooleanNode(False)
            elif token.value == "NULL":
                self.advance()
                return NullNode()
            elif token.value == "NEW":
                return self.parse_new_expression()
            elif token.value == "THIS":
                return self.parse_this_expression()
            elif token.value == "SUPER":
                return self.parse_super_expression()
            else:
                raise BouBelError(
                    f"Unexpected keyword in expression: {token}",
                    token.line, token.column
                )
        elif token.type == TokenType.LPAREN:
            self.advance()
            expr = self.safe_parse_expression()
            self.expect(TokenType.RPAREN)
            return expr
        else:
            raise BouBelError(
                f"Unexpected token in expression: {token}",
                token.line, token.column
            )
    
    def parse_compound_assignment(self):
        name = self.expect(TokenType.IDENTIFIER).value
        op = self.current_token().type
        self.advance()
        value = self.safe_parse_expression()
        self.expect(TokenType.SEMICOLON)
        
        return AssignmentNode(name, BinOpNode(
            IdentifierNode(name),
            op,
            value
        ))
    
    def parse_variable(self):
        self.advance()
        name = self.expect(TokenType.IDENTIFIER).value
        
        type_name = None
        
        if self.current_token() and self.current_token().type == TokenType.COLON:
            self.advance()
            type_name = self.expect(TokenType.IDENTIFIER).value
        
        self.expect(TokenType.EQUALS)
        
        value = None
        if self.current_token() and self.current_token().type == TokenType.LBRACKET:
            self.advance()
            elements = []
            while self.current_token() and self.current_token().type != TokenType.RBRACKET:
                if self.current_token() is None:
                    raise BouBelError("Unexpected EOF in array literal")
                if self.current_token().type == TokenType.COMMA:
                    self.advance()
                    continue
                elements.append(self.safe_parse_expression())
            self.expect(TokenType.RBRACKET)
            value = ArrayLiteralNode(elements)
        else:
            value = self.safe_parse_expression()
        
        self.expect(TokenType.SEMICOLON)
        
        if isinstance(value, NewNode):
            value.target = name
        
        return VariableNode(name, type_name, value)
    
    def parse_assignment(self):
        name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.EQUALS)
        value = self.safe_parse_expression()
        self.expect(TokenType.SEMICOLON)
        
        if isinstance(value, NewNode):
            value.target = name
        
        return AssignmentNode(name, value)
    
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
        
        while self.current_token() and self.current_token().type == TokenType.KEYWORD and self.current_token().value in ["ELSE_IF", "ELSE"]:
            if self.current_token().value == "ELSE_IF":
                self.advance()
                elif_condition = self.safe_parse_expression()
                
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
                
                elif_node = IfNode(elif_condition, elif_body, None)
                
                if else_body is None:
                    else_body = elif_node
                else:
                    last = else_body
                    while isinstance(last.else_body, IfNode):
                        last = last.else_body
                    last.else_body = elif_node
            
            elif self.current_token().value == "ELSE":
                self.advance()
                self.expect(TokenType.LBRACE)
                
                else_body_final = []
                while self.current_token() and self.current_token().type != TokenType.RBRACE:
                    stmt = self.parse_statement()
                    if stmt:
                        else_body_final.append(stmt)
                
                self.expect(TokenType.RBRACE)
                
                if else_body is None:
                    else_body = else_body_final
                else:
                    last = else_body
                    while isinstance(last.else_body, IfNode):
                        last = last.else_body
                    last.else_body = else_body_final
                break
        
        while self.current_token() and self.current_token().type == TokenType.SEMICOLON:
            self.advance()
        
        return IfNode(condition, then_body, else_body)
    
    def parse_for_keyword_first(self):
        self.expect(TokenType.KEYWORD)
        iterator = self.expect(TokenType.IDENTIFIER).value
        
        start = self.safe_parse_expression()
        
        self.expect(TokenType.KEYWORD)
        
        end = self.safe_parse_expression()
        
        self.expect(TokenType.KEYWORD)
        
        self.expect(TokenType.LBRACE)
        body = []
        while self.current_token() and self.current_token().type != TokenType.RBRACE:
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
        self.expect(TokenType.RBRACE)
        
        while self.current_token() and self.current_token().type == TokenType.SEMICOLON:
            self.advance()
        
        return ForNode(iterator, start, end, body)
    
    def parse_for_identifier_first(self):
        iterator = self.current_token().value
        self.advance()
        
        self.expect(TokenType.KEYWORD)
        
        start = self.safe_parse_expression()
        
        self.expect(TokenType.KEYWORD)
        
        end = self.safe_parse_expression()
        
        self.expect(TokenType.KEYWORD)
        
        self.expect(TokenType.LBRACE)
        body = []
        while self.current_token() and self.current_token().type != TokenType.RBRACE:
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
        self.expect(TokenType.RBRACE)
        
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
        
        properties = {}
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
                        properties[stmt.name] = stmt.value
                    elif isinstance(stmt, PropertyNode):
                        if hasattr(stmt, 'name') and stmt.name is not None:
                            properties[stmt.name] = stmt.value
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
    
    def parse_new_expression(self):
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
        return NewNode(class_name, args)
    
    def parse_this_expression(self):
        self.advance()
        self.expect(TokenType.DOT)
        prop_name = self.expect(TokenType.IDENTIFIER).value
        
        if self.current_token() and self.current_token().type == TokenType.LPAREN:
            self.advance()
            args = []
            if self.current_token() and self.current_token().type != TokenType.RPAREN:
                while self.current_token() and self.current_token().type != TokenType.RPAREN:
                    args.append(self.safe_parse_expression())
                    if self.current_token() and self.current_token().type == TokenType.COMMA:
                        self.advance()
            self.expect(TokenType.RPAREN)
            return MethodCallNode("hetha", prop_name, args)
        
        if self.current_token() and self.current_token().type == TokenType.EQUALS:
            self.advance()
            value = self.safe_parse_expression()
            return PropertyNode(prop_name, value, is_assignment=True)
        
        return PropertyNode(prop_name, None, is_assignment=False)
    
    def parse_super_expression(self):
        self.advance()
        self.expect(TokenType.LPAREN)
        args = []
        if self.current_token() and self.current_token().type != TokenType.RPAREN:
            while self.current_token() and self.current_token().type != TokenType.RPAREN:
                args.append(self.safe_parse_expression())
                if self.current_token() and self.current_token().type == TokenType.COMMA:
                    self.advance()
        self.expect(TokenType.RPAREN)
        return SuperNode(args)
    
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