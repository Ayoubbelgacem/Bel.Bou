# src/vm/vm.py
import sys
import os
import time
import json
from src.vm.bytecode import OpCode
from src.vm.closure import Closure, Environment
from src.vm.cache import VariableCache

class VM:
    def __init__(self, search_paths=None):
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
        self.exception_handlers = []
        self.search_paths = search_paths or []
        self.loaded_modules = {}

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
        self.exception_handlers = []
        self.loaded_modules = {}

        if self.debug:
            print("🚀 Starting VM execution (Optimized)...")
            bytecode.disassemble()

        try:
            while self.pc < len(self.code):
                opcode, arg = self.code[self.pc]
                self.pc += 1
                if self.debug:
                    print(f"  PC: {self.pc-1}, Op: {opcode.name}, Arg: {arg}, Stack: {self.stack}")
                try:
                    self.execute(opcode, arg)
                except Exception as e:
                    if self.exception_handlers:
                        handler = self.exception_handlers.pop()
                        del self.stack[handler['stack_len']:]
                        del self.frames[handler['frames_len']:]
                        self.stack.append(str(e))
                        self.pc = handler['catch_pc']
                        continue
                    raise
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
            self.var_cache.invalidate()
            for i, param in enumerate(params):
                if i < len(args):
                    self.variables[param] = args[i]
                else:
                    self.variables[param] = None
            self.pc = func.get('start', 0)
            return True
        return False

    def _compare(self, left, right, op):
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return op(left, right)
        try:
            lnum = float(left) if not isinstance(left, (int, float)) else left
            rnum = float(right) if not isinstance(right, (int, float)) else right
            return op(lnum, rnum)
        except (ValueError, TypeError):
            return op(str(left), str(right))

    def _call_function(self, func_name, return_override=None):
        if func_name in self.functions:
            func = self.functions[func_name]
            params = func.get('params', [])
            args = []
            for _ in range(len(params)):
                if self.stack:
                    args.insert(0, self.stack.pop())
            self.call_depth += 1
            if self.call_depth > self.max_call_depth:
                raise Exception("Maximum call depth exceeded (possible infinite recursion)")
            if return_override is None and self._is_tail_call():
                self.call_depth -= 1
                if self._tail_call(func_name, args):
                    return
            self.frames.append({
                'pc': self.pc,
                'variables': self.variables.copy(),
                'stack': self.stack.copy(),
                'return_override': return_override,
            })
            self.variables = {}
            self.var_cache.invalidate()
            for i, param in enumerate(params):
                if i < len(args):
                    self.variables[param] = args[i]
                else:
                    self.variables[param] = None
            self.pc = func.get('start', 0)
        else:
            self.stack.append(return_override)

    # ----- Import : ne pas exécuter, seulement récupérer les définitions -----
    def _import_module(self, module_name):
        if module_name in self.loaded_modules:
            return

        found = None
        for base in self.search_paths:
            path = os.path.join(base, f"{module_name}.bou")
            if os.path.exists(path):
                found = path
                break

        if found is None:
            try:
                mod = __import__(module_name)
                self.variables[module_name] = mod
                if self.debug:
                    print(f"✅ Module Python '{module_name}' imported")
                self.loaded_modules[module_name] = True
                return
            except ImportError:
                raise ImportError(f"Module '{module_name}' not found in search paths: {self.search_paths}")

        try:
            from src.lexer.lexer import Lexer
            from src.parser.parser import Parser
            from src.vm.compiler import Compiler

            with open(found, 'r', encoding='utf-8') as f:
                source = f.read()

            lexer = Lexer(source)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            ast = parser.parse()

            compiler = Compiler(search_paths=self.search_paths)
            module_bytecode = compiler.compile(ast)

            # 🔥 On ajoute les fonctions et classes SANS exécuter le module
            # Pour éviter les conflits avec les built-ins, on ne fusionne pas
            # les fonctions qui portent le nom d'un built-in (time_now, sleep, to_json).
            builtin_names = {'len', 'str', 'int', 'float', 'type', 'sum', 'max', 'min', 'time_now', 'sleep', 'to_json'}
            for name, func in module_bytecode.functions.items():
                if name not in builtin_names:
                    self.functions[name] = func
            self.classes.update(module_bytecode.classes)

            self.loaded_modules[module_name] = True
            if self.debug:
                print(f"✅ Module '{module_name}' loaded from {found} (definitions only)")

        except Exception as e:
            raise ImportError(f"Failed to load module '{module_name}' from {found}: {e}")

    # ----- Exécution d'un opcode -----
    def execute(self, opcode, arg):
        # ----- IMPORT -----
        if opcode == OpCode.IMPORT:
            self._import_module(arg)
            self.stack.append(True)
            return

        # ----- Stack -----
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

        # ----- Arithmétique -----
        elif opcode == OpCode.ADD:
            right = self.stack.pop() if self.stack else 0
            left = self.stack.pop() if self.stack else 0
            if left is None: left = 0
            if right is None: right = 0
            if isinstance(left, str) or isinstance(right, str):
                self.stack.append(str(left) + str(right))
            else:
                self.stack.append(left + right)

        elif opcode == OpCode.SUB:
            right = self.stack.pop() if self.stack else 0
            left = self.stack.pop() if self.stack else 0
            if left is None: left = 0
            if right is None: right = 0
            self.stack.append(left - right)

        elif opcode == OpCode.MUL:
            right = self.stack.pop() if self.stack else 0
            left = self.stack.pop() if self.stack else 0
            if left is None: left = 1
            if right is None: right = 1
            self.stack.append(left * right)

        elif opcode == OpCode.DIV:
            right = self.stack.pop() if self.stack else 1
            left = self.stack.pop() if self.stack else 0
            if left is None: left = 0
            if right is None: right = 1
            if right == 0:
                raise Exception("Division by zero")
            self.stack.append(left / right)

        elif opcode == OpCode.MOD:
            right = self.stack.pop() if self.stack else 1
            left = self.stack.pop() if self.stack else 0
            if left is None: left = 0
            if right is None: right = 1
            if right == 0:
                raise Exception("Modulo by zero")
            self.stack.append(left % right)

        elif opcode == OpCode.NEG:
            value = self.stack.pop() if self.stack else 0
            if value is None: value = 0
            self.stack.append(-value)

        elif opcode == OpCode.INC:
            value = self.stack.pop() if self.stack else 0
            if value is None: value = 0
            self.stack.append(value + 1)

        elif opcode == OpCode.DEC:
            value = self.stack.pop() if self.stack else 0
            if value is None: value = 0
            self.stack.append(value - 1)

        # ----- Comparaisons -----
        elif opcode == OpCode.EQ:
            right = self.stack.pop()
            left = self.stack.pop()
            self.stack.append(self._compare(left, right, lambda a, b: a == b))

        elif opcode == OpCode.NE:
            right = self.stack.pop()
            left = self.stack.pop()
            self.stack.append(self._compare(left, right, lambda a, b: a != b))

        elif opcode == OpCode.GT:
            right = self.stack.pop()
            left = self.stack.pop()
            self.stack.append(self._compare(left, right, lambda a, b: a > b))

        elif opcode == OpCode.LT:
            right = self.stack.pop()
            left = self.stack.pop()
            self.stack.append(self._compare(left, right, lambda a, b: a < b))

        elif opcode == OpCode.GE:
            right = self.stack.pop()
            left = self.stack.pop()
            self.stack.append(self._compare(left, right, lambda a, b: a >= b))

        elif opcode == OpCode.LE:
            right = self.stack.pop()
            left = self.stack.pop()
            self.stack.append(self._compare(left, right, lambda a, b: a <= b))

        # ----- Contrôle de flux -----
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

        # ----- Functions (priorité aux built‑ins) -----
        elif opcode == OpCode.CALL:
            if arg is not None:
                func_name = arg
            else:
                func_name = self.stack.pop() if self.stack else None

            # 🔥 Convertir en chaîne si nécessaire (pour les appels dynamiques)
            if func_name is not None and not isinstance(func_name, str):
                if hasattr(func_name, 'name'):
                    func_name = func_name.name
                else:
                    func_name = str(func_name)

            if func_name:
                # ✅ Priorité absolue aux built‑ins
                if func_name in ['len', 'str', 'int', 'float', 'type', 'sum', 'max', 'min', 'time_now', 'sleep', 'to_json']:
                    self._call_builtin(func_name)
                elif func_name in self.functions:
                    self._call_function(func_name)
                else:
                    self.stack.append(None)
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
                self.var_cache.invalidate()
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
                self.var_cache.invalidate()
                self.stack = frame['stack']
                override = frame.get('return_override')
                self.stack.append(override if override is not None else result)
            else:
                self.stack.append(result)

        elif opcode == OpCode.RETURN_FAST:
            result = self.stack.pop() if self.stack else None
            self.stack.append(result)

        # ----- Objets -----
        elif opcode == OpCode.NEW_OBJECT:
            num_args = arg if isinstance(arg, int) else 0
            class_name = self.stack.pop() if self.stack else None
            args = [None] * num_args
            for i in range(num_args - 1, -1, -1):
                args[i] = self.stack.pop() if self.stack else None

            if class_name in self.classes:
                obj = {
                    '__class__': class_name,
                    '__properties__': {},
                    '__methods__': self.classes[class_name]['methods'].copy()
                }
                cls = self.classes[class_name]
                if cls.get('parent') and cls['parent'] in self.classes:
                    parent = self.classes[cls['parent']]
                    for m_name, m_info in parent['methods'].items():
                        if m_name not in obj['__methods__']:
                            obj['__methods__'][m_name] = m_info

                self.objects[f"obj_{self.object_counter}"] = obj
                self.object_counter += 1

                if 'jdid' in obj['__methods__']:
                    func_name = obj['__methods__']['jdid']['func_name']
                    if func_name in self.functions:
                        self.stack.append(obj)
                        for a in args:
                            self.stack.append(a)
                        self._call_function(func_name, return_override=obj)
                    else:
                        self.stack.append(obj)
                else:
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
            if isinstance(arg, tuple):
                method_name, num_args = arg
            else:
                method_name, num_args = arg, 0

            obj = self.stack.pop() if self.stack else None
            args = []
            for _ in range(num_args):
                args.insert(0, self.stack.pop() if self.stack else None)

            if obj and isinstance(obj, dict) and '__methods__' in obj:
                if method_name in obj['__methods__']:
                    func_name = obj['__methods__'][method_name]['func_name']
                    if func_name in self.functions:
                        self.stack.append(obj)
                        for a in args:
                            self.stack.append(a)
                        self._call_function(func_name)
                    else:
                        self.stack.append(None)
                else:
                    self.stack.append(None)
            else:
                self.stack.append(None)

        elif opcode == OpCode.CALL_METHOD_FAST:
            if isinstance(arg, tuple):
                method_name, num_args = arg
            else:
                method_name, num_args = arg, 0

            obj = self.stack.pop() if self.stack else None
            args = []
            for _ in range(num_args):
                args.insert(0, self.stack.pop() if self.stack else None)

            if obj and isinstance(obj, dict) and '__methods__' in obj:
                if method_name in obj['__methods__']:
                    func_name = obj['__methods__'][method_name]['func_name']
                    if func_name in self.functions:
                        self.stack.append(obj)
                        for a in args:
                            self.stack.append(a)
                        self._call_function(func_name)
                    else:
                        self.stack.append(None)
                else:
                    self.stack.append(None)
            else:
                self.stack.append(None)

        # ----- Tableaux -----
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

        # ----- I/O -----
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

        # ----- Fichiers -----
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

        # ----- Exceptions -----
        elif opcode == OpCode.TRY:
            self.exception_handlers.append({
                'catch_pc': arg,
                'stack_len': len(self.stack),
                'frames_len': len(self.frames),
            })

        elif opcode == OpCode.CATCH:
            if self.exception_handlers:
                self.exception_handlers.pop()

        # ----- HALT -----
        elif opcode == OpCode.HALT:
            self.pc = len(self.code)

        else:
            raise Exception(f"Unknown opcode: {opcode}")

    # ===== Built‑ins =====
    def _call_builtin(self, func_name):
        if func_name == 'len':
            if self.stack:
                val = self.stack.pop()
                if isinstance(val, list) or isinstance(val, str):
                    self.stack.append(len(val))
                else:
                    self.stack.append(0)
            else:
                self.stack.append(0)

        elif func_name == 'str':
            if self.stack:
                val = self.stack.pop()
                self.stack.append(str(val))
            else:
                self.stack.append("")

        elif func_name == 'int':
            if self.stack:
                val = self.stack.pop()
                try:
                    self.stack.append(int(val))
                except:
                    self.stack.append(0)
            else:
                self.stack.append(0)

        elif func_name == 'float':
            if self.stack:
                val = self.stack.pop()
                try:
                    self.stack.append(float(val))
                except:
                    self.stack.append(0.0)
            else:
                self.stack.append(0.0)

        elif func_name == 'type':
            if self.stack:
                val = self.stack.pop()
                if isinstance(val, int):
                    type_str = "int"
                elif isinstance(val, float):
                    type_str = "float"
                elif isinstance(val, str):
                    type_str = "str"
                elif isinstance(val, bool):
                    type_str = "bool"
                elif isinstance(val, list):
                    type_str = "list"
                elif isinstance(val, dict):
                    type_str = "object"
                else:
                    type_str = "unknown"
                self.stack.append(type_str)
            else:
                self.stack.append("unknown")

        elif func_name == 'sum':
            if self.stack:
                arr = self.stack.pop()
                if isinstance(arr, list):
                    total = 0
                    for x in arr:
                        if isinstance(x, (int, float)):
                            total += x
                    self.stack.append(total)
                else:
                    self.stack.append(0)
            else:
                self.stack.append(0)

        elif func_name == 'max':
            if self.stack:
                arr = self.stack.pop()
                if isinstance(arr, list) and len(arr) > 0:
                    max_val = arr[0]
                    for x in arr:
                        if x > max_val:
                            max_val = x
                    self.stack.append(max_val)
                else:
                    self.stack.append(0)
            else:
                self.stack.append(0)

        elif func_name == 'min':
            if self.stack:
                arr = self.stack.pop()
                if isinstance(arr, list) and len(arr) > 0:
                    min_val = arr[0]
                    for x in arr:
                        if x < min_val:
                            min_val = x
                    self.stack.append(min_val)
                else:
                    self.stack.append(0)
            else:
                self.stack.append(0)

        elif func_name == 'time_now':
            self.stack.append(int(time.time()))

        elif func_name == 'sleep':
            if self.stack:
                seconds = self.stack.pop()
                time.sleep(float(seconds))
                self.stack.append(0)
            else:
                self.stack.append(0)

        elif func_name == 'to_json':
            if self.stack:
                val = self.stack.pop()
                try:
                    self.stack.append(json.dumps(val, ensure_ascii=False))
                except:
                    self.stack.append("null")
            else:
                self.stack.append("null")

        else:
            self.stack.append(None)

    def get_output(self):
        return '\n'.join(self.output) if self.output else ""

    def get_stack(self):
        return self.stack

    def get_variables(self):
        return self.variables