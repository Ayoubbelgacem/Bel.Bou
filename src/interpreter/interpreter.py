# src/interpreter/interpreter.py
import os
import sys
from src.parser.ast import *

class ReturnException(Exception):
    """Exception pour capturer les retours des fonctions"""
    def __init__(self, value):
        self.value = value

class Interpreter:
    def __init__(self):
        self.environment = {}
        self.functions = {}
        self.classes = {}
        self.output = []
        self.arrays = {}
        self.objects = {}
        self.last_result = None
        self.is_repl = False
    
    def interpret(self, node, is_repl=False):
        self.is_repl = is_repl
        if isinstance(node, ProgramNode):
            try:
                for stmt in node.statements:
                    result = self.visit(stmt)
                    if is_repl and result is not None:
                        print(result)
            except ReturnException as e:
                # Capturer le return si jamais il remonte
                pass
        elif is_repl:
            result = self.visit(node)
            if result is not None:
                print(result)
            return result
    
    def visit(self, node):
        if isinstance(node, ProgramNode):
            self.visit_program(node)
        elif isinstance(node, VariableNode):
            return self.visit_variable(node)
        elif isinstance(node, AssignmentNode):
            return self.visit_assignment(node)
        elif isinstance(node, ArrayNode):
            return self.visit_array(node)
        elif isinstance(node, ArrayLiteralNode):
            return self.visit_array_literal(node)
        elif isinstance(node, ArrayAccessNode):
            return self.visit_array_access(node)
        elif isinstance(node, PrintNode):
            return self.visit_print(node)
        elif isinstance(node, InputNode):
            return self.visit_input(node)
        elif isinstance(node, FileWriteNode):
            return self.visit_file_write(node)
        elif isinstance(node, FileReadNode):
            return self.visit_file_read(node)
        elif isinstance(node, IfNode):
            return self.visit_if(node)
        elif isinstance(node, ForNode):
            return self.visit_for(node)
        elif isinstance(node, WhileNode):
            return self.visit_while(node)
        elif isinstance(node, FunctionNode):
            return self.visit_function(node)
        elif isinstance(node, ReturnNode):
            return self.visit_return(node)
        elif isinstance(node, CallNode):
            return self.visit_call(node)
        elif isinstance(node, ClassNode):
            return self.visit_class(node)
        elif isinstance(node, MethodNode):
            return self.visit_method(node)
        elif isinstance(node, NewNode):
            return self.visit_new(node)
        elif isinstance(node, MethodCallNode):
            return self.visit_method_call(node)
        elif isinstance(node, TryNode):
            return self.visit_try(node)
        elif isinstance(node, ImportNode):
            return self.visit_import(node)
        elif isinstance(node, BinOpNode):
            return self.visit_binop(node)
        elif isinstance(node, UnaryOpNode):
            return self.visit_unary(node)
        elif isinstance(node, NumberNode):
            return node.value
        elif isinstance(node, StringNode):
            return node.value
        elif isinstance(node, BooleanNode):
            return node.value
        elif isinstance(node, NullNode):
            return None
        elif isinstance(node, IdentifierNode):
            return self.visit_identifier(node)
        elif isinstance(node, PropertyNode):
            return self.visit_property(node)
        elif isinstance(node, SuperNode):
            return self.visit_super(node)
        else:
            return None
    
    def visit_program(self, node):
        for stmt in node.statements:
            self.visit(stmt)
    
    def visit_variable(self, node):
        value = self.visit(node.value)
        self.environment[node.name] = value
        return value
    
    def visit_assignment(self, node):
        value = self.visit(node.value)
        self.environment[node.name] = value
        return value
    
    def visit_array(self, node):
        elements = [self.visit(elem) for elem in node.elements]
        self.environment[node.name] = elements
        self.arrays[node.name] = elements
        return elements
    
    def visit_array_literal(self, node):
        return [self.visit(elem) for elem in node.elements]
    
    def visit_array_access(self, node):
        # Si node est un ArrayAccessNode avec array_name (string)
        if hasattr(node, 'array_name') and isinstance(node.array_name, str):
            array = self.environment.get(node.array_name)
            if array is None:
                array = self.arrays.get(node.array_name)
            
            if array and isinstance(array, list):
                index = self.visit(node.index)
                if isinstance(index, int):
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
            return None
        
        # Si node est un ArrayAccessNode avec node (objet)
        if hasattr(node, 'array_name') and hasattr(node.array_name, 'name'):
            obj = self.environment.get(node.array_name.name)
            if obj and isinstance(obj, list):
                index = self.visit(node.index)
                if isinstance(index, int) and 0 <= index < len(obj):
                    if node.is_assignment:
                        value = self.visit(node.value)
                        obj[index] = value
                        return value
                    return obj[index]
            return None
        
        return None
    
    def visit_print(self, node):
        value = self.visit(node.value)
        output = str(value) if value is not None else ""
        print(output)
        self.output.append(output)
        self.last_result = output
        return output
    
    def visit_input(self, node):
        prompt = self.visit(node.prompt) if node.prompt else ""
        return input(prompt)
    
    def visit_file_write(self, node):
        filename = self.visit(node.filename)
        content = self.visit(node.content)
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(str(content))
            return True
        except Exception as e:
            return f"Error: {e}"
    
    def visit_file_read(self, node):
        filename = self.visit(node.filename)
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        except Exception as e:
            return f"Error: {e}"
    
    def visit_if(self, node):
        condition = self.visit(node.condition)
        if condition:
            for stmt in node.then_body:
                result = self.visit(stmt)
                if isinstance(stmt, ReturnNode):
                    return result
        elif node.else_body:
            for stmt in node.else_body:
                result = self.visit(stmt)
                if isinstance(stmt, ReturnNode):
                    return result
        return None
    
    def visit_for(self, node):
        start = self.visit(node.start)
        end = self.visit(node.end)
        
        if start is None or end is None:
            return None
        
        for i in range(int(start), int(end) + 1):
            self.environment[node.iterator] = i
            for stmt in node.body:
                result = self.visit(stmt)
                if isinstance(stmt, ReturnNode):
                    return result
        return None
    
    def visit_while(self, node):
        while self.visit(node.condition):
            for stmt in node.body:
                result = self.visit(stmt)
                if isinstance(stmt, ReturnNode):
                    return result
        return None
    
    def visit_function(self, node):
        self.functions[node.name] = {
            'params': node.params,
            'body': node.body,
            'return_type': node.return_type
        }
        return None
    
    def visit_return(self, node):
        value = self.visit(node.value)
        raise ReturnException(value)
    
    def visit_call(self, node):
        # Vérifier les fonctions built-in
        builtin = self.call_builtin(node.name, node.args)
        if builtin is not None:
            return builtin
        
        # Vérifier les fonctions définies par l'utilisateur
        if node.name in self.functions:
            func = self.functions[node.name]
            args = [self.visit(arg) for arg in node.args]
            
            old_env = self.environment
            self.environment = {}
            
            for i, param in enumerate(func['params']):
                if i < len(args):
                    self.environment[param] = args[i]
            
            result = None
            try:
                for stmt in func['body']:
                    result = self.visit(stmt)
                    if isinstance(stmt, ReturnNode):
                        break
            except ReturnException as e:
                result = e.value
            
            self.environment = old_env
            return result
        
        return None
    
    def call_builtin(self, name, args):
        evaluated_args = [self.visit(arg) for arg in args]
        
        if name == "len":
            if len(evaluated_args) > 0:
                if isinstance(evaluated_args[0], list):
                    return len(evaluated_args[0])
                elif isinstance(evaluated_args[0], str):
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
        elif name == "input":
            if len(evaluated_args) > 0:
                return input(str(evaluated_args[0]))
            return input()
        elif name == "iqra_mlf":
            if len(evaluated_args) > 0:
                filename = str(evaluated_args[0])
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        return f.read()
                except Exception as e:
                    return f"Error: {e}"
            return ""
        elif name == "ikteb_fi_mlf":
            if len(evaluated_args) >= 2:
                filename = str(evaluated_args[0])
                content = str(evaluated_args[1])
                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(content)
                    return True
                except Exception as e:
                    return f"Error: {e}"
            return False
        
        return None
    
    def visit_class(self, node):
        self.classes[node.name] = {
            'parent': node.parent,
            'methods': {},
            'properties': {}
        }
        
        # Add methods
        for method in node.methods:
            self.classes[node.name]['methods'][method.name] = method
        
        # Add properties
        for prop in node.properties:
            if hasattr(prop, 'name'):
                self.classes[node.name]['properties'][prop.name] = prop
        
        return None
    
    def visit_method(self, node):
        return node
    
    def _resolve_class_members(self, class_name):
        """Walk up the inheritance chain (toroth/parent) collecting methods
        and default properties, with subclasses overriding their parents."""
        if class_name not in self.classes:
            return {}, {}
        
        cls = self.classes[class_name]
        methods = {}
        properties = {}
        
        if cls.get('parent'):
            parent_methods, parent_properties = self._resolve_class_members(cls['parent'])
            methods.update(parent_methods)
            properties.update(parent_properties)
        
        methods.update(cls['methods'])
        properties.update(cls['properties'])
        
        return methods, properties
    
    def visit_new(self, node):
        class_name = node.class_name
        if class_name in self.classes:
            # Create instance
            instance = {
                '__class__': class_name,
                '__properties__': {},
                '__methods__': {}
            }
            
            all_methods, all_properties = self._resolve_class_members(class_name)
            
            # Add methods (including inherited ones)
            instance['__methods__'] = dict(all_methods)
            
            # Initialize default property values (including inherited ones)
            for prop_name, prop_node in all_properties.items():
                if prop_node and prop_node.value is not None:
                    instance['__properties__'][prop_name] = self.visit(prop_node.value)
                else:
                    instance['__properties__'][prop_name] = None
            
            # Store instance in objects
            instance_id = len(self.objects)
            self.objects[instance_id] = instance
            
            # Call constructor (jdid)
            if 'jdid' in instance['__methods__']:
                constructor = instance['__methods__']['jdid']
                old_env = self.environment
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
    
    def visit_method_call(self, node):
        obj = self.environment.get(node.object_name)
        
        if obj is None:
            for o in self.objects.values():
                if o.get('__class__') == node.object_name:
                    obj = o
                    break
        
        if isinstance(obj, dict) and '__methods__' in obj:
            method = obj['__methods__'].get(node.method_name)
            if method:
                args = [self.visit(arg) for arg in node.args]
                
                old_env = self.environment
                self.environment = {'hetha': obj}
                
                for i, param in enumerate(method.params):
                    if i < len(args):
                        self.environment[param] = args[i]
                
                result = None
                try:
                    for stmt in method.body:
                        result = self.visit(stmt)
                        if isinstance(stmt, ReturnNode):
                            break
                except ReturnException as e:
                    result = e.value
                
                self.environment = old_env
                return result
        
        return None
    
    def visit_property(self, node):
        if isinstance(node.name, str):
            obj = self.environment.get('hetha')
            if obj is None:
                return None
            
            if node.is_assignment:
                value = self.visit(node.value)
                obj['__properties__'][node.name] = value
                return value
            
            return obj['__properties__'].get(node.name)
        
        if hasattr(node.name, 'name'):
            obj = self.visit(node.name)
            if obj and isinstance(obj, dict):
                if node.is_assignment:
                    value = self.visit(node.value)
                    obj['__properties__'][node.name.name] = value
                    return value
                return obj['__properties__'].get(node.name.name)
        
        return None
    
    def visit_super(self, node):
        obj = self.environment.get('hetha')
        if obj:
            parent_class = self.classes.get(obj['__class__']).get('parent')
            if parent_class:
                parent_methods = self._resolve_class_members(parent_class)[0]
                if 'jdid' in parent_methods:
                    constructor = parent_methods['jdid']
                    args = [self.visit(arg) for arg in node.args]
                    old_env = self.environment
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
    
    def visit_try(self, node):
        try:
            for stmt in node.try_body:
                result = self.visit(stmt)
                if isinstance(stmt, ReturnNode):
                    return result
        except Exception as e:
            if node.catch_var:
                self.environment[node.catch_var] = str(e)
                for stmt in node.catch_body:
                    result = self.visit(stmt)
                    if isinstance(stmt, ReturnNode):
                        return result
        finally:
            if node.finally_body:
                for stmt in node.finally_body:
                    self.visit(stmt)
        return None
    
    def visit_import(self, node):
        module_name = node.module
        try:
            # Try to import Python module
            module = __import__(module_name)
            self.environment[module_name] = module
            print(f"✅ Module '{module_name}' imported")
        except ImportError:
            print(f"❌ Module '{module_name}' not found")
        return None
    
    def visit_binop(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        
        # Gérer les None
        if left is None and right is None:
            if node.op.value == "PLUS":
                return 0
            return None
        
        if left is None:
            if node.op.value == "PLUS":
                left = ""
            else:
                left = 0
        if right is None:
            if node.op.value == "PLUS":
                right = ""
            else:
                right = 0
        
        op_value = node.op.value if hasattr(node.op, 'value') else str(node.op)
        
        if op_value == "PLUS":
            if isinstance(left, str) or isinstance(right, str):
                return str(left) + str(right)
            return left + right
        elif op_value == "MINUS":
            return left - right
        elif op_value == "STAR":
            return left * right
        elif op_value == "SLASH":
            if right == 0:
                raise Exception("Division by zero")
            return left / right
        elif op_value == "MOD":
            if right == 0:
                raise Exception("Modulo by zero")
            return left % right
        elif op_value == "GREATER":
            return left > right
        elif op_value == "LESS":
            return left < right
        elif op_value == "GREATER_EQUAL":
            return left >= right
        elif op_value == "LESS_EQUAL":
            return left <= right
        elif op_value == "EQUAL_EQUAL":
            return left == right
        elif op_value == "NOT_EQUAL":
            return left != right
        
        return None
    
    def visit_unary(self, node):
        expr = self.visit(node.expr)
        if node.op.value == "MINUS":
            return -expr
        return expr
    
    def visit_identifier(self, node):
        if node.name in self.environment:
            return self.environment[node.name]
        return None
    
    def get_output(self):
        return '\n'.join(self.output)