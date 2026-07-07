# src/vm/vm.py
import sys
import os
from src.vm.bytecode import OpCode

class VM:
    def __init__(self):
        self.stack = []
        self.variables = {}
        self.functions = {}
        self.classes = {}
        self.objects = {}
        self.object_counter = 0
        self.pc = 0
        self.code = []
        self.constants = []
        self.frames = []
        self.output = []
        self.debug = False
        self.bytecode = None
    
    def run(self, bytecode, debug=False):
        self.debug = debug
        self.bytecode = bytecode
        self.code = bytecode.code
        self.constants = bytecode.constants
        self.functions = bytecode.functions
        self.classes = bytecode.classes
        self.pc = 0
        self.stack = []
        self.variables = {}
        self.frames = []
        self.output = []
        self.objects = {}
        self.object_counter = 0
        
        if self.debug:
            print("🚀 Starting VM execution...")
            bytecode.disassemble()
        
        try:
            while self.pc < len(self.code):
                opcode, arg = self.code[self.pc]
                self.pc += 1
                
                if self.debug:
                    print(f"  PC: {self.pc-1}, Op: {opcode.name}, Arg: {arg}, Stack: {self.stack}")
                
                self.execute(opcode, arg)
        except Exception as e:
            print(f"❌ VM Error at PC {self.pc-1}: {e}")
            raise
        
        if self.debug:
            print("✅ VM execution complete!")
        
        return self.output
    
    def execute(self, opcode, arg):
        # ===== STACK OPERATIONS =====
        if opcode == OpCode.PUSH:
            self.stack.append(arg)
        
        elif opcode == OpCode.POP:
            if self.stack:
                return self.stack.pop()
        
        elif opcode == OpCode.LOAD_CONST:
            if arg < len(self.constants):
                self.stack.append(self.constants[arg])
            else:
                self.stack.append(None)
        
        elif opcode == OpCode.LOAD_VAR:
            if arg in self.variables:
                self.stack.append(self.variables[arg])
            elif arg in self.functions:
                # Mettre la fonction sur la stack (callback)
                self.stack.append(arg)
            else:
                self.stack.append(None)
        
        elif opcode == OpCode.STORE_VAR:
            if self.stack:
                self.variables[arg] = self.stack.pop()
        
        # ===== ARITHMETIC =====
        elif opcode == OpCode.ADD:
            right = self.stack.pop() if self.stack else 0
            left = self.stack.pop() if self.stack else 0
            if left is None:
                left = 0
            if right is None:
                right = 0
            if isinstance(left, str) or isinstance(right, str):
                self.stack.append(str(left) + str(right))
            else:
                self.stack.append(left + right)
        
        elif opcode == OpCode.SUB:
            right = self.stack.pop() if self.stack else 0
            left = self.stack.pop() if self.stack else 0
            if left is None:
                left = 0
            if right is None:
                right = 0
            self.stack.append(left - right)
        
        elif opcode == OpCode.MUL:
            right = self.stack.pop() if self.stack else 0
            left = self.stack.pop() if self.stack else 0
            if left is None:
                left = 1
            if right is None:
                right = 1
            self.stack.append(left * right)
        
        elif opcode == OpCode.DIV:
            right = self.stack.pop() if self.stack else 1
            left = self.stack.pop() if self.stack else 0
            if left is None:
                left = 0
            if right is None:
                right = 1
            if right == 0:
                raise Exception("Division by zero")
            self.stack.append(left / right)
        
        elif opcode == OpCode.MOD:
            right = self.stack.pop() if self.stack else 1
            left = self.stack.pop() if self.stack else 0
            if left is None:
                left = 0
            if right is None:
                right = 1
            if right == 0:
                raise Exception("Modulo by zero")
            self.stack.append(left % right)
        
        # ===== COMPARISON =====
        elif opcode == OpCode.EQ:
            right = self.stack.pop()
            left = self.stack.pop()
            if left is None:
                left = 0
            if right is None:
                right = 0
            self.stack.append(left == right)
        
        elif opcode == OpCode.NE:
            right = self.stack.pop()
            left = self.stack.pop()
            if left is None:
                left = 0
            if right is None:
                right = 0
            self.stack.append(left != right)
        
        elif opcode == OpCode.GT:
            right = self.stack.pop()
            left = self.stack.pop()
            if left is None:
                left = 0
            if right is None:
                right = 0
            self.stack.append(left > right)
        
        elif opcode == OpCode.LT:
            right = self.stack.pop()
            left = self.stack.pop()
            if left is None:
                left = 0
            if right is None:
                right = 0
            self.stack.append(left < right)
        
        elif opcode == OpCode.GE:
            right = self.stack.pop()
            left = self.stack.pop()
            if left is None:
                left = 0
            if right is None:
                right = 0
            self.stack.append(left >= right)
        
        elif opcode == OpCode.LE:
            right = self.stack.pop()
            left = self.stack.pop()
            if left is None:
                left = 0
            if right is None:
                right = 0
            self.stack.append(left <= right)
        
        # ===== LOGIC =====
        elif opcode == OpCode.AND:
            right = self.stack.pop()
            left = self.stack.pop()
            self.stack.append(left and right)
        
        elif opcode == OpCode.OR:
            right = self.stack.pop()
            left = self.stack.pop()
            self.stack.append(left or right)
        
        elif opcode == OpCode.NOT:
            value = self.stack.pop()
            self.stack.append(not value)
        
        # ===== CONTROL FLOW =====
        elif opcode == OpCode.JUMP:
            if isinstance(arg, int):
                self.pc = arg
            elif isinstance(arg, str) and self.bytecode and arg in self.bytecode.labels:
                self.pc = self.bytecode.labels[arg]
        
        elif opcode == OpCode.JUMP_IF_FALSE:
            value = self.stack.pop()
            if not value:
                if isinstance(arg, int):
                    self.pc = arg
                elif isinstance(arg, str) and self.bytecode and arg in self.bytecode.labels:
                    self.pc = self.bytecode.labels[arg]
        
        elif opcode == OpCode.JUMP_IF_TRUE:
            value = self.stack.pop()
            if value:
                if isinstance(arg, int):
                    self.pc = arg
                elif isinstance(arg, str) and self.bytecode and arg in self.bytecode.labels:
                    self.pc = self.bytecode.labels[arg]
        
        # ===== FUNCTIONS =====
        elif opcode == OpCode.CALL:
            # Récupérer le nom de la fonction
            if arg is not None:
                func_name = arg
            else:
                # Le nom est sur la stack
                func_name = self.stack.pop() if self.stack else None
            
            if func_name and func_name in self.functions:
                func = self.functions[func_name]
                
                # Récupérer les paramètres
                params = func.get('params', [])
                args = []
                for _ in range(len(params)):
                    if self.stack:
                        args.insert(0, self.stack.pop())
                
                # Sauvegarder l'état
                self.frames.append({
                    'pc': self.pc,
                    'variables': self.variables.copy(),
                    'stack': self.stack.copy()
                })
                
                # Nouvel environnement
                self.variables = {}
                
                # Charger les paramètres
                for i, param in enumerate(params):
                    if i < len(args):
                        self.variables[param] = args[i]
                
                # Aller à la fonction
                self.pc = func.get('start', 0)
            else:
                self.stack.append(None)
        
        elif opcode == OpCode.RETURN:
            result = self.stack.pop() if self.stack else None
            if self.frames:
                frame = self.frames.pop()
                self.pc = frame['pc']
                self.variables = frame['variables']
                self.stack = frame['stack']
                self.stack.append(result)
            else:
                # Retour final
                self.stack.append(result)
            return result
        
        # ===== OBJECTS =====
        elif opcode == OpCode.NEW_OBJECT:
            class_name = self.stack.pop()
            args = []
            # Récupérer les arguments (dans l'ordre)
            for _ in range(len(self.stack)):
                args.insert(0, self.stack.pop())
            
            if class_name in self.classes:
                obj = {
                    '__class__': class_name,
                    '__properties__': {},
                    '__methods__': {}
                }
                
                cls = self.classes[class_name]
                
                # Héritage
                if cls.get('parent'):
                    parent = self.classes.get(cls['parent'])
                    if parent:
                        obj['__methods__'].update(parent.get('methods', {}))
                
                # Ajouter les méthodes
                obj['__methods__'].update(cls.get('methods', {}))
                
                # Ajouter les propriétés
                obj['__properties__'] = {}
                
                # Stocker l'objet
                obj_id = f"obj_{self.object_counter}"
                self.object_counter += 1
                self.objects[obj_id] = obj
                
                self.stack.append(obj)
            else:
                self.stack.append(None)
        
        elif opcode == OpCode.LOAD_PROPERTY:
            prop_name = arg
            obj = self.stack.pop() if self.stack else None
            if obj and isinstance(obj, dict):
                self.stack.append(obj.get('__properties__', {}).get(prop_name))
            else:
                self.stack.append(None)
        
        elif opcode == OpCode.STORE_PROPERTY:
            prop_name = arg
            value = self.stack.pop() if self.stack else None
            obj = self.stack.pop() if self.stack else None
            if obj and isinstance(obj, dict):
                obj['__properties__'][prop_name] = value
                self.stack.append(value)
            else:
                self.stack.append(None)
        
        elif opcode == OpCode.CALL_METHOD:
            method_name = arg
            # Récupérer l'objet
            obj = self.stack.pop() if self.stack else None
            # Récupérer les arguments
            args = []
            # On récupère les arguments dans l'ordre inverse
            # TODO: déterminer le nombre d'arguments
            while self.stack and len(self.stack) > 0:
                args.insert(0, self.stack.pop())
            
            if obj and isinstance(obj, dict) and '__methods__' in obj:
                method = obj['__methods__'].get(method_name)
                if method:
                    # Sauvegarder l'état
                    self.frames.append({
                        'pc': self.pc,
                        'variables': self.variables.copy(),
                        'stack': self.stack.copy()
                    })
                    
                    self.variables = {'hetha': obj}
                    
                    # Charger les paramètres
                    for i, param in enumerate(method.params):
                        if i < len(args):
                            self.variables[param] = args[i]
                    
                    # Exécuter la méthode
                    # TODO: Implémenter l'exécution des méthodes
                    self.stack.append(None)
        
        # ===== ARRAYS =====
        elif opcode == OpCode.NEW_ARRAY:
            elements = []
            for _ in range(arg if isinstance(arg, int) else 0):
                elements.insert(0, self.stack.pop() if self.stack else None)
            self.stack.append(elements)
        
        elif opcode == OpCode.LOAD_INDEX:
            index = self.stack.pop() if self.stack else 0
            array = self.stack.pop() if self.stack else []
            if not isinstance(index, int):
                try:
                    index = int(index)
                except:
                    index = 0
            if isinstance(array, list):
                if 0 <= index < len(array):
                    self.stack.append(array[index])
                else:
                    self.stack.append(None)
            else:
                self.stack.append(None)
        
        elif opcode == OpCode.STORE_INDEX:
            value = self.stack.pop() if self.stack else None
            index = self.stack.pop() if self.stack else 0
            array = self.stack.pop() if self.stack else []
            if not isinstance(index, int):
                try:
                    index = int(index)
                except:
                    index = 0
            if isinstance(array, list):
                if 0 <= index < len(array):
                    array[index] = value
                else:
                    while len(array) <= index:
                        array.append(None)
                    array[index] = value
                self.stack.append(value)
            else:
                self.stack.append(None)
        
        # ===== I/O =====
        elif opcode == OpCode.PRINT:
            value = self.stack.pop() if self.stack else ""
            if value is None:
                value = ""
            output = str(value)
            print(output)
            self.output.append(output)
            self.stack.append(output)
        
        elif opcode == OpCode.INPUT:
            prompt = self.stack.pop() if self.stack else ""
            try:
                value = input(str(prompt))
                self.stack.append(value)
            except:
                self.stack.append("")
        
        # ===== FILE I/O =====
        elif opcode == OpCode.READ_FILE:
            filename = self.stack.pop() if self.stack else ""
            try:
                with open(str(filename), 'r', encoding='utf-8') as f:
                    content = f.read()
                self.stack.append(content)
            except Exception as e:
                self.stack.append(f"Error: {e}")
        
        elif opcode == OpCode.WRITE_FILE:
            content = self.stack.pop() if self.stack else ""
            filename = self.stack.pop() if self.stack else ""
            try:
                with open(str(filename), 'w', encoding='utf-8') as f:
                    f.write(str(content))
                self.stack.append(True)
            except Exception as e:
                self.stack.append(f"Error: {e}")
        
        # ===== HALT =====
        elif opcode == OpCode.HALT:
            self.pc = len(self.code)
        
        else:
            raise Exception(f"Unknown opcode: {opcode}")
    
    def get_output(self):
        return '\n'.join(self.output) if self.output else ""
    
    def get_stack(self):
        return self.stack
    
    def get_variables(self):
        return self.variables