"""
Compilation des expressions pour le compilateur LLVM
"""

import llvmlite.ir as ir
import sys
import os

print("✅ [TRACE] expressions.py CHARGÉ (version finale)", file=sys.stderr)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from src.parser.ast import (
        NumberNode, StringNode, BooleanNode, NullNode, IdentifierNode,
        BinOpNode, CallNode, NewNode, MethodCallNode, PropertyNode,
        SuperNode, UnaryOpNode, ArrayLiteralNode, ArrayAccessNode,
        FileReadNode, FileWriteNode
    )
except ImportError:
    # Fallback
    class NumberNode: pass
    class StringNode: pass
    class BooleanNode: pass
    class NullNode: pass
    class IdentifierNode: pass
    class BinOpNode: pass
    class CallNode: pass
    class NewNode: pass
    class MethodCallNode: pass
    class PropertyNode: pass
    class SuperNode: pass
    class UnaryOpNode: pass
    class ArrayLiteralNode: pass
    class ArrayAccessNode: pass
    class FileReadNode: pass
    class FileWriteNode: pass


class ExpressionsHelper:
    """Compilation des expressions"""

    def __init__(self, compiler):
        self.compiler = compiler

    # ---------- Détection booléenne (corrigée) ----------
    def _is_boolean_expression(self, node):
        from src.parser.ast import BooleanNode, BinOpNode, CallNode, IdentifierNode

        if isinstance(node, BooleanNode):
            return True
        if isinstance(node, IdentifierNode):
            if node.name in self.compiler.bool_variables:
                return True
            var_type = self.compiler.variable_types.get(node.name)
            if var_type == ir.IntType(1) or str(var_type) == "i1":
                return True
            return False
        if isinstance(node, BinOpNode):
            op = node.op.value if hasattr(node.op, 'value') else str(node.op)
            if op in ("EQUAL_EQUAL", "==", "NOT_EQUAL", "!=",
                      "GREATER", ">", "LESS", "<",
                      "GREATER_EQUAL", ">=", "LESS_EQUAL", "<=",
                      "AND", "&&", "OR", "||"):
                return True
            return False
        if isinstance(node, CallNode):
            func_name = node.name.name if hasattr(node.name, 'name') else node.name
            if func_name.startswith('est_') or func_name in ('est_pair', 'est_impair'):
                return True
        return False

    # ---------- Compilation expression ----------
    def compile(self, node):
        try:
            if isinstance(node, NumberNode):
                if isinstance(node.value, float):
                    return ir.Constant(ir.DoubleType(), node.value)
                return ir.Constant(ir.IntType(64), node.value)

            elif isinstance(node, StringNode):
                return self.compiler.utils.create_string(node.value)

            elif isinstance(node, BooleanNode):
                return ir.Constant(ir.IntType(64), 1 if node.value else 0)

            elif isinstance(node, NullNode):
                return ir.Constant(ir.IntType(64), 0)

            elif isinstance(node, IdentifierNode):
                if node.name in self.compiler.variables:
                    if self.compiler.is_array.get(node.name, False):
                        return self.compiler.variables[node.name]
                    return self.compiler.builder.load(self.compiler.variables[node.name])
                elif node.name in self.compiler.function_args:
                    return self.compiler.function_args[node.name]
                elif node.name in self.compiler.functions:
                    func_ptr = self.compiler.functions[node.name]
                    return self.compiler.builder.ptrtoint(func_ptr, ir.IntType(64))
                elif node.name in self.compiler.object_class:
                    obj_ptr = self.compiler.variables.get(node.name)
                    if obj_ptr:
                        if isinstance(obj_ptr.type, ir.PointerType) and isinstance(obj_ptr.type.pointee, ir.PointerType):
                            return self.compiler.builder.load(obj_ptr)
                        return obj_ptr
                else:
                    if self.compiler.debug:
                        print(f"Warning: Variable '{node.name}' not found")
                    return ir.Constant(ir.IntType(64), 0)

            elif isinstance(node, BinOpNode):
                return self.compile_binop(node)

            elif isinstance(node, CallNode):
                return self.compiler.stmt.compile_call(node)

            elif isinstance(node, NewNode):
                return self.compiler.oop.compile_new(node)

            elif isinstance(node, MethodCallNode):
                return self.compiler.oop.compile_method_call(node)

            elif isinstance(node, PropertyNode):
                return self.compiler.oop.compile_property(node)

            elif isinstance(node, SuperNode):
                return self.compiler.oop.compile_super(node)

            elif isinstance(node, UnaryOpNode):
                value = self.compile(node.expr)
                op_value = node.op.value if hasattr(node.op, 'value') else str(node.op)
                if op_value in ["MINUS", "TokenType.MINUS", "-"]:
                    if value.type == ir.DoubleType():
                        return self.compiler.builder.fneg(value)
                    return self.compiler.builder.neg(value)
                elif op_value in ["NOT", "TokenType.NOT", "!"]:
                    is_zero = self.compiler.builder.icmp_signed('==', value, ir.Constant(ir.IntType(64), 0))
                    return self.compiler.builder.zext(is_zero, ir.IntType(64))
                return value

            elif isinstance(node, ArrayLiteralNode):
                return self.compiler.arrays.compile_literal(node)

            elif isinstance(node, ArrayAccessNode):
                return self.compiler.arrays.compile_access(node)

            elif isinstance(node, FileReadNode):
                return self.compiler.files.compile_file_read(node)

            elif isinstance(node, FileWriteNode):
                return self.compiler.files.compile_file_write(node)

            else:
                return ir.Constant(ir.IntType(64), 0)
        except Exception as e:
            print(f"Error compiling expression {type(node).__name__}: {e}")
            if self.compiler.debug:
                import traceback
                traceback.print_exc()
            return ir.Constant(ir.IntType(64), 0)

    # ---------- BinOp corrigé ----------
    def compile_binop(self, node):
        left = self.compile(node.left)
        right = self.compile(node.right)

        op_value = node.op.value if hasattr(node.op, 'value') else str(node.op)

        if op_value in ["PLUS", "TokenType.PLUS", "+"]:
            # Détection booléenne pour conversion en chaîne (seulement si le côté est booléen)
            left_is_bool = self._is_boolean_expression(node.left)
            right_is_bool = self._is_boolean_expression(node.right)

            if left_is_bool:
                left = self.compiler.utils.bool_to_string(left)
            if right_is_bool:
                right = self.compiler.utils.bool_to_string(right)

            # Conversion des tableaux en chaîne
            left_array_info = self.compiler.arrays.value_info(left)
            if left_array_info is not None:
                count_val, is_fixed = left_array_info
                left = self.compiler.arrays.array_ptr_to_string(left, count_val, is_fixed)
            
            right_array_info = self.compiler.arrays.value_info(right)
            if right_array_info is not None:
                count_val, is_fixed = right_array_info
                right = self.compiler.arrays.array_ptr_to_string(right, count_val, is_fixed)

            left_is_string = isinstance(node.left, StringNode) or str(left.type) == "i8*"
            right_is_string = isinstance(node.right, StringNode) or str(right.type) == "i8*"

            if left_is_string or right_is_string:
                return self.compiler.utils.concat_strings(left, right)

            # Addition numérique
            left, right, is_float = self.compiler.types.promote_for_binop(left, right)
            if is_float:
                return self.compiler.builder.fadd(left, right)
            return self.compiler.builder.add(left, right)

        elif op_value in ["MINUS", "TokenType.MINUS", "-"]:
            left, right, is_float = self.compiler.types.promote_for_binop(left, right)
            if is_float:
                return self.compiler.builder.fsub(left, right)
            return self.compiler.builder.sub(left, right)

        elif op_value in ["STAR", "TokenType.STAR", "*"]:
            left, right, is_float = self.compiler.types.promote_for_binop(left, right)
            if is_float:
                return self.compiler.builder.fmul(left, right)
            return self.compiler.builder.mul(left, right)

        # ✅ DIVISION : toujours convertir en double
        elif op_value in ["SLASH", "TokenType.SLASH", "/"]:
            print("🔍 [TRACE] Division SLASH détectée, conversion en double", file=sys.stderr)
            left = self.compiler.types.coerce_to_double(left)
            right = self.compiler.types.coerce_to_double(right)
            
            zero = ir.Constant(ir.DoubleType(), 0.0)
            is_zero = self.compiler.builder.fcmp_ordered('==', right, zero)
            
            divide_block = self.compiler.current_function.append_basic_block("divide_ok")
            error_block = self.compiler.current_function.append_basic_block("divide_error")
            end_block = self.compiler.current_function.append_basic_block("divide_end")
            
            result_alloca = self.compiler.builder.alloca(ir.DoubleType(), name="div_result")
            
            self.compiler.builder.cbranch(is_zero, error_block, divide_block)
            
            self.compiler.builder.position_at_start(divide_block)
            div_result = self.compiler.builder.fdiv(left, right)
            self.compiler.builder.store(div_result, result_alloca)
            self.compiler.builder.branch(end_block)
            
            self.compiler.builder.position_at_start(error_block)
            error_msg = self.compiler.utils.create_string("Division by zero")
            self.compiler.builder.call(self.compiler.runtime_throw, [error_msg, ir.Constant(ir.IntType(64), 0)])
            self.compiler.builder.store(zero, result_alloca)
            self.compiler.builder.branch(end_block)
            
            self.compiler.builder.position_at_start(end_block)
            return self.compiler.builder.load(result_alloca)  # double

        elif op_value in ["MOD", "TokenType.MOD", "%"]:
            if self.compiler.types.is_float_type(left.type):
                left = self.compiler.builder.fptosi(left, ir.IntType(64))
            if self.compiler.types.is_float_type(right.type):
                right = self.compiler.builder.fptosi(right, ir.IntType(64))
            zero = ir.Constant(ir.IntType(64), 0)
            one = ir.Constant(ir.IntType(64), 1)
            
            is_zero = self.compiler.builder.icmp_signed('==', right, zero)
            
            mod_block = self.compiler.current_function.append_basic_block("mod_ok")
            error_block = self.compiler.current_function.append_basic_block("mod_error")
            end_block = self.compiler.current_function.append_basic_block("mod_end")
            
            result_alloca = self.compiler.builder.alloca(ir.IntType(64), name="mod_result")
            self.compiler.builder.cbranch(is_zero, error_block, mod_block)
            
            self.compiler.builder.position_at_start(mod_block)
            mod_result = self.compiler.builder.srem(left, right)
            self.compiler.builder.store(mod_result, result_alloca)
            self.compiler.builder.branch(end_block)
            
            self.compiler.builder.position_at_start(error_block)
            error_msg = self.compiler.utils.create_string("Modulo by zero")
            self.compiler.builder.call(self.compiler.runtime_throw, [error_msg, ir.Constant(ir.IntType(64), 0)])
            self.compiler.builder.store(zero, result_alloca)
            self.compiler.builder.branch(end_block)
            
            self.compiler.builder.position_at_start(end_block)
            return self.compiler.builder.load(result_alloca)

        elif op_value in ["EQUAL_EQUAL", "TokenType.EQUAL_EQUAL", "==",
                           "NOT_EQUAL", "TokenType.NOT_EQUAL", "!=",
                           "GREATER", "TokenType.GREATER", ">",
                           "LESS", "TokenType.LESS", "<",
                           "GREATER_EQUAL", "TokenType.GREATER_EQUAL", ">=",
                           "LESS_EQUAL", "TokenType.LESS_EQUAL", "<="]:
            left, right, is_float = self.compiler.types.promote_for_binop(left, right)

            op_map = {
                "EQUAL_EQUAL": "==", "TokenType.EQUAL_EQUAL": "==", "==": "==",
                "NOT_EQUAL": "!=", "TokenType.NOT_EQUAL": "!=", "!=": "!=",
                "GREATER": ">", "TokenType.GREATER": ">", ">": ">",
                "LESS": "<", "TokenType.LESS": "<", "<": "<",
                "GREATER_EQUAL": ">=", "TokenType.GREATER_EQUAL": ">=", ">=": ">=",
                "LESS_EQUAL": "<=", "TokenType.LESS_EQUAL": "<=", "<=": "<=",
            }
            cmp_op = op_map[op_value]

            if is_float:
                cmp = self.compiler.builder.fcmp_ordered(cmp_op, left, right)
            else:
                cmp = self.compiler.builder.icmp_signed(cmp_op, left, right)
            return self.compiler.builder.zext(cmp, ir.IntType(64))

        elif op_value in ["AND", "TokenType.AND"]:
            left_bool = self.compiler.builder.icmp_signed('!=', self.compiler.types.coerce_to_i64(left), ir.Constant(ir.IntType(64), 0))
            right_bool = self.compiler.builder.icmp_signed('!=', self.compiler.types.coerce_to_i64(right), ir.Constant(ir.IntType(64), 0))
            result = self.compiler.builder.and_(left_bool, right_bool)
            return self.compiler.builder.zext(result, ir.IntType(64))

        elif op_value in ["OR", "TokenType.OR"]:
            left_bool = self.compiler.builder.icmp_signed('!=', self.compiler.types.coerce_to_i64(left), ir.Constant(ir.IntType(64), 0))
            right_bool = self.compiler.builder.icmp_signed('!=', self.compiler.types.coerce_to_i64(right), ir.Constant(ir.IntType(64), 0))
            result = self.compiler.builder.or_(left_bool, right_bool)
            return self.compiler.builder.zext(result, ir.IntType(64))

        else:
            left, right, is_float = self.compiler.types.promote_for_binop(left, right)
            if is_float:
                return self.compiler.builder.fadd(left, right)
            return self.compiler.builder.add(left, right)