# src/vm/vm.py
import sys
import os
from src.vm.bytecode import OpCode
from src.vm.closure import Closure, Environment
from src.vm.cache import VariableCache

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
        self.var_cache = VariableCache()
        self.env = Environment()
        self.call_depth = 0
        self.max_call_depth = 1000
    
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
        self.call_depth = 0
        self.var_cache = VariableCache()
        self.env = Environment()
        
        if self.debug:
            print("🚀 Starting VM execution (Optimized)...")
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
            self._print_stats()
        
        return self.output
    
    def _print_stats(self):
        print("\n=== VM STATISTICS ===")
        print(f"  Instructions executed: {self.pc}")
        print(f"  Stack size: {len(self.stack)}")
        print(f"  Call depth: {self.call_depth}")
        cache_stats = self.var_cache.get_stats()
        print(f"  Cache hits: {cache_stats['hits']}")
        print(f"  Cache misses: {cache_stats['misses']}")
        print(f"  Hit rate: {cache_stats['hit_rate']:.1f}%")
        print("======================\n")
    
    def _is_tail_call(self):
        if self.pc < len(self.code):
            next_opcode = self.code[self.pc][0]
            return next_opcode == OpCode.RETURN
        return False
    
    def _tail_call(self, func_name, args):
        if func_name in self.functions:
            func = self.functions[func_name]
            params = func.get('params', [])
            
            for i, param in enumerate(params):
                if i < len(args):
                    self.variables[param] = args[i]
                else:
                    self.variables[param] = None
            
            self.pc = func.get('start', 0)
            return True
        
        return False
    
    def execute(self, opcode, arg):
        # ===== STACK OPERATIONS =====
        if opcode == OpCode.PUSH:
            self.stack.append(arg)
        
        elif opcode == OpCode.POP:
            if self.stack:
                return self.stack.pop()
        
        elif opcode == OpCode.DUP:
            if self.stack:
                self.stack.append(self.stack[-1])
        
        elif opcode == OpCode.SWAP:
            if len(self.stack) >= 2:
                a = self.stack.pop()
                b = self.stack.pop()
                self.stack.append(a)
                self.stack.append(b)
        
        elif opcode == OpCode.LOAD_CONST:
            if arg < len(self.constants):
                self.stack.append(self.constants[arg])
            else:
                self.stack.append(None)
        
        elif opcode == OpCode.LOAD_VAR:
            value = self.var_cache.get(arg)
            if value is not None:
                self.stack.append(value)
            else:
                if arg in self.variables:
                    value = self.variables[arg]
                    self.var_cache.set(arg, value)
                    self.stack.append(value)
                elif arg in self.functions:
                    self.stack.append(arg)
                else:
                    self.stack.append(None)
        
        elif opcode == OpCode.STORE_VAR:
            if self.stack:
                value = self.stack.pop()
                self.variables[arg] = value
                self.var_cache.set(arg, value)
        
        # ===== ARITHMETIC (Optimized) =====
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
        
        elif opcode == OpCode.NEG:
            value = self.stack.pop() if self.stack else 0
            if value is None:
                value = 0
            self.stack.append(-value)
        
        elif opcode == OpCode.INC:
            value = self.stack.pop() if self.stack else 0
            if value is None:
                value = 0
            self.stack.append(value + 1)
        
        elif opcode == OpCode.DEC:
            value = self.stack.pop() if self.stack else 0
            if value is None:
                value = 0
            self.stack.append(value - 1)
        
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
        
        elif opcode == OpCode.JUMP_IF_NIL:
            value = self.stack.pop()
            if value is None:
                if isinstance(arg, int):
                    self.pc = arg
                elif isinstance(arg, str) and self.bytecode and arg in self.bytecode.labels:
                    self.pc = self.bytecode.labels[arg]
        
        elif opcode == OpCode.LOOP:
            if self.stack:
                count = self.stack.pop()
                if count > 0:
                    self.stack.append(count - 1)
                    if isinstance(arg, int):
                        self.pc = arg
                    elif isinstance(arg, str) and self.bytecode and arg in self.bytecode.labels:
                        self.pc = self.bytecode.labels[arg]
        
        # ===== FUNCTIONS =====
        elif opcode == OpCode.CALL:
            if arg is not None:
                func_name = arg
            else:
                func_name = self.stack.pop() if self.stack else None
            
            if func_name and func_name in self.functions:
                func = self.functions[func_name]
                params = func.get('params', [])
                args = []
                for _ in range(len(params)):
                    if self.stack:
                        args.insert(0, self.stack.pop())
                
                self.call_depth += 1
                if self.call_depth > self.max_call_depth:
                    raise Exception("Maximum call depth exceeded (possible infinite recursion)")
                
                if self._is_tail_call():
                    self.call_depth -= 1
                    if self._tail_call(func_name, args):
                        return
                
                self.frames.append({
                    'pc': self.pc,
                    'variables': self.variables.copy(),
                    'stack': self.stack.copy()
                })
                
                self.variables = {}
                
                for i, param in enumerate(params):
                    if i < len(args):
                        self.variables[param] = args[i]
                    else:
                        self.variables[param] = None
                
                self.pc = func.get('start', 0)
            else:
                self.stack.append(None)
        
        elif opcode == OpCode.CALL_FAST:
            if arg is not None and arg in self.functions:
                func = self.functions[arg]
                params = func.get('params', [])
                args = []
                for _ in range(len(params)):
                    if self.stack:
                        args.insert(0, self.stack.pop())
                
                for i, param in enumerate(params):
                    if i < len(args):
                        self.variables[param] = args[i]
                    else:
                        self.variables[param] = None
                
                self.pc = func.get('start', 0)
        
        elif opcode == OpCode.RETURN:
            result = self.stack.pop() if self.stack else None
            self.call_depth -= 1
            if self.frames:
                frame = self.frames.pop()
                self.pc = frame['pc']
                self.variables = frame['variables']
                self.stack = frame['stack']
                self.stack.append(result)
            else:
                self.stack.append(result)
        
        elif opcode == OpCode.RETURN_FAST:
            result = self.stack.pop() if self.stack else None
            self.stack.append(result)
        
        # ===== OBJECTS =====
        elif opcode == OpCode.NEW_OBJECT:
            class_name = self.stack.pop()
            args = []
            for _ in range(len(self.stack)):
                args.insert(0, self.stack.pop())
            
            if class_name in self.classes:
                obj = {
                    '__class__': class_name,
                    '__properties__': {},
                    '__methods__': {}
                }
                
                cls = self.classes[class_name]
                
                if cls.get('parent'):
                    parent = self.classes.get(cls['parent'])
                    if parent:
                        obj['__methods__'].update(parent.get('methods', {}))
                
                obj['__methods__'].update(cls.get('methods', {}))
                obj['__properties__'] = {}
                
                self.objects[f"obj_{self.object_counter}"] = obj
                self.object_counter += 1
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
            obj = self.stack.pop() if self.stack else None
            args = []
            while self.stack:
                args.insert(0, self.stack.pop())
            
            if obj and isinstance(obj, dict) and '__methods__' in obj:
                method = obj['__methods__'].get(method_name)
                if method:
                    self.frames.append({
                        'pc': self.pc,
                        'variables': self.variables.copy(),
                        'stack': self.stack.copy()
                    })
                    
                    self.variables = {'hetha': obj}
                    
                    for i, param in enumerate(method.params):
                        if i < len(args):
                            self.variables[param] = args[i]
                    
                    self.stack.append(None)
        
        elif opcode == OpCode.CALL_METHOD_FAST:
            method_name = arg
            obj = self.stack.pop() if self.stack else None
            args = []
            while self.stack:
                args.insert(0, self.stack.pop())
            
            if obj and isinstance(obj, dict) and '__methods__' in obj:
                method = obj['__methods__'].get(method_name)
                if method:
                    for i, param in enumerate(method.params):
                        if i < len(args):
                            self.variables[param] = args[i]
                    
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
        
        elif opcode == OpCode.ARRAY_LEN:
            array = self.stack.pop() if self.stack else []
            if isinstance(array, list):
                self.stack.append(len(array))
            else:
                self.stack.append(0)
        
        # ===== I/O =====
        elif opcode == OpCode.PRINT:
            value = self.stack.pop() if self.stack else ""
            if value is None:
                value = ""
            output = str(value)
            print(output)
            self.output.append(output)
            self.stack.append(output)
        
        elif opcode == OpCode.PRINT_FAST:
            value = self.stack.pop() if self.stack else ""
            if value is None:
                value = ""
            output = str(value)
            print(output)
            self.output.append(output)
        
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