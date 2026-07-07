# src/vm/compiler.py
from src.vm.bytecode import Bytecode, OpCode
from src.parser.ast import *

class Compiler:
    def __init__(self):
        self.bytecode = Bytecode()
        self.current_function = None
        self.loop_stack = []
        self.temp_var_count = 0
    
    def compile(self, node):
        """Compiler l'AST en bytecode"""
        self.visit(node)
        self.bytecode.add(OpCode.HALT)
        self.bytecode.patch_labels()
        return self.bytecode
    
    def visit(self, node):
        if node is None:
            return
        
        node_type = node.__class__.__name__
        visit_method = getattr(self, f'visit_{node_type}', None)
        if visit_method:
            return visit_method(node)
        else:
            raise Exception(f"Unsupported node type in compiler: {node_type}")
    
    def visit_ProgramNode(self, node):
        # D'abord compiler toutes les fonctions
        for stmt in node.statements:
            if isinstance(stmt, FunctionNode):
                self.visit(stmt)
        
        # Puis compiler le corps du programme
        for stmt in node.statements:
            if not isinstance(stmt, FunctionNode):
                self.visit(stmt)
    
    def visit_VariableNode(self, node):
        self.visit(node.value)
        self.bytecode.add(OpCode.STORE_VAR, node.name)
    
    def visit_AssignmentNode(self, node):
        self.visit(node.value)
        self.bytecode.add(OpCode.STORE_VAR, node.name)
    
    def visit_PrintNode(self, node):
        self.visit(node.value)
        self.bytecode.add(OpCode.PRINT)
    
    def visit_InputNode(self, node):
        if node.prompt:
            self.visit(node.prompt)
        else:
            self.bytecode.add(OpCode.PUSH, "")
        self.bytecode.add(OpCode.INPUT)
    
    def visit_IfNode(self, node):
        label_else = f"if_else_{len(self.bytecode.code)}"
        label_end = f"if_end_{len(self.bytecode.code)}"
        
        self.visit(node.condition)
        self.bytecode.add(OpCode.JUMP_IF_FALSE, label_else)
        
        for stmt in node.then_body:
            self.visit(stmt)
        self.bytecode.add(OpCode.JUMP, label_end)
        
        self.bytecode.add_label(label_else)
        if node.else_body:
            if isinstance(node.else_body, list):
                for stmt in node.else_body:
                    self.visit(stmt)
            elif isinstance(node.else_body, IfNode):
                self.visit(node.else_body)
        
        self.bytecode.add_label(label_end)
    
    def visit_ForNode(self, node):
        start_label = f"for_start_{len(self.bytecode.code)}"
        end_label = f"for_end_{len(self.bytecode.code)}"
        
        # Initialisation
        self.visit(node.start)
        self.bytecode.add(OpCode.STORE_VAR, node.iterator)
        
        self.bytecode.add_label(start_label)
        
        # Condition
        self.bytecode.add(OpCode.LOAD_VAR, node.iterator)
        self.visit(node.end)
        self.bytecode.add(OpCode.LE)
        self.bytecode.add(OpCode.JUMP_IF_FALSE, end_label)
        
        # Corps
        for stmt in node.body:
            self.visit(stmt)
        
        # Incrémentation
        self.bytecode.add(OpCode.LOAD_VAR, node.iterator)
        self.bytecode.add(OpCode.PUSH, 1)
        self.bytecode.add(OpCode.ADD)
        self.bytecode.add(OpCode.STORE_VAR, node.iterator)
        self.bytecode.add(OpCode.JUMP, start_label)
        
        self.bytecode.add_label(end_label)
    
    def visit_WhileNode(self, node):
        start_label = f"while_start_{len(self.bytecode.code)}"
        end_label = f"while_end_{len(self.bytecode.code)}"
        
        self.bytecode.add_label(start_label)
        
        self.visit(node.condition)
        self.bytecode.add(OpCode.JUMP_IF_FALSE, end_label)
        
        for stmt in node.body:
            self.visit(stmt)
        
        self.bytecode.add(OpCode.JUMP, start_label)
        self.bytecode.add_label(end_label)
    
    def visit_FunctionNode(self, node):
        self.bytecode.add_label(node.name)
        start = len(self.bytecode.code)
        self.bytecode.functions[node.name] = {
            'params': node.params,
            'start': start
        }
        
        # Compiler le corps de la fonction
        for stmt in node.body:
            self.visit(stmt)
        
        # Return None par défaut
        self.bytecode.add(OpCode.PUSH, None)
        self.bytecode.add(OpCode.RETURN)
    
    def visit_ReturnNode(self, node):
        self.visit(node.value)
        self.bytecode.add(OpCode.RETURN)
    
    def visit_CallNode(self, node):
        # Vérifier si c'est un appel avec un nom de fonction
        if isinstance(node.name, str):
            # Évaluer les arguments
            for arg in node.args:
                self.visit(arg)
            # Appeler la fonction par son nom
            self.bytecode.add(OpCode.CALL, node.name)
        else:
            # C'est un appel sur un objet ou une expression
            # Évaluer l'objet
            self.visit(node.name)
            # Évaluer les arguments
            for arg in node.args:
                self.visit(arg)
            # Appeler (le nom est sur la stack)
            self.bytecode.add(OpCode.CALL)
    
    def visit_ClassNode(self, node):
        methods = {}
        for method in node.methods:
            methods[method.name] = {
                'params': method.params,
                'body': method.body
            }
        self.bytecode.classes[node.name] = {
            'parent': node.parent,
            'methods': methods,
            'properties': node.properties
        }
    
    def visit_NewNode(self, node):
        self.bytecode.add(OpCode.PUSH, node.class_name)
        for arg in node.args:
            self.visit(arg)
        self.bytecode.add(OpCode.NEW_OBJECT)
    
    def visit_MethodCallNode(self, node):
        # Évaluer l'objet
        if hasattr(node.object_name, 'name'):
            self.visit(node.object_name)
        else:
            self.bytecode.add(OpCode.LOAD_VAR, node.object_name)
        
        # Évaluer les arguments
        for arg in node.args:
            self.visit(arg)
        
        # Appeler la méthode
        self.bytecode.add(OpCode.CALL_METHOD, node.method_name)
    
    def visit_TryNode(self, node):
        # Implémentation simplifiée
        for stmt in node.try_body:
            self.visit(stmt)
    
    def visit_BinOpNode(self, node):
        self.visit(node.left)
        self.visit(node.right)
        
        op_map = {
            "PLUS": OpCode.ADD,
            "MINUS": OpCode.SUB,
            "STAR": OpCode.MUL,
            "SLASH": OpCode.DIV,
            "MOD": OpCode.MOD,
            "EQUAL_EQUAL": OpCode.EQ,
            "NOT_EQUAL": OpCode.NE,
            "GREATER": OpCode.GT,
            "LESS": OpCode.LT,
            "GREATER_EQUAL": OpCode.GE,
            "LESS_EQUAL": OpCode.LE,
            "AND": OpCode.AND,
            "OR": OpCode.OR,
        }
        
        op_value = node.op.value if hasattr(node.op, 'value') else str(node.op)
        if op_value in op_map:
            self.bytecode.add(op_map[op_value])
        else:
            raise Exception(f"Unsupported binary operator: {op_value}")
    
    def visit_UnaryOpNode(self, node):
        self.visit(node.expr)
        op_value = node.op.value if hasattr(node.op, 'value') else str(node.op)
        if op_value == "MINUS":
            self.bytecode.add(OpCode.PUSH, 0)
            self.bytecode.add(OpCode.SUB)
        elif op_value == "NOT":
            self.bytecode.add(OpCode.NOT)
        else:
            raise Exception(f"Unsupported unary operator: {op_value}")
    
    def visit_NumberNode(self, node):
        const_idx = self.bytecode.add_constant(node.value)
        self.bytecode.add(OpCode.LOAD_CONST, const_idx)
    
    def visit_StringNode(self, node):
        const_idx = self.bytecode.add_constant(node.value)
        self.bytecode.add(OpCode.LOAD_CONST, const_idx)
    
    def visit_BooleanNode(self, node):
        const_idx = self.bytecode.add_constant(node.value)
        self.bytecode.add(OpCode.LOAD_CONST, const_idx)
    
    def visit_NullNode(self, node):
        self.bytecode.add(OpCode.PUSH, None)
    
    def visit_IdentifierNode(self, node):
        # Vérifier si c'est une variable ou une fonction
        self.bytecode.add(OpCode.LOAD_VAR, node.name)
    
    def visit_PropertyNode(self, node):
        if node.is_assignment:
            self.visit(node.value)
            self.bytecode.add(OpCode.STORE_PROPERTY, node.name)
        else:
            self.bytecode.add(OpCode.LOAD_PROPERTY, node.name)
    
    def visit_ArrayLiteralNode(self, node):
        for elem in node.elements:
            self.visit(elem)
        self.bytecode.add(OpCode.NEW_ARRAY, len(node.elements))
    
    def visit_ArrayAccessNode(self, node):
        if hasattr(node.array_name, 'name'):
            self.visit(node.array_name)
        else:
            self.bytecode.add(OpCode.LOAD_VAR, node.array_name)
        
        self.visit(node.index)
        
        if node.is_assignment:
            self.visit(node.value)
            self.bytecode.add(OpCode.STORE_INDEX)
        else:
            self.bytecode.add(OpCode.LOAD_INDEX)
    
    def visit_BreakNode(self, node):
        # TODO: implémenter break
        pass
    
    def visit_ContinueNode(self, node):
        # TODO: implémenter continue
        pass
    
    def visit_ImportNode(self, node):
        # L'import est géré par l'interpréteur, on l'ignore en bytecode
        pass
    
    def visit_FileWriteNode(self, node):
        self.visit(node.filename)
        self.visit(node.content)
        self.bytecode.add(OpCode.WRITE_FILE)
    
    def visit_FileReadNode(self, node):
        self.visit(node.filename)
        self.bytecode.add(OpCode.READ_FILE)
    
    def visit_SuperNode(self, node):
        # Implémentation simplifiée
        pass