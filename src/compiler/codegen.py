# src/compiler/codegen.py
"""
Générateur de code pour le compilateur LLVM
"""

class CodeGenerator:
    """
    Générateur de code pour le compilateur LLVM
    """
    
    def __init__(self, module):
        self.module = module
        self.builder = None
        self.variables = {}
        self.functions = {}
        self.current_function = None
    
    def generate(self, ast):
        """
        Génère le code à partir de l'AST
        """
        # Cette classe est utilisée par LLVMCompiler
        # L'implémentation est dans llvm_compiler.py
        pass
    
    def generate_function(self, func_node):
        """
        Génère une fonction
        """
        # À implémenter si besoin d'étendre
        pass
    
    def generate_statement(self, stmt_node):
        """
        Génère une statement
        """
        # À implémenter si besoin d'étendre
        pass
    
    def generate_expression(self, expr_node):
        """
        Génère une expression
        """
        # À implémenter si besoin d'étendre
        pass