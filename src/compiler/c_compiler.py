"""
Compilateur C pour Bou.Bel
Génère du code C à partir de l'AST et le compile en exécutable
"""

import os
import subprocess
import tempfile
import sys
from src.parser.ast import *

class CCompiler:
    """
    Compilateur C pour Bou.Bel
    Génère du code C à partir de l'AST
    """
    
    def __init__(self, debug=False):
        self.debug = debug
        self.variables = {}  # nom -> (type, nom_c)
        self.functions = {}
        self.indent = 0
        self.code = []
        self.string_constants = {}
        self.loop_stack = []
        self.temp_var_count = 0
        self.arrays = {}
        self.array_sizes = {}
    
    def _escape_string(self, string):
        """Échappe une chaîne pour le code C"""
        if string is None:
            return ""
        return (string
                .replace("\\", "\\\\")
                .replace('"', '\\"')
                .replace("\n", "\\n")
                .replace("\t", "\\t")
                .replace("\r", "\\r"))
    
    def _get_array_size(self, name):
        """Retourne la taille d'un tableau"""
        if name in self.array_sizes:
            return self.array_sizes[name]
        return 0
    
    def _get_c_type(self, type_name):
        """Convertit un type Bou.Bel en type C"""
        types = {
            'int': 'long long',
            'real': 'double',
            'string': 'char*',
            'bool': 'int',
            'char': 'char',
            None: 'long long'  # Default
        }
        return types.get(type_name, 'long long')
    
    def _get_default_value(self, type_name):
        """Retourne la valeur par défaut pour un type"""
        defaults = {
            'int': '0',
            'real': '0.0',
            'string': '""',
            'bool': '0',
            'char': "'\\0'",
            None: '0'
        }
        return defaults.get(type_name, '0')
    
    def compile(self, node, output_file=None):
        """Compile un AST Bou.Bel en code C"""
        try:
            self.code = []
            self.variables = {}
            self.functions = {}
            self.string_constants = {}
            self.loop_stack = []
            self.indent = 0
            self.temp_var_count = 0
            self.arrays = {}
            self.array_sizes = {}
            
            # En-tête du fichier
            self._add_line('#include <stdio.h>')
            self._add_line('#include <stdlib.h>')
            self._add_line('#include <string.h>')
            self._add_line('#include <math.h>')
            self._add_line('#include <assert.h>')
            self._add_line('#ifdef _WIN32')
            self._add_line('#include <windows.h>')
            self._add_line('#endif')
            self._add_line('')
            
            # Compiler les fonctions
            if isinstance(node, ProgramNode):
                for stmt in node.statements:
                    if isinstance(stmt, FunctionNode):
                        self._compile_function(stmt)
            
            # Compiler le main
            self._compile_main(node)
            
            # Écrire le code C
            c_code = '\n'.join(self.code)
            
            if self.debug:
                print("\n📄 C Code Generated:")
                print("-" * 50)
                print(c_code)
                print("-" * 50)
            
            # Si un fichier de sortie est spécifié, compiler en exécutable
            if output_file:
                return self._compile_c_to_exe(c_code, output_file)
            
            return c_code
            
        except Exception as e:
            print(f"❌ Compilation error in CCompiler: {e}")
            if self.debug:
                import traceback
                traceback.print_exc()
            raise
    
    def _add_line(self, line):
        """Ajoute une ligne avec indentation"""
        if line:
            self.code.append('    ' * self.indent + line)
        else:
            self.code.append('')
    
    def _compile_main(self, node):
        """Compile le programme principal avec support UTF-8"""
        self._add_line('int main(int argc, char** argv) {')
        self.indent += 1
        
        # Support UTF-8 pour Windows
        self._add_line('#ifdef _WIN32')
        self._add_line('SetConsoleOutputCP(CP_UTF8);')
        self._add_line('#endif')
        self._add_line('')
        
        if isinstance(node, ProgramNode):
            for stmt in node.statements:
                if not isinstance(stmt, FunctionNode):
                    self._compile_statement(stmt)
        
        self._add_line('return 0;')
        self.indent -= 1
        self._add_line('}')
    
    def _compile_function(self, func_node):
        """Compile une fonction Bou.Bel en C"""
        old_vars = self.variables.copy()
        old_arrays = self.arrays.copy()
        old_sizes = self.array_sizes.copy()
        self.variables = {}
        self.arrays = {}
        self.array_sizes = {}
        
        # Les paramètres sont toujours des long long par défaut
        params_str = ', '.join(f'long long {p}' for p in func_node.params)
        self._add_line(f'long long {func_node.name}({params_str}) {{')
        self.indent += 1
        
        for param in func_node.params:
            self.variables[param] = ('int', param)
        
        for stmt in func_node.body:
            self._compile_statement(stmt)
        
        if not any(isinstance(stmt, ReturnNode) for stmt in func_node.body):
            self._add_line('return 0;')
        
        self.indent -= 1
        self._add_line('}')
        self._add_line('')
        self.variables = old_vars
        self.arrays = old_arrays
        self.array_sizes = old_sizes
    
    def _compile_statement(self, node):
        """Compile une statement"""
        if node is None:
            return
        
        if isinstance(node, VariableNode):
            self._compile_variable(node)
        elif isinstance(node, AssignmentNode):
            self._compile_assignment(node)
        elif isinstance(node, PrintNode):
            self._compile_print(node)
        elif isinstance(node, InputNode):
            self._compile_input(node)
        elif isinstance(node, IfNode):
            self._compile_if(node)
        elif isinstance(node, ForNode):
            self._compile_for(node)
        elif isinstance(node, WhileNode):
            self._compile_while(node)
        elif isinstance(node, ReturnNode):
            self._compile_return(node)
        elif isinstance(node, CallNode):
            self._compile_call(node)
        elif isinstance(node, BreakNode):
            self._compile_break()
        elif isinstance(node, ContinueNode):
            self._compile_continue()
        elif isinstance(node, FileWriteNode):
            self._compile_file_write(node)
        elif isinstance(node, FileReadNode):
            self._compile_file_read(node)
        elif isinstance(node, ArrayLiteralNode):
            self._compile_array_literal(node)
        elif isinstance(node, ArrayAccessNode):
            self._compile_array_access(node)
        else:
            expr = self._compile_expression(node)
            if expr and not isinstance(node, (NumberNode, StringNode, BooleanNode, IdentifierNode)):
                self._add_line(f'{expr};')
    
    def _compile_variable(self, node):
        """Compile une variable avec son type"""
        try:
            c_type = self._get_c_type(node.type_name)
            
            if isinstance(node.value, ArrayLiteralNode):
                # Variable tableau
                size = len(node.value.elements)
                self._add_line(f'{c_type} {node.name}[{size}];')
                self.arrays[node.name] = node.name
                self.array_sizes[node.name] = size
                for i, elem in enumerate(node.value.elements):
                    val = self._compile_expression(elem)
                    self._add_line(f'{node.name}[{i}] = {val};')
                self.variables[node.name] = (node.type_name, node.name)
            else:
                value = self._compile_expression(node.value)
                if value is not None:
                    self._add_line(f'{c_type} {node.name} = {value};')
                    self.variables[node.name] = (node.type_name, node.name)
                else:
                    # Valeur par défaut
                    default = self._get_default_value(node.type_name)
                    self._add_line(f'{c_type} {node.name} = {default};')
                    self.variables[node.name] = (node.type_name, node.name)
        except Exception as e:
            print(f"Error compiling variable {node.name}: {e}")
            raise
    
    def _compile_assignment(self, node):
        """Compile une assignation"""
        try:
            value = self._compile_expression(node.value)
            if node.name in self.variables:
                var_type, var_cname = self.variables[node.name]
                self._add_line(f'{var_cname} = {value};')
            elif node.name in self.arrays:
                self._add_line(f'// {node.name} is an array, cannot assign directly')
            else:
                # Assignation implicite - utiliser int par défaut
                self._add_line(f'long long {node.name} = {value};')
                self.variables[node.name] = ('int', node.name)
        except Exception as e:
            print(f"Error compiling assignment {node.name}: {e}")
            raise
    
    def _compile_print(self, node):
        """Compile un print avec support des types et tableaux"""
        try:
            # Cas 1: Chaîne littérale
            if isinstance(node.value, StringNode):
                clean_value = self._escape_string(node.value.value)
                self._add_line(f'printf("{clean_value}\\n");')
                return
            
            # Cas 2: Identifiant (variable ou tableau)
            if isinstance(node.value, IdentifierNode):
                name = node.value.name
                
                # Si c'est un tableau
                if name in self.arrays or name in self.array_sizes:
                    size = self._get_array_size(name)
                    if size > 0:
                        # Afficher le tableau comme [1, 2, 3]
                        self._add_line(f'printf("[");')
                        self._add_line(f'for(int i=0;i<{size};i++) {{')
                        self.indent += 1
                        self._add_line(f'printf("%lld", {name}[i]);')
                        self._add_line(f'if(i<{size}-1) printf(", ");')
                        self.indent -= 1
                        self._add_line(f'}}')
                        self._add_line(f'printf("]\\n");')
                        return
                
                # Variable - vérifier le type pour le format
                if name in self.variables:
                    var_type, _ = self.variables[name]
                    if var_type == 'string':
                        self._add_line(f'printf("%s\\n", {name});')
                        return
                    elif var_type == 'real':
                        self._add_line(f'printf("%f\\n", {name});')
                        return
                    elif var_type == 'char':
                        self._add_line(f'printf("%c\\n", {name});')
                        return
                    elif var_type == 'bool':
                        self._add_line(f'printf("%s\\n", {name} ? "s7i7" : "ghalet");')
                        return
                
                # Fallback: int
                self._add_line(f'printf("%lld\\n", (long long){name});')
                return
            
            # Cas 3: Expression
            value = self._compile_expression(node.value)
            if value is not None:
                self._add_line(f'printf("%lld\\n", (long long){value});')
                
        except Exception as e:
            print(f"Error compiling print: {e}")
            raise
    
    def _compile_input(self, node):
        """Compile un input"""
        var_name = f'temp_input_{self.temp_var_count}'
        self.temp_var_count += 1
        self._add_line(f'long long {var_name};')
        self._add_line(f'scanf("%lld", &{var_name});')
        return var_name
    
    def _compile_expression(self, node):
        """Compile une expression"""
        if node is None:
            return '0'
        
        if isinstance(node, NumberNode):
            return str(node.value)
        elif isinstance(node, StringNode):
            clean = self._escape_string(node.value)
            return f'"{clean}"'
        elif isinstance(node, BooleanNode):
            return '1' if node.value else '0'
        elif isinstance(node, NullNode):
            return '0'
        elif isinstance(node, IdentifierNode):
            if node.name in self.variables:
                _, var_cname = self.variables[node.name]
                return var_cname
            elif node.name in self.arrays:
                return node.name
            self._add_line(f'long long {node.name} = 0;')
            self.variables[node.name] = ('int', node.name)
            return node.name
        elif isinstance(node, BinOpNode):
            left = self._compile_expression(node.left)
            right = self._compile_expression(node.right)
            op = self._get_c_op(node.op)
            if op == '/' or op == '%':
                return f'(({right} != 0) ? ({left} {op} {right}) : 0)'
            return f'({left} {op} {right})'
        elif isinstance(node, CallNode):
            return self._compile_call(node)
        elif isinstance(node, UnaryOpNode):
            expr = self._compile_expression(node.expr)
            op = node.op.value if hasattr(node.op, 'value') else str(node.op)
            if op in ['MINUS', 'TokenType.MINUS', '-']:
                return f'(-{expr})'
            elif op in ['NOT', 'TokenType.NOT', '!']:
                return f'(!{expr})'
            return expr
        elif isinstance(node, ArrayLiteralNode):
            if node.elements:
                return self._compile_expression(node.elements[0])
            return '0'
        elif isinstance(node, ArrayAccessNode):
            array_name = node.array_name.name if hasattr(node.array_name, 'name') else str(node.array_name)
            index = self._compile_expression(node.index)
            if node.is_assignment:
                value = self._compile_expression(node.value)
                self._add_line(f'{array_name}[{index}] = {value};')
                return value
            return f'{array_name}[{index}]'
        else:
            return '0'
    
    def _get_c_op(self, op):
        """Convertit un token en opérateur C"""
        if hasattr(op, 'value'):
            op_value = op.value
        else:
            op_value = str(op)
        
        ops = {
            'PLUS': '+', 'MINUS': '-', 'STAR': '*', 'SLASH': '/', 'MOD': '%',
            'EQUAL_EQUAL': '==', 'NOT_EQUAL': '!=', 'GREATER': '>', 'LESS': '<',
            'GREATER_EQUAL': '>=', 'LESS_EQUAL': '<=', 'AND': '&&', 'OR': '||'
        }
        return ops.get(op_value, '+')
    
    def _compile_if(self, node):
        """Compile un if"""
        try:
            condition = self._compile_expression(node.condition)
            self._add_line(f'if ({condition}) {{')
            self.indent += 1
            for stmt in node.then_body:
                self._compile_statement(stmt)
            self.indent -= 1
            
            if node.else_body:
                self._add_line('} else {')
                self.indent += 1
                if isinstance(node.else_body, list):
                    for stmt in node.else_body:
                        self._compile_statement(stmt)
                elif isinstance(node.else_body, IfNode):
                    self._compile_if(node.else_body)
                self.indent -= 1
            
            self._add_line('}')
        except Exception as e:
            print(f"Error compiling if: {e}")
            raise
    
    def _compile_for(self, node):
        """Compile un for avec support des variables de boucle"""
        try:
            start = self._compile_expression(node.start)
            end = self._compile_expression(node.end)
            self.loop_stack.append(('for', node.iterator, None))
            
            # Sauvegarder l'ancienne valeur si la variable existe déjà
            old_type = None
            old_cname = None
            if node.iterator in self.variables:
                old_type, old_cname = self.variables[node.iterator]
            
            # Déclarer et initialiser la variable de boucle
            self._add_line(f'for (long long {node.iterator} = {start}; {node.iterator} <= {end}; {node.iterator}++) {{')
            
            # Ajouter la variable de boucle à self.variables
            self.variables[node.iterator] = ('int', node.iterator)
            
            self.indent += 1
            
            for stmt in node.body:
                self._compile_statement(stmt)
            
            self.indent -= 1
            self._add_line('}')
            self.loop_stack.pop()
            
            # Restaurer l'ancienne valeur ou supprimer la variable
            if old_type is not None:
                self.variables[node.iterator] = (old_type, old_cname)
            elif node.iterator in self.variables:
                del self.variables[node.iterator]
                
        except Exception as e:
            print(f"Error compiling for: {e}")
            raise
    
    def _compile_while(self, node):
        """Compile un while"""
        try:
            condition = self._compile_expression(node.condition)
            self.loop_stack.append(('while', None, None))
            
            self._add_line(f'while ({condition}) {{')
            self.indent += 1
            
            for stmt in node.body:
                self._compile_statement(stmt)
            
            self.indent -= 1
            self._add_line('}')
            self.loop_stack.pop()
        except Exception as e:
            print(f"Error compiling while: {e}")
            raise
    
    def _compile_return(self, node):
        """Compile un return"""
        try:
            value = self._compile_expression(node.value)
            self._add_line(f'return (long long){value};')
        except Exception as e:
            print(f"Error compiling return: {e}")
            raise
    
    def _compile_call(self, node):
        """Compile un appel de fonction"""
        try:
            func_name = node.name.name if hasattr(node.name, 'name') else node.name
            args = [self._compile_expression(arg) for arg in node.args]
            
            if func_name == 'len':
                if args:
                    if args[0] in self.array_sizes:
                        return str(self.array_sizes[args[0]])
                    return f'strlen({args[0]})'
                return '0'
            elif func_name == 'str':
                return f'"{args[0]}"' if args else '""'
            elif func_name == 'int':
                return f'atoi({args[0]})' if args else '0'
            elif func_name == 'float':
                return f'atof({args[0]})' if args else '0.0'
            elif func_name == 'type':
                return '"int"'
            elif func_name == 'printf':
                return f'printf({", ".join(args)})'
            elif func_name == 'print':
                for arg in args:
                    self._add_line(f'printf("%s\\n", {arg});')
                return '0'
            
            return f'{func_name}({", ".join(args)})'
        except Exception as e:
            print(f"Error compiling call {func_name}: {e}")
            raise
    
    def _compile_break(self):
        self._add_line('break;')
    
    def _compile_continue(self):
        self._add_line('continue;')
    
    def _compile_file_write(self, node):
        try:
            filename = self._compile_expression(node.filename)
            content = self._compile_expression(node.content)
            self._add_line(f'FILE* f = fopen({filename}, "w");')
            self._add_line(f'fprintf(f, "%s", {content});')
            self._add_line('fclose(f);')
        except Exception as e:
            print(f"Error compiling file write: {e}")
            raise
    
    def _compile_file_read(self, node):
        try:
            filename = self._compile_expression(node.filename)
            self._add_line(f'FILE* f = fopen({filename}, "r");')
            self._add_line('char buffer[1024];')
            self._add_line('fread(buffer, 1, 1023, f);')
            self._add_line('fclose(f);')
            return 'buffer'
        except Exception as e:
            print(f"Error compiling file read: {e}")
            raise
    
    def _compile_array_literal(self, node):
        arr_name = f'arr_{self.temp_var_count}'
        self.temp_var_count += 1
        size = len(node.elements)
        self._add_line(f'long long {arr_name}[{size}];')
        self.arrays[arr_name] = arr_name
        self.array_sizes[arr_name] = size
        for i, elem in enumerate(node.elements):
            val = self._compile_expression(elem)
            self._add_line(f'{arr_name}[{i}] = {val};')
        return arr_name
    
    def _compile_array_access(self, node):
        array_name = node.array_name.name if hasattr(node.array_name, 'name') else str(node.array_name)
        index = self._compile_expression(node.index)
        if node.is_assignment:
            value = self._compile_expression(node.value)
            self._add_line(f'{array_name}[{index}] = {value};')
            return value
        return f'{array_name}[{index}]'
    

    def _compile_c_to_exe(self, c_code, output_file):
      """Compile le code C en exécutable"""
      try:
        c_file = tempfile.NamedTemporaryFile(suffix='.c', delete=False)
        c_file.write(c_code.encode('utf-8'))
        c_file.close()
        
        if self.debug:
            print(f"📝 C file created: {c_file.name}")
        
        # ✅ Vérifier GCC avec shutil
        import shutil
        gcc_cmd = shutil.which('gcc')
        
        if not gcc_cmd:
            # Fallback: chemins MSYS2
            gcc_paths = [
                '/ucrt64/bin/gcc.exe',
                'C:/msys64/ucrt64/bin/gcc.exe',
                'C:/msys64/mingw64/bin/gcc.exe',
                'C:/msys64/ucrt64/bin/gcc',
            ]
            for path in gcc_paths:
                if os.path.exists(path):
                    gcc_cmd = path
                    break
        
        if gcc_cmd is None:
            print("❌ GCC not found. Please install MSYS2 with GCC.")
            print("   Download: https://www.msys2.org/")
            print("   Then run: pacman -S mingw-w64-ucrt-x86_64-gcc")
            return c_code
        
        if self.debug:
            print(f"🔧 Using GCC: {gcc_cmd}")
        
        # ✅ Ajouter les flags d'optimisation
        flags = ['-O2', '-Wall', '-Wno-unused-variable']
        
        # Déterminer le nom de sortie
        if os.name == 'nt':
            if not output_file.endswith('.exe'):
                output_file += '.exe'
        else:
            if not output_file.endswith('.out'):
                output_file += '.out'
        
        # Compiler
        cmd = [gcc_cmd, c_file.name, '-o', output_file, '-lm', '-w'] + flags
        
        if self.debug:
            print(f"🔧 Compiling: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.stdout:
            print(result.stdout)
        
        if result.stderr:
            print(f"⚠️ Compiler output:\n{result.stderr}")
        
        if result.returncode != 0:
            print(f"❌ Compilation failed with code {result.returncode}")
            if self.debug:
                print(f"📄 Full C code:\n{c_code}")
            return c_code
        
        print(f"✅ Compiled successfully: {output_file}")
        return output_file
        
      except Exception as e:
        print(f"❌ Compilation error: {e}")
        if self.debug:
            import traceback
            traceback.print_exc()
        return c_code
    
      finally:
        try:
            if os.path.exists(c_file.name):
                os.remove(c_file.name)
        except:
            pass
    


