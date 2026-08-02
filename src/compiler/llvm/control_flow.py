"""
Structure de contrôle pour le compilateur LLVM
"""

import llvmlite.ir as ir
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from src.parser.ast import (
        IfNode, ProgramNode, ClassNode, FunctionNode,
        VariableNode, ArrayLiteralNode, ReturnNode, StringNode, NumberNode,
        IdentifierNode, BinOpNode, CallNode, ArrayAccessNode
    )
except ImportError:
    class IfNode: pass
    class ProgramNode: pass
    class ClassNode: pass
    class FunctionNode: pass
    class VariableNode: pass
    class ArrayLiteralNode: pass
    class ReturnNode: pass
    class StringNode: pass
    class NumberNode: pass
    class IdentifierNode: pass
    class BinOpNode: pass
    class CallNode: pass
    class ArrayAccessNode: pass


class ControlFlowHelper:
    """Gestion des structures de contrôle"""

    def __init__(self, compiler):
        self.compiler = compiler

    def compile_if(self, node):
        condition = self.compiler.expr.compile(node.condition)
        cond_bool = self.compiler.builder.icmp_signed('!=', condition, ir.Constant(ir.IntType(64), 0))

        then_block = self.compiler.current_function.append_basic_block(name="then")
        else_block = self.compiler.current_function.append_basic_block(name="else")
        end_block = self.compiler.current_function.append_basic_block(name="endif")

        self.compiler.builder.cbranch(cond_bool, then_block, else_block)

        self.compiler.builder.position_at_start(then_block)
        for stmt in node.then_body:
            self.compiler.stmt.compile(stmt)
        if not self.compiler.builder.block.is_terminated:
            self.compiler.builder.branch(end_block)

        self.compiler.builder.position_at_start(else_block)
        if node.else_body:
            if isinstance(node.else_body, list):
                for stmt in node.else_body:
                    self.compiler.stmt.compile(stmt)
            elif isinstance(node.else_body, IfNode):
                self.compile_if(node.else_body)
        if not self.compiler.builder.block.is_terminated:
            self.compiler.builder.branch(end_block)

        self.compiler.builder.position_at_start(end_block)

    def compile_for(self, node):
        old_variables = self.compiler.variables.copy()
        old_types = self.compiler.variable_types.copy()
        old_is_array = self.compiler.is_array.copy()
        old_array_sizes = self.compiler.array_sizes.copy()
        old_array_values = self.compiler.array_values.copy()

        start_val = self.compiler.expr.compile(node.start)
        iter_alloca = self.compiler.builder.alloca(ir.IntType(64), name=node.iterator)
        self.compiler.builder.store(start_val, iter_alloca)
        self.compiler.variables[node.iterator] = iter_alloca
        self.compiler.variable_types[node.iterator] = ir.IntType(64)
        self.compiler.is_array[node.iterator] = False

        check_block = self.compiler.current_function.append_basic_block("for_check")
        body_block = self.compiler.current_function.append_basic_block("for_body")
        increment_block = self.compiler.current_function.append_basic_block("for_increment")
        end_block = self.compiler.current_function.append_basic_block("for_end")

        self.compiler.loop_stack.append((increment_block, end_block))

        self.compiler.builder.branch(check_block)

        self.compiler.builder.position_at_start(check_block)
        current = self.compiler.builder.load(iter_alloca)
        end_value = self.compiler.expr.compile(node.end)
        condition = self.compiler.builder.icmp_signed("<=", current, end_value)
        self.compiler.builder.cbranch(condition, body_block, end_block)

        self.compiler.builder.position_at_start(body_block)
        for stmt in node.body:
            self.compiler.stmt.compile(stmt)
        if not self.compiler.builder.block.is_terminated:
            self.compiler.builder.branch(increment_block)

        self.compiler.builder.position_at_start(increment_block)
        current = self.compiler.builder.load(iter_alloca)
        increment = self.compiler.builder.add(current, ir.Constant(ir.IntType(64), 1))
        self.compiler.builder.store(increment, iter_alloca)
        self.compiler.builder.branch(check_block)

        self.compiler.builder.position_at_start(end_block)
        self.compiler.loop_stack.pop()

        self.compiler.variables = old_variables
        self.compiler.variable_types = old_types
        self.compiler.is_array = old_is_array
        self.compiler.array_sizes = old_array_sizes
        self.compiler.array_values = old_array_values

    def compile_while(self, node):
        start_block = self.compiler.current_function.append_basic_block("while_start")
        body_block = self.compiler.current_function.append_basic_block("while_body")
        end_block = self.compiler.current_function.append_basic_block("while_end")

        self.compiler.loop_stack.append((start_block, end_block))

        self.compiler.builder.branch(start_block)
        self.compiler.builder.position_at_start(start_block)

        condition = self.compiler.expr.compile(node.condition)
        cond_bool = self.compiler.builder.icmp_signed('!=', condition, ir.Constant(ir.IntType(64), 0))
        self.compiler.builder.cbranch(cond_bool, body_block, end_block)

        self.compiler.builder.position_at_start(body_block)
        for stmt in node.body:
            self.compiler.stmt.compile(stmt)
        if not self.compiler.builder.block.is_terminated:
            self.compiler.builder.branch(start_block)

        self.compiler.builder.position_at_start(end_block)
        self.compiler.loop_stack.pop()

    def compile_return(self, node):
        value = self.compiler.expr.compile(node.value)

        func_name = self.compiler.current_function.name if self.compiler.current_function is not None else None
        if func_name == 'main':
            expected_type = ir.IntType(32)
        else:
            expected_type = self.compiler.function_return_type.get(func_name, ir.IntType(64))

        if expected_type == ir.PointerType(ir.IntType(8)):
            if str(value.type) != "i8*":
                value = self.compiler.utils.convert_to_string(value)
            elif value.type != expected_type:
                value = self.compiler.builder.bitcast(value, expected_type)

        elif expected_type == ir.DoubleType():
            value = self.compiler.types.coerce_to_double(value)

        elif expected_type == ir.PointerType(ir.IntType(64)):
            if value.type != expected_type:
                value = self.compiler.builder.bitcast(value, expected_type)

        elif isinstance(expected_type, ir.PointerType) and isinstance(expected_type.pointee, ir.ArrayType):
            if value.type != expected_type:
                zero_array = ir.Constant(
                    expected_type.pointee,
                    [ir.Constant(ir.IntType(64), 0)] * expected_type.pointee.count
                )
                tmp_alloca = self.compiler.builder.alloca(expected_type.pointee, name="ret_array_fallback")
                self.compiler.builder.store(zero_array, tmp_alloca)
                value = tmp_alloca

        else:
            value = self.compiler.types.coerce_to_i64(value)

        self.compiler.builder.ret(value)

    def compile_break(self):
        if self.compiler.loop_stack:
            _, end_block = self.compiler.loop_stack[-1]
            self.compiler.builder.branch(end_block)

    def compile_continue(self):
        if self.compiler.loop_stack:
            start_block, _ = self.compiler.loop_stack[-1]
            self.compiler.builder.branch(start_block)

    # ============================================================
    # TRY/CATCH/FINALLY - MODELE COOPERATIF (sans setjmp/longjmp)
    #
    # boubel_try_start() ne fait plus de setjmp (voir boubel_runtime.c pour
    # l'explication du segfault que ca causait). A la place, on insere une
    # verification boubel_exception_pending() APRES CHAQUE instruction du
    # bloc try : si une exception a ete levee (division/modulo par zero,
    # etc.), on saute directement vers le bloc catch au lieu de continuer
    # a executer le reste du bloc try avec des valeurs bidon.
    # ============================================================
    def compile_try(self, node):
        self.compiler.builder.call(self.compiler.runtime_try_start, [])

        try_block = self.compiler.current_function.append_basic_block("try_body")
        catch_block = self.compiler.current_function.append_basic_block("catch_body")
        finally_block = self.compiler.current_function.append_basic_block("finally_body")
        end_block = self.compiler.current_function.append_basic_block("try_end")

        self.compiler.builder.branch(try_block)
        self.compiler.builder.position_at_start(try_block)

        for stmt in node.try_body:
            if self.compiler.builder.block.is_terminated:
                break

            self.compiler.stmt.compile(stmt)

            if self.compiler.builder.block.is_terminated:
                break

            # Verification apres CHAQUE instruction du bloc try
            pending = self.compiler.builder.call(self.compiler.runtime_exception_pending, [])
            is_pending = self.compiler.builder.icmp_signed(
                '!=', pending, ir.Constant(ir.IntType(32), 0)
            )
            next_block = self.compiler.current_function.append_basic_block("try_continue")
            self.compiler.builder.cbranch(is_pending, catch_block, next_block)
            self.compiler.builder.position_at_start(next_block)

        if not self.compiler.builder.block.is_terminated:
            self.compiler.builder.branch(finally_block)

        self.compiler.builder.position_at_start(catch_block)
        if node.catch_var:
            msg = self.compiler.builder.call(self.compiler.runtime_exception_message, [])
            alloca = self.compiler.builder.alloca(ir.PointerType(ir.IntType(8)), name=node.catch_var)
            self.compiler.builder.store(msg, alloca)
            self.compiler.variables[node.catch_var] = alloca
            self.compiler.variable_types[node.catch_var] = ir.PointerType(ir.IntType(8))
            self.compiler.is_array[node.catch_var] = False

        for stmt in node.catch_body:
            if self.compiler.builder.block.is_terminated:
                break
            self.compiler.stmt.compile(stmt)
        if not self.compiler.builder.block.is_terminated:
            self.compiler.builder.branch(finally_block)

        self.compiler.builder.position_at_start(finally_block)
        for stmt in node.finally_body:
            if self.compiler.builder.block.is_terminated:
                break
            self.compiler.stmt.compile(stmt)
        if not self.compiler.builder.block.is_terminated:
            self.compiler.builder.branch(end_block)

        self.compiler.builder.position_at_start(end_block)
        self.compiler.builder.call(self.compiler.runtime_try_end, [])

    def compile_main(self, node):
        try:
            main_type = ir.FunctionType(
                ir.IntType(32),
                [ir.IntType(32), ir.PointerType(ir.PointerType(ir.IntType(8)))]
            )
            main_func = ir.Function(self.compiler.module, main_type, name="main")
            self.compiler.functions['main'] = main_func

            block = main_func.append_basic_block(name="entry")
            builder = ir.IRBuilder(block)

            self.compiler.builder = builder
            self.compiler.current_function = main_func
            self.compiler.variables = {}
            self.compiler.variable_types = {}
            self.compiler.is_array = {}
            self.compiler.array_sizes = {}
            self.compiler.array_length = {}
            self.compiler.array_values = {}
            self.compiler.function_args = {}
            self.compiler.object_class = {}
            self.compiler.loop_stack = []
            self.compiler.current_this_ptr = None

            if self.compiler.set_console_cp is not None:
                self.compiler.builder.call(self.compiler.set_console_cp, [ir.Constant(ir.IntType(32), 65001)])

            if isinstance(node, ProgramNode):
                for stmt in node.statements:
                    if isinstance(stmt, ClassNode):
                        self.compiler.oop.compile_class(stmt)

                for stmt in node.statements:
                    if not isinstance(stmt, FunctionNode) and not isinstance(stmt, ClassNode):
                        self.compiler.stmt.compile(stmt)

            if not self.compiler.builder.block.is_terminated:
                self.compiler.builder.ret(ir.Constant(ir.IntType(32), 0))

        except Exception as e:
            print(f"Error compiling main: {e}")
            if self.compiler.debug:
                import traceback
                traceback.print_exc()
            raise

    def compile_function(self, func_node):
        try:
            if self.compiler.debug:
                print(f"REGISTER FUNCTION: {func_node.name}")

            return_type, return_param_index = self._infer_function_return_kind(func_node)
            self.compiler.function_return_type[func_node.name] = return_type
            self.compiler.function_return_array_param[func_node.name] = return_param_index

            array_param_names = set(self._find_array_param_names(func_node))
            self.compiler.function_array_params[func_node.name] = [
                (p in array_param_names) for p in func_node.params
            ]

            param_types = []
            for param in func_node.params:
                if param in array_param_names:
                    param_types.append(ir.PointerType(ir.IntType(64)))
                    param_types.append(ir.IntType(64))
                else:
                    param_types.append(ir.IntType(64))

            func_type = ir.FunctionType(return_type, param_types)
            func = ir.Function(self.compiler.module, func_type, name=func_node.name)
            self.compiler.functions[func_node.name] = func

            block = func.append_basic_block(name="entry")
            builder = ir.IRBuilder(block)

            old_builder = self.compiler.builder
            old_function = self.compiler.current_function
            old_variables = self.compiler.variables.copy()
            old_types = self.compiler.variable_types.copy()
            old_is_array = self.compiler.is_array.copy()
            old_array_sizes = self.compiler.array_sizes.copy()
            old_array_length = self.compiler.array_length.copy()
            old_array_values = self.compiler.array_values.copy()

            self.compiler.builder = builder
            self.compiler.current_function = func
            self.compiler.variables = {}
            self.compiler.variable_types = {}
            self.compiler.is_array = {}
            self.compiler.array_sizes = {}
            self.compiler.array_length = {}
            self.compiler.array_values = {}
            self.compiler.function_args = {}
            self.compiler.loop_stack = []
            self.compiler.current_this_ptr = None

            llvm_args = list(func.args)
            arg_index = 0
            for param_name in func_node.params:
                if param_name in array_param_names:
                    ptr_arg = llvm_args[arg_index]; arg_index += 1
                    len_arg = llvm_args[arg_index]; arg_index += 1
                    ptr_arg.name = param_name
                    len_arg.name = f"{param_name}_len"
                    self.compiler.variables[param_name] = ptr_arg
                    self.compiler.is_array[param_name] = True
                    self.compiler.array_length[param_name] = len_arg
                    self.compiler.function_args[param_name] = ptr_arg
                else:
                    arg = llvm_args[arg_index]; arg_index += 1
                    arg.name = param_name
                    alloca = builder.alloca(ir.IntType(64), name=param_name)
                    builder.store(arg, alloca)
                    self.compiler.variables[param_name] = alloca
                    self.compiler.variable_types[param_name] = ir.IntType(64)
                    self.compiler.is_array[param_name] = False
                    self.compiler.function_args[param_name] = arg

            has_return = False
            for stmt in func_node.body:
                if isinstance(stmt, ReturnNode):
                    has_return = True
                self.compiler.stmt.compile(stmt)

            if not has_return and not self.compiler.builder.block.is_terminated:
                if return_type == ir.PointerType(ir.IntType(8)):
                    self.compiler.builder.ret(self.compiler.utils.create_string(""))
                elif return_type == ir.DoubleType():
                    self.compiler.builder.ret(ir.Constant(ir.DoubleType(), 0.0))
                elif return_type == ir.PointerType(ir.IntType(64)):
                    self.compiler.builder.ret(ir.Constant(return_type, None))
                elif isinstance(return_type, ir.PointerType) and isinstance(return_type.pointee, ir.ArrayType):
                    zero_array = ir.Constant(
                        return_type.pointee,
                        [ir.Constant(ir.IntType(64), 0)] * return_type.pointee.count
                    )
                    tmp_alloca = self.compiler.builder.alloca(return_type.pointee, name="empty_ret_array")
                    self.compiler.builder.store(zero_array, tmp_alloca)
                    self.compiler.builder.ret(tmp_alloca)
                else:
                    self.compiler.builder.ret(ir.Constant(ir.IntType(64), 0))

            self.compiler.builder = old_builder
            self.compiler.current_function = old_function
            self.compiler.variables = old_variables
            self.compiler.variable_types = old_types
            self.compiler.is_array = old_is_array
            self.compiler.array_sizes = old_array_sizes
            self.compiler.array_length = old_array_length
            self.compiler.array_values = old_array_values

        except Exception as e:
            print(f"Error compiling function {func_node.name}: {e}")
            if self.compiler.debug:
                import traceback
                traceback.print_exc()
            raise

    def _infer_function_return_kind(self, func_node):
        array_param_names = set(self._find_array_param_names(func_node))
        local_array_literal_lengths = {}
        returns_string = [False]
        returns_float = [False]
        returned_array_name = [None]
        returned_array_is_param = [False]

        def scan_for_local_arrays(stmts):
            if not isinstance(stmts, list):
                return
            for stmt in stmts:
                if stmt is None:
                    continue
                if isinstance(stmt, VariableNode) and isinstance(stmt.value, ArrayLiteralNode):
                    local_array_literal_lengths[stmt.name] = len(stmt.value.elements)
                for attr in ('then_body', 'else_body', 'body'):
                    if hasattr(stmt, attr):
                        scan_for_local_arrays(getattr(stmt, attr))

        scan_for_local_arrays(func_node.body)

        def check_expr(expr):
            if expr is None:
                return
            if isinstance(expr, StringNode):
                returns_string[0] = True
            elif isinstance(expr, NumberNode) and isinstance(expr.value, float):
                returns_float[0] = True
            elif isinstance(expr, IdentifierNode):
                if expr.name in local_array_literal_lengths:
                    returned_array_name[0] = expr.name
                    returned_array_is_param[0] = False
                elif expr.name in array_param_names:
                    if returned_array_name[0] is None:
                        returned_array_name[0] = expr.name
                        returned_array_is_param[0] = True
            elif isinstance(expr, BinOpNode):
                op_value = expr.op.value if hasattr(expr.op, 'value') else str(expr.op)
                if op_value in ["PLUS", "TokenType.PLUS", "+"]:
                    if isinstance(expr.left, StringNode) or isinstance(expr.right, StringNode):
                        returns_string[0] = True
                if op_value in ["SLASH", "TokenType.SLASH", "/"]:
                    returns_float[0] = True
                check_expr(expr.left)
                check_expr(expr.right)
            elif isinstance(expr, CallNode):
                fname = expr.name.name if hasattr(expr.name, 'name') else expr.name
                if fname in ('str', 'concat'):
                    returns_string[0] = True
                elif fname == 'float':
                    returns_float[0] = True

        def scan_returns(stmts):
            if not isinstance(stmts, list):
                return
            for stmt in stmts:
                if stmt is None:
                    continue
                if isinstance(stmt, ReturnNode):
                    check_expr(stmt.value)
                for attr in ('then_body', 'else_body', 'body'):
                    if hasattr(stmt, attr):
                        scan_returns(getattr(stmt, attr))

        scan_returns(func_node.body)

        if returned_array_name[0] is not None:
            if returned_array_is_param[0]:
                param_index = func_node.params.index(returned_array_name[0])
                result = (ir.PointerType(ir.IntType(64)), param_index)
            else:
                length = local_array_literal_lengths[returned_array_name[0]]
                result = (ir.PointerType(ir.ArrayType(ir.IntType(64), length)), None)
        elif returns_string[0]:
            result = (ir.PointerType(ir.IntType(8)), None)
        elif returns_float[0]:
            result = (ir.DoubleType(), None)
        else:
            result = (ir.IntType(64), None)

        return result

    def _find_array_param_names(self, func_node):
        param_names = set(func_node.params)
        found = set()

        def name_of(n):
            if hasattr(n, 'name'):
                return n.name
            return n if isinstance(n, str) else None

        def visit(n):
            if n is None:
                return
            if isinstance(n, list):
                for item in n:
                    visit(item)
                return
            if isinstance(n, ArrayAccessNode):
                nm = name_of(n.array_name)
                if nm in param_names:
                    found.add(nm)
                visit(n.index)
                if getattr(n, "is_assignment", False):
                    visit(n.value)
                return
            if isinstance(n, CallNode):
                fname = n.name.name if hasattr(n.name, 'name') else n.name
                for a in n.args:
                    if fname == 'len' and isinstance(a, IdentifierNode) and a.name in param_names:
                        found.add(a.name)
                    visit(a)
                return
            for attr in ('value', 'left', 'right', 'expr', 'condition',
                         'then_body', 'else_body', 'body', 'start', 'end'):
                if hasattr(n, attr):
                    visit(getattr(n, attr))

        visit(func_node.body)
        return [p for p in func_node.params if p in found]

    def optimize_module(self, module):
        try:
            import llvmlite.binding as llvm
            pm_builder = llvm.PassManagerBuilder()
            pm_builder.opt_level = 1 if self.compiler.optimize else 0
            pm_builder.size_level = 0

            pm = llvm.ModulePassManager()
            pm_builder.populate(pm)

            pm.run(module)
        except Exception as e:
            if self.compiler.debug:
                print(f"Optimization warning: {e}")