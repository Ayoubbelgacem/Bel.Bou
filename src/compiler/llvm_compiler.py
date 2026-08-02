"""
Compilateur LLVM principal pour Bou.Bel
Version décomposée - Orchestrateur
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path

print("🔍 [TRACE] llvm_compiler.py chargé", file=sys.stderr)
print(f"   - __file__ = {__file__}", file=sys.stderr)

try:
    import llvmlite.ir as ir
    import llvmlite.binding as llvm
    LLVM_AVAILABLE = True
except ImportError:
    LLVM_AVAILABLE = False

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from src.parser.ast import ProgramNode, FunctionNode, ClassNode, ImportNode
except ImportError:
    try:
        from parser.ast import ProgramNode, FunctionNode, ClassNode, ImportNode
    except ImportError:
        class ProgramNode: pass
        class FunctionNode: pass
        class ClassNode: pass
        class ImportNode: pass

try:
    from src.optimizer.ast_optimizer import ASTOptimizer
except ImportError:
    ASTOptimizer = None

from .llvm import (
    RuntimeHelper,
    UtilsHelper,
    TypesHelper,
    ArraysHelper,
    StringsHelper,
    ExpressionsHelper,
    StatementsHelper,
    BuiltinsHelper,
    OOPHelper,
    FilesHelper,
    ControlFlowHelper
)


class LLVMCompiler:
    def __init__(self, optimize=True, debug=False):
        if not LLVM_AVAILABLE:
            raise ImportError("llvmlite is required for native compilation")

        self.optimize = optimize
        self.ast_optimize = optimize
        self.debug = debug

        # État du compilateur
        self.module = None
        self.builder = None
        self.functions = {}
        self.variables = {}
        self.variable_types = {}
        self.current_function = None
        self.function_args = {}
        self.string_constants = {}
        self.loop_stack = []
        self.target_machine = None
        self.triple = None

        self.function_return_type = {}
        self.array_sizes = {}
        self.array_length = {}
        self.is_array = {}
        self.function_array_params = {}
        self.array_values = {}
        self.function_return_array_param = {}
        self._array_ptr_lengths = {}
        self.bool_variables = set()

        # OOP
        self.classes = {}
        self.object_class = {}
        self.runtime_initialized = False
        self.class_methods = {}
        self.current_this_ptr = None

        # Runtime functions (seront définies par RuntimeHelper)
        self.runtime_new_class = None
        self.runtime_new_object = None
        self.runtime_get_field = None
        self.runtime_set_field = None
        self.runtime_call_method = None
        self.runtime_free_object = None
        self.runtime_try_start = None
        self.runtime_try_end = None
        self.runtime_throw = None
        self.runtime_get_exception = None
        self.runtime_exception_message = None
        self.runtime_exception_pending = None
        self.runtime_create_callback = None
        self.runtime_create_closure = None
        self.runtime_call_callback = None
        self.runtime_free_callback = None
        self.runtime_add_field = None
        self.runtime_add_method = None
        self.runtime_get_field_string = None
        self.runtime_set_field_string = None
        self.runtime_file_write = None
        self.runtime_file_read = None
        self.runtime_value_to_string = None
        self.runtime_len = None
        self.runtime_typeof = None
        self.runtime_time_now = None
        self.runtime_sleep = None

        # GC functions
        self.runtime_incref = None
        self.runtime_decref = None

        # External functions
        self.printf = None
        self.puts = None
        self.strlen = None
        self.atoi = None
        self.atof = None
        self.scanf = None
        self.sprintf = None
        self.set_console_cp = None

        # --- Modules et packages ---
        self.loaded_modules = {}
        self.loading_modules = set()
        user_packages = os.path.join(os.path.expanduser("~"), ".boubel", "packages")
        self.module_paths = ['modules', '.', user_packages]

        self._init_helpers()

        try:
            llvm.initialize_native_target()
            llvm.initialize_native_asmprinter()
            self.target = llvm.Target.from_default_triple()
            self.target_machine = self.target.create_target_machine(reloc='static')
            self.triple = llvm.get_default_triple()
            if self.debug:
                print(f"Target triple: {self.triple}")
                print(f"Target: {self.target.name}")
        except Exception as e:
            print(f"Warning: LLVM initialization error: {e}")
            self.target_machine = None

        # Built-in functions
        self.builtin_functions = {
            'len': self._call_len,
            'str': self._call_str,
            'int': self._call_int,
            'float': self._call_float,
            'type': self._call_type,
            'print': self._call_print_builtin,
            'input': self._call_input_builtin,
            'sum': self._call_sum,
            'max': self._call_max,
            'min': self._call_min,
            'abs': self._call_abs,
            'concat': self._call_concat,
            'iqra_mlf': self._call_iqra_mlf,
            'ikteb_fi_mlf': self._call_ikteb_fi_mlf,
            'time_now': self._call_time_now,
            'sleep': self._call_sleep,
            'to_json': self._call_to_json,
        }

    def _init_helpers(self):
        print("🔍 [TRACE] Initialisation des helpers...", file=sys.stderr)
        self.runtime = RuntimeHelper(self)
        print("   - runtime OK", file=sys.stderr)
        self.utils = UtilsHelper(self)
        print("   - utils OK", file=sys.stderr)
        self.types = TypesHelper(self)
        print("   - types OK", file=sys.stderr)
        self.arrays = ArraysHelper(self)
        print("   - arrays OK", file=sys.stderr)
        self.strings = StringsHelper(self)
        print("   - strings OK", file=sys.stderr)
        self.expr = ExpressionsHelper(self)
        print("   - expr OK", file=sys.stderr)
        self.stmt = StatementsHelper(self)
        print("   - stmt OK", file=sys.stderr)
        self.builtins = BuiltinsHelper(self)
        print("   - builtins OK", file=sys.stderr)
        self.oop = OOPHelper(self)
        print("   - oop OK", file=sys.stderr)
        self.files = FilesHelper(self)
        print("   - files OK", file=sys.stderr)
        self.control = ControlFlowHelper(self)
        print("   - control OK", file=sys.stderr)
        print("🔍 [TRACE] Tous les helpers initialisés.", file=sys.stderr)

    # ===== Runtime =====
    def _init_runtime(self):
        if not self.runtime_initialized:
            self.runtime.init()
            self.runtime_initialized = True

    # === Méthodes pour les modules (avec filtrage des built-ins) ===
    def find_module_file(self, module_name):
        for base_path in self.module_paths:
            candidate1 = os.path.join(base_path, f"{module_name}.bou")
            if os.path.exists(candidate1):
                return candidate1
            candidate2 = os.path.join(base_path, module_name, f"{module_name}.bou")
            if os.path.exists(candidate2):
                return candidate2
        return None

    def load_module(self, module_name):
        if module_name in self.loaded_modules:
            return
        if module_name in self.loading_modules:
            raise RuntimeError(f"Cycle détecté lors de l'import de '{module_name}'")
        filepath = self.find_module_file(module_name)
        if filepath is None:
            raise FileNotFoundError(f"Module '{module_name}' introuvable dans {self.module_paths}")
        self.loading_modules.add(module_name)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                source = f.read()
            from src.lexer.lexer import Lexer
            from src.parser.parser import Parser
            lexer = Lexer(source)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            ast = parser.parse()
            for stmt in ast.statements:
                if isinstance(stmt, FunctionNode):
                    # ✅ FILTRE : on ignore les fonctions qui portent le nom d'un built-in
                    if stmt.name not in self.builtin_functions:
                        self.control.compile_function(stmt)
                elif isinstance(stmt, ClassNode):
                    self.oop.register_class(stmt)
                    self.oop.compile_class(stmt)
            self.loaded_modules[module_name] = True
        finally:
            self.loading_modules.remove(module_name)

    # === compile() ===
    def compile(self, node, output_file=None):
        if not LLVM_AVAILABLE:
            raise ImportError("llvmlite is required for native compilation")

        try:
            if self.ast_optimize and ASTOptimizer is not None:
                if self.debug:
                    print("🔧 Applying AST optimizations...")
                optimizer = ASTOptimizer(debug=self.debug)
                node = optimizer.optimize(node)
                if self.debug:
                    print("✅ AST optimizations applied.")

            self.module = ir.Module(name="boubel_module")
            self.module.triple = self.triple if hasattr(self, 'triple') else llvm.get_default_triple()

            if self.debug:
                print(f"Target triple: {self.module.triple}")

            self.utils.declare_external_functions()
            self._init_runtime()

            if isinstance(node, ProgramNode):
                for stmt in node.statements:
                    if isinstance(stmt, ClassNode):
                        self.oop.register_class(stmt)
                for stmt in node.statements:
                    if isinstance(stmt, ImportNode):
                        self.load_module(stmt.module_name)
                    elif isinstance(stmt, FunctionNode):
                        self.control.compile_function(stmt)
                    elif isinstance(stmt, ClassNode):
                        self.oop.compile_class(stmt)

            self.control.compile_main(node)

            if self.optimize:
                self.control.optimize_module(self.module)

            if self.debug:
                print("\nLLVM IR Generated:")
                print("-" * 50)
                print(str(self.module))
                print("-" * 50)

            if output_file:
                return self._compile_to_executable(output_file)

            return str(self.module)

        except Exception as e:
            print(f"Compilation error: {e}")
            if self.debug:
                import traceback
                traceback.print_exc()
            raise

    # ---------- Délégation aux helpers ----------
    def _compile_expression(self, node):
        return self.expr.compile(node)

    def _compile_statement(self, node):
        return self.stmt.compile(node)

    def _compile_binop(self, node):
        return self.expr.compile_binop(node)

    def _compile_print(self, node):
        return self.stmt.compile_print(node)

    def _compile_file_write(self, node):
        return self.files.compile_file_write(node)

    def _compile_file_read(self, node):
        return self.files.compile_file_read(node)

    # ---------- Appels des built-ins ----------
    def _call_len(self, args):
        return self.builtins.call_len(args)

    def _call_str(self, args):
        return self.builtins.call_str(args)

    def _call_int(self, args):
        return self.builtins.call_int(args)

    def _call_float(self, args):
        return self.builtins.call_float(args)

    def _call_type(self, args):
        return self.builtins.call_type(args)

    def _call_print_builtin(self, args):
        return self.builtins.call_print(args)

    def _call_input_builtin(self, args):
        return self.builtins.call_input(args)

    def _call_sum(self, args):
        return self.builtins.call_sum(args)

    def _call_max(self, args):
        return self.builtins.call_max(args)

    def _call_min(self, args):
        return self.builtins.call_min(args)

    def _call_abs(self, args):
        return self.builtins.call_abs(args)

    def _call_concat(self, args):
        return self.builtins.call_concat(args)

    def _call_iqra_mlf(self, args):
        return self.files.call_iqra_mlf(args)

    def _call_ikteb_fi_mlf(self, args):
        return self.files.call_ikteb_fi_mlf(args)

    def _call_time_now(self, args):
        return self.builtins.call_time_now(args)

    def _call_sleep(self, args):
        return self.builtins.call_sleep(args)

    def _call_to_json(self, args):
        return self.builtins.call_to_json(args)

    # ---------- Utilitaires ----------
    def _create_string(self, string):
        return self.utils.create_string(string)

    def _concat_strings(self, left, right):
        return self.utils.concat_strings(left, right)

    def _convert_to_string(self, value):
        return self.utils.convert_to_string(value)

    def _bool_to_string(self, value):
        return self.utils.bool_to_string(value)

    def _array_ptr_to_string(self, array_ptr, count_val, is_fixed_array):
        return self.arrays.array_ptr_to_string(array_ptr, count_val, is_fixed_array)

    def _print_array_runtime(self, array_ptr, count_val, is_fixed_array):
        return self.arrays.print_array_runtime(array_ptr, count_val, is_fixed_array)

    def _compile_array_literal(self, node):
        return self.arrays.compile_literal(node)

    def _compile_array_access(self, node):
        return self.arrays.compile_access(node)

    def _array_value_info(self, value):
        return self.arrays.value_info(value)

    def _is_array_pointer(self, value):
        return self.arrays.is_pointer(value)

    def _get_dynamic_length(self, value):
        return self.arrays.get_dynamic_length(value)

    def _coerce_to_i64(self, value):
        return self.types.coerce_to_i64(value)

    def _coerce_to_double(self, value):
        return self.types.coerce_to_double(value)

    def _promote_for_binop(self, left, right):
        return self.types.promote_for_binop(left, right)

    def _is_float_type(self, llvm_type):
        return self.types.is_float_type(llvm_type)

    def _compile_class(self, node):
        return self.oop.compile_class(node)

    def _compile_method(self, class_name, method_node):
        return self.oop.compile_method(class_name, method_node)

    def _compile_new(self, node):
        return self.oop.compile_new(node)

    def _compile_method_call(self, node):
        return self.oop.compile_method_call(node)

    def _compile_property(self, node):
        return self.oop.compile_property(node)

    def _compile_super(self, node):
        return self.oop.compile_super(node)

    def _compile_main(self, node):
        return self.control.compile_main(node)

    def _compile_function(self, func_node):
        return self.control.compile_function(func_node)

    def _compile_if(self, node):
        return self.control.compile_if(node)

    def _compile_for(self, node):
        return self.control.compile_for(node)

    def _compile_while(self, node):
        return self.control.compile_while(node)

    def _compile_return(self, node):
        return self.control.compile_return(node)

    def _compile_break(self):
        return self.control.compile_break()

    def _compile_continue(self):
        return self.control.compile_continue()

    def _compile_try(self, node):
        return self.control.compile_try(node)

    def _optimize_module(self):
        return self.control.optimize_module(self.module)

    def _compile_variable(self, node):
        return self.stmt.compile_variable(node)

    def _compile_assignment(self, node):
        return self.stmt.compile_assignment(node)

    def _compile_input(self, node):
        return self.stmt.compile_input(node)

    def _compile_call(self, node):
        return self.stmt.compile_call(node)

    def _declare_runtime_func(self, name, return_type, param_types):
        return self.runtime.declare(name, return_type, param_types)

    # ---------- Génération d'exécutable ----------
    def _compile_to_executable(self, output_file):
        obj_path = None
        try:
            module_ir = str(self.module)
            parsed_module = llvm.parse_assembly(module_ir)
            parsed_module.verify()

            target_machine = self.target_machine
            if target_machine is None:
                target = llvm.Target.from_default_triple()
                target_machine = target.create_target_machine(reloc='static')

            obj_file = tempfile.NamedTemporaryFile(suffix='.o', delete=False)
            obj_path = obj_file.name
            obj_file.close()

            with open(obj_path, 'wb') as f:
                f.write(target_machine.emit_object(parsed_module))

            if self.debug:
                print(f"📦 Object file created: {obj_path}")

            linker_cmd = shutil.which('clang') or shutil.which('gcc') or shutil.which('cc')

            if linker_cmd is None:
                candidates = [
                    'C:/msys64/ucrt64/bin/gcc.exe',
                    'C:/msys64/mingw64/bin/gcc.exe',
                    '/ucrt64/bin/gcc.exe',
                    '/ucrt64/bin/gcc',
                ]
                for path in candidates:
                    if os.path.exists(path):
                        linker_cmd = path
                        break

            if linker_cmd is None:
                print("❌ GCC/Clang not found. Please install MSYS2 with GCC.")
                print("   Download: https://www.msys2.org/")
                print("   Then run: pacman -S mingw-w64-ucrt-x86_64-gcc")
                return module_ir

            if self.debug:
                print(f"🔧 Using linker: {linker_cmd}")

            if os.name == 'nt':
                if not output_file.endswith('.exe'):
                    output_file += '.exe'
            else:
                if not output_file.endswith('.out'):
                    output_file += '.out'

            current_dir = os.getcwd()
            runtime_dir = os.path.join(current_dir, 'runtime')
            if os.path.basename(current_dir) == 'compiler':
                runtime_dir = os.path.join(os.path.dirname(os.path.dirname(current_dir)), 'runtime')

            runtime_a = os.path.join(runtime_dir, 'libboubel_runtime.a')
            runtime_dll = os.path.join(runtime_dir, 'libboubel_runtime.dll')

            if self.debug:
                print(f"📁 Runtime directory: {runtime_dir}")
                print(f"📦 Static library: {runtime_a} exists: {os.path.exists(runtime_a)}")
                print(f"📦 DLL: {runtime_dll} exists: {os.path.exists(runtime_dll)}")

            cmd = [linker_cmd, obj_path, '-o', output_file]

            if os.name != 'nt':
                cmd.append('-lm')
            else:
                cmd.append('-no-pie')
                if os.path.exists(runtime_a):
                    cmd.append(runtime_a)
                    if self.debug:
                        print(f"🔧 Using static library: {runtime_a}")
                elif os.path.exists(runtime_dll):
                    cmd.append(runtime_dll)
                    if self.debug:
                        print(f"🔧 Using DLL: {runtime_dll}")
                    output_dir = os.path.dirname(output_file) or '.'
                    dest_dll = os.path.join(output_dir, 'libboubel_runtime.dll')
                    if not os.path.exists(dest_dll):
                        shutil.copy(runtime_dll, dest_dll)
                        if self.debug:
                            print(f"📋 Copied runtime DLL to: {dest_dll}")
                else:
                    print("❌ Runtime library not found!")
                    print(f"   Looking in: {runtime_dir}")
                    print("   Please compile it first:")
                    print("   cd runtime && python build_runtime.py")
                    return module_ir

            if self.debug:
                print(f"🔧 Linking: {' '.join(cmd)}")

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(f"⚠️ Linker output:\n{result.stderr}")

            if result.returncode != 0:
                print(f"❌ Linking failed with code {result.returncode}")
                return module_ir

            print(f"✅ Compiled successfully: {output_file}")
            return output_file

        except Exception as e:
            print(f"❌ Error during executable generation: {e}")
            if self.debug:
                import traceback
                traceback.print_exc()
            return str(self.module)

        finally:
            if obj_path and os.path.exists(obj_path):
                try:
                    os.remove(obj_path)
                except Exception:
                    pass

    def compile_to_ir(self, node):
        self.compile(node)
        return str(self.module)