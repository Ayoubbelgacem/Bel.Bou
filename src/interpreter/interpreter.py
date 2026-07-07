# src/interpreter/interpreter.py

import os
import sys
from src.parser.ast import *

class ReturnException(Exception):
    def __init__(self, value):
        self.value = value

class BreakException(Exception):
    pass

class ContinueException(Exception):
    pass

class Interpreter:
    def __init__(self):
        self.environment = {}
        self.functions = {}
        self.classes = {}
        self.output = []
        self.last_result = None
        self.is_repl = False
        self.debug = False
        self.objects = {}
        self.object_counter = 0
        self.env_stack = []
    
    def interpret(self, node, is_repl=False):
        self.is_repl = is_repl
        if hasattr(node, 'statements'):
            for stmt in node.statements:
                self.visit(stmt)
        else:
            return self.visit(node)
    
    def visit(self, node):
        if node is None:
            return None
        node_type = node.__class__.__name__
        visit_method = getattr(self, f'visit_{node_type}', None)
        if visit_method:
            return visit_method(node)
        return None
    
    def visit_ProgramNode(self, node):
        for stmt in node.statements:
            self.visit(stmt)
    
    def visit_VariableNode(self, node):
        value = self.visit(node.value)
        self.environment[node.name] = value
        
        if isinstance(value, dict) and '__class__' in value:
            self.objects[node.name] = value
        
        return value
    
    def visit_AssignmentNode(self, node):
        value = self.visit(node.value)
        self.environment[node.name] = value
        
        if isinstance(value, dict) and '__class__' in value:
            self.objects[node.name] = value
        
        return value
    
    def visit_NumberNode(self, node):
        return node.value
    
    def visit_StringNode(self, node):
        return node.value
    
    def visit_BooleanNode(self, node):
        return node.value
    
    def visit_NullNode(self, node):
        return None
    
    def visit_IdentifierNode(self, node):
        if node.name in self.environment:
            return self.environment[node.name]
        if node.name in self.objects:
            return self.objects[node.name]
        return None
    
    def visit_BinOpNode(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        
        # Gérer les None
        if left is None:
            left = 0
        if right is None:
            right = 0
        
        op = node.op
        
        # Normalisation du token
        op_value = None
        if hasattr(op, "value"):
            op_value = op.value
        elif hasattr(op, "name"):
            op_value = op.name
        else:
            op_value = str(op)
        
        # Comparaisons robustes
        if op_value in ["PLUS", "TokenType.PLUS", "PLUS_EQUALS", "TokenType.PLUS_EQUALS"]:
            if isinstance(left, str) or isinstance(right, str):
                return str(left) + str(right)
            return left + right
        
        if op_value in ["MINUS", "TokenType.MINUS", "MINUS_EQUALS", "TokenType.MINUS_EQUALS"]:
            return left - right
        
        if op_value in ["STAR", "TokenType.STAR", "STAR_EQUALS", "TokenType.STAR_EQUALS"]:
            return left * right
        
        if op_value in ["SLASH", "TokenType.SLASH", "SLASH_EQUALS", "TokenType.SLASH_EQUALS"]:
            if right == 0:
                raise Exception("Division by zero")
            return left / right
        
        if op_value in ["MOD", "TokenType.MOD"]:
            if right == 0:
                raise Exception("Modulo by zero")
            return left % right
        
        if op_value in ["GREATER", "TokenType.GREATER"]:
            return left > right
        
        if op_value in ["LESS", "TokenType.LESS"]:
            return left < right
        
        if op_value in ["GREATER_EQUAL", "TokenType.GREATER_EQUAL"]:
            return left >= right
        
        if op_value in ["LESS_EQUAL", "TokenType.LESS_EQUAL"]:
            return left <= right
        
        if op_value in ["EQUAL_EQUAL", "TokenType.EQUAL_EQUAL"]:
            return left == right
        
        if op_value in ["NOT_EQUAL", "TokenType.NOT_EQUAL"]:
            return left != right
        
        if op_value in ["AND", "TokenType.AND"]:
            return left and right
        
        if op_value in ["OR", "TokenType.OR"]:
            return left or right
        
        return None
    
    def visit_PrintNode(self, node):
        value = self.visit(node.value)
        output = str(value) if value is not None else ""
        print(output)
        self.output.append(output)
        self.last_result = output
        return output
    
    def visit_IfNode(self, node):
        condition = self.visit(node.condition)
        if condition:
            for stmt in node.then_body:
                self.visit(stmt)
        elif node.else_body:
            if isinstance(node.else_body, list):
                for stmt in node.else_body:
                    self.visit(stmt)
            elif isinstance(node.else_body, IfNode):
                self.visit(node.else_body)
        return None
    
    def visit_ForNode(self, node):
        start = self.visit(node.start)
        end = self.visit(node.end)
        
        if start is None or end is None:
            return None
        
        try:
            start = int(start)
            end = int(end)
        except:
            return None
        
        for i in range(start, end + 1):
            self.environment[node.iterator] = i
            for stmt in node.body:
                self.visit(stmt)
        
        return None
    
    def visit_WhileNode(self, node):
        while self.visit(node.condition):
            for stmt in node.body:
                self.visit(stmt)
        return None
    
    def visit_FunctionNode(self, node):
        self.functions[node.name] = {
            'params': node.params,
            'body': node.body
        }
        return None
    
    def visit_ReturnNode(self, node):
        value = self.visit(node.value)
        raise ReturnException(value)
    
    def visit_CallNode(self, node):
        func_name = node.name
        if hasattr(node.name, 'name'):
            func_name = node.name.name
        
        # Vérifier les callbacks
        if isinstance(func_name, str):
            func_obj = self.environment.get(func_name)
            if callable(func_obj):
                args = [self.visit(arg) for arg in node.args]
                return func_obj(*args)
        
        # Vérifier les fonctions built-in
        builtin = self.call_builtin(func_name, node.args)
        if builtin is not None:
            return builtin
        
        # Vérifier les fonctions définies
        if func_name in self.functions:
            func = self.functions[func_name]
            args = [self.visit(arg) for arg in node.args]
            
            old_env = self.environment.copy()
            self.environment = {}
            
            for i, param in enumerate(func['params']):
                if i < len(args):
                    self.environment[param] = args[i]
            
            result = None
            try:
                for stmt in func['body']:
                    self.visit(stmt)
            except ReturnException as e:
                result = e.value
            
            self.environment = old_env
            return result
        
        return None
    
    def call_builtin(self, name, args):
        evaluated_args = [self.visit(arg) for arg in args]
        
        if name == "len":
            if len(evaluated_args) > 0:
                if isinstance(evaluated_args[0], (list, str, dict)):
                    return len(evaluated_args[0])
            return 0
        elif name == "str":
            if len(evaluated_args) > 0:
                return str(evaluated_args[0])
            return ""
        elif name == "int":
            if len(evaluated_args) > 0:
                try:
                    return int(evaluated_args[0])
                except:
                    return 0
            return 0
        elif name == "float":
            if len(evaluated_args) > 0:
                try:
                    return float(evaluated_args[0])
                except:
                    return 0.0
            return 0.0
        elif name == "type":
            if len(evaluated_args) > 0:
                return type(evaluated_args[0]).__name__
            return "NoneType"
        elif name == "print":
            for arg in evaluated_args:
                print(arg)
            return None
        elif name == "input":
            prompt = str(evaluated_args[0]) if evaluated_args else ""
            return input(prompt)
        elif name == "range":
            if len(evaluated_args) == 1:
                return list(range(int(evaluated_args[0])))
            elif len(evaluated_args) == 2:
                return list(range(int(evaluated_args[0]), int(evaluated_args[1])))
            elif len(evaluated_args) == 3:
                return list(range(int(evaluated_args[0]), int(evaluated_args[1]), int(evaluated_args[2])))
            return []
        elif name == "sum":
            if len(evaluated_args) > 0 and isinstance(evaluated_args[0], list):
                return sum(evaluated_args[0])
            return 0
        elif name == "max":
            if len(evaluated_args) > 0 and isinstance(evaluated_args[0], list):
                return max(evaluated_args[0])
            if evaluated_args:
                return max(evaluated_args)
            return None
        elif name == "min":
            if len(evaluated_args) > 0 and isinstance(evaluated_args[0], list):
                return min(evaluated_args[0])
            if evaluated_args:
                return min(evaluated_args)
            return None
        elif name == "abs":
            if len(evaluated_args) > 0:
                return abs(evaluated_args[0])
            return 0
        elif name == "sorted":
            if len(evaluated_args) > 0 and isinstance(evaluated_args[0], list):
                return sorted(evaluated_args[0])
            return []
        elif name == "append":
            if len(evaluated_args) >= 2 and isinstance(evaluated_args[0], list):
                evaluated_args[0].append(evaluated_args[1])
                return evaluated_args[0]
            return None
        elif name == "pop":
            if len(evaluated_args) >= 1 and isinstance(evaluated_args[0], list):
                if len(evaluated_args) == 1:
                    return evaluated_args[0].pop()
                else:
                    return evaluated_args[0].pop(int(evaluated_args[1]))
            return None
        
        return None
    
    def visit_ArrayLiteralNode(self, node):
        return [self.visit(elem) for elem in node.elements]
    
    def visit_ArrayAccessNode(self, node):
        array = None
        if hasattr(node.array_name, 'name'):
            array = self.environment.get(node.array_name.name)
            if array is None:
                array = self.objects.get(node.array_name.name)
        else:
            array = self.visit(node.array_name)
        
        if isinstance(array, list):
            index = self.visit(node.index)
            try:
                index = int(index)
            except:
                return None
            
            if node.is_assignment:
                value = self.visit(node.value)
                if 0 <= index < len(array):
                    array[index] = value
                else:
                    while len(array) <= index:
                        array.append(None)
                    array[index] = value
                return value
            if 0 <= index < len(array):
                return array[index]
        return None
    
    def visit_ClassNode(self, node):
        self.classes[node.name] = {
            'parent': node.parent,
            'methods': {},
            'properties': {}
        }
        
        for method in node.methods:
            self.classes[node.name]['methods'][method.name] = method
        
        for prop_name, prop_value in node.properties.items():
            self.classes[node.name]['properties'][prop_name] = prop_value
        
        return None
    
    def visit_MethodNode(self, node):
        return {
            'name': node.name,
            'params': node.params,
            'body': node.body
        }
    
    def visit_NewNode(self, node):
        class_name = node.class_name
        if class_name in self.classes:
            instance = {
                '__class__': class_name,
                '__properties__': {},
                '__methods__': {}
            }
            
            cls = self.classes[class_name]
            
            # Ajouter les méthodes et propriétés du parent
            if cls.get('parent'):
                parent = self.classes.get(cls['parent'])
                if parent:
                    instance['__methods__'].update(parent['methods'])
                    for prop_name, prop_value in parent['properties'].items():
                        if prop_name not in instance['__properties__']:
                            instance['__properties__'][prop_name] = None
            
            # Ajouter les méthodes et propriétés de la classe
            instance['__methods__'].update(cls['methods'])
            for prop_name, prop_value in cls['properties'].items():
                if prop_value is not None:
                    instance['__properties__'][prop_name] = self.visit(prop_value)
                else:
                    instance['__properties__'][prop_name] = None
            
            # Stocker l'instance
            if node.target:
                self.environment[node.target] = instance
                self.objects[node.target] = instance
            else:
                instance_id = f"obj_{self.object_counter}"
                self.object_counter += 1
                self.objects[instance_id] = instance
            
            # Appeler le constructeur
            if 'jdid' in instance['__methods__']:
                constructor = instance['__methods__']['jdid']
                old_env = self.environment.copy()
                self.environment = {'hetha': instance}
                
                args = [self.visit(arg) for arg in node.args]
                for i, param in enumerate(constructor.params):
                    if i < len(args):
                        self.environment[param] = args[i]
                
                try:
                    for stmt in constructor.body:
                        self.visit(stmt)
                except ReturnException:
                    pass
                
                self.environment = old_env
            
            return instance
        
        return None
    
    def _find_object(self, name):
        if name in self.environment:
            obj = self.environment[name]
            if isinstance(obj, dict) and '__class__' in obj:
                return obj
        
        for key, obj in self.objects.items():
            if obj.get('__class__') == name:
                return obj
            if key == name:
                return obj
        
        return None
    
    def visit_MethodCallNode(self, node):
        obj = self.environment.get(node.object_name)
        
        if obj is None:
            obj = self._find_object(node.object_name)
        
        if obj is None:
            for key, value in self.objects.items():
                if key == node.object_name or value.get('__class__') == node.object_name:
                    obj = value
                    break
        
        if isinstance(obj, dict) and '__methods__' in obj:
            method = obj['__methods__'].get(node.method_name)
            if method:
                args = [self.visit(arg) for arg in node.args]
                
                old_env = self.environment.copy()
                self.environment = {'hetha': obj}
                
                for i, param in enumerate(method.params):
                    if i < len(args):
                        self.environment[param] = args[i]
                
                result = None
                try:
                    for stmt in method.body:
                        self.visit(stmt)
                except ReturnException as e:
                    result = e.value
                
                self.environment = old_env
                return result
        
        return None
    
    def visit_PropertyNode(self, node):
        if isinstance(node.name, str):
            obj = self.environment.get('hetha')
            
            if obj is None:
                for key, value in self.environment.items():
                    if isinstance(value, dict) and '__class__' in value:
                        if value.get('__class__') == node.name or key == node.name:
                            obj = value
                            break
                if obj is None:
                    for key, value in self.objects.items():
                        if isinstance(value, dict) and '__class__' in value:
                            if value.get('__class__') == node.name or key == node.name:
                                obj = value
                                break
            
            if obj is None:
                return None
            
            if node.is_assignment:
                value = self.visit(node.value)
                obj['__properties__'][node.name] = value
                return value
            
            return obj['__properties__'].get(node.name)
        return None
    
    def visit_TryNode(self, node):
        try:
            for stmt in node.try_body:
                self.visit(stmt)
        except Exception as e:
            if node.catch_var:
                self.environment[node.catch_var] = str(e)
                for stmt in node.catch_body:
                    self.visit(stmt)
            else:
                raise
        finally:
            if node.finally_body:
                for stmt in node.finally_body:
                    self.visit(stmt)
        return None
    
    def visit_ImportNode(self, node):
        module_name = node.module
        try:
            module = __import__(module_name)
            self.environment[module_name] = module
            if self.is_repl:
                print(f"✅ Module '{module_name}' imported")
        except ImportError:
            if self.is_repl:
                print(f"❌ Module '{module_name}' not found")
        return None
    
    def visit_FileWriteNode(self, node):
        filename = self.visit(node.filename)
        content = self.visit(node.content)
        try:
            with open(str(filename), 'w', encoding='utf-8') as f:
                f.write(str(content))
            print(f"✅ Fichier '{filename}' écrit avec succès!")
            return True
        except Exception as e:
            error_msg = f"Error: {e}"
            print(error_msg)
            return error_msg
    
    def visit_FileReadNode(self, node):
        filename = self.visit(node.filename)
        try:
            with open(str(filename), 'r', encoding='utf-8') as f:
                content = f.read()
            if content:
                print(content)
            return content
        except Exception as e:
            error_msg = f"Error: {e}"
            print(error_msg)
            return error_msg
    
    def visit_UnaryOpNode(self, node):
        expr = self.visit(node.expr)
        op_value = node.op.value if hasattr(node.op, 'value') else str(node.op)
        
        if op_value in ["MINUS", "TokenType.MINUS"]:
            return -expr if expr is not None else 0
        elif op_value in ["NOT", "TokenType.NOT"]:
            return not expr
        return expr
    
    def visit_SuperNode(self, node):
        obj = self.environment.get('hetha')
        if obj and '__class__' in obj:
            class_name = obj['__class__']
            if class_name in self.classes:
                parent = self.classes[class_name].get('parent')
                if parent and parent in self.classes:
                    parent_methods = self.classes[parent]['methods']
                    if 'jdid' in parent_methods:
                        constructor = parent_methods['jdid']
                        args = [self.visit(arg) for arg in node.args]
                        
                        old_env = self.environment.copy()
                        self.environment = {'hetha': obj}
                        
                        for i, param in enumerate(constructor.params):
                            if i < len(args):
                                self.environment[param] = args[i]
                        
                        try:
                            for stmt in constructor.body:
                                self.visit(stmt)
                        except ReturnException:
                            pass
                        
                        self.environment = old_env
        return None
    
    def get_output(self):
        return '\n'.join(self.output)