"""
Compilation des statements pour le compilateur LLVM
"""

import llvmlite.ir as ir
import sys
import os

print("✅ [TRACE] statements.py CHARGÉ (version finale)", file=sys.stderr)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from src.parser.ast import (
        VariableNode, AssignmentNode, PrintNode, InputNode, IfNode,
        ForNode, WhileNode, ReturnNode, CallNode, FunctionNode,
        ClassNode, NewNode, MethodCallNode, PropertyNode, TryNode,
        SuperNode, BreakNode, ContinueNode, FileWriteNode, FileReadNode,
        ArrayLiteralNode, ArrayAccessNode, BooleanNode, IdentifierNode,
        BinOpNode, StringNode, ImportNode
    )
except ImportError:
    # Fallback
    class VariableNode: pass
    class AssignmentNode: pass
    class PrintNode: pass
    class InputNode: pass
    class IfNode: pass
    class ForNode: pass
    class WhileNode: pass
    class ReturnNode: pass
    class CallNode: pass
    class FunctionNode: pass
    class ClassNode: pass
    class NewNode: pass
    class MethodCallNode: pass
    class PropertyNode: pass
    class TryNode: pass
    class SuperNode: pass
    class BreakNode: pass
    class ContinueNode: pass
    class FileWriteNode: pass
    class FileReadNode: pass
    class ArrayLiteralNode: pass
    class ArrayAccessNode: pass
    class BooleanNode: pass
    class IdentifierNode: pass
    class BinOpNode: pass
    class StringNode: pass
    class ImportNode: pass


class StatementsHelper:
    """Compilation des statements"""

    def __init__(self, compiler):
        self.compiler = compiler

    # ---------- Détection booléenne ----------
    def _is_boolean_expression(self, node):
        """Retourne True si le nœud est une valeur booléenne (comparaison, logique, variable booléenne, appel est_*)."""
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

    # ---------- Compilation principale ----------
    def compile(self, node):
        if node is None:
            return

        if hasattr(self.compiler.builder, 'block') and self.compiler.builder.block.is_terminated:
            return

        if self.compiler.debug:
            print(f"  Compiling statement: {type(node).__name__}")

        try:
            if isinstance(node, VariableNode):
                self.compile_variable(node)
            elif isinstance(node, AssignmentNode):
                self.compile_assignment(node)
            elif isinstance(node, PrintNode):
                self.compile_print(node)
            elif isinstance(node, InputNode):
                self.compile_input(node)
            elif isinstance(node, IfNode):
                self.compiler.control.compile_if(node)
            elif isinstance(node, ForNode):
                self.compiler.control.compile_for(node)
            elif isinstance(node, WhileNode):
                self.compiler.control.compile_while(node)
            elif isinstance(node, ReturnNode):
                self.compiler.control.compile_return(node)
            elif isinstance(node, CallNode):
                self.compile_call(node)
            elif isinstance(node, FunctionNode):
                pass
            elif isinstance(node, ClassNode):
                pass
            elif isinstance(node, NewNode):
                self.compiler.oop.compile_new(node)
            elif isinstance(node, MethodCallNode):
                self.compiler.oop.compile_method_call(node)
            elif isinstance(node, PropertyNode):
                self.compiler.oop.compile_property(node)
            elif isinstance(node, TryNode):
                self.compiler.control.compile_try(node)
            elif isinstance(node, SuperNode):
                self.compiler.oop.compile_super(node)
            elif isinstance(node, BreakNode):
                self.compiler.control.compile_break()
            elif isinstance(node, ContinueNode):
                self.compiler.control.compile_continue()
            elif isinstance(node, FileWriteNode):
                self.compiler.files.compile_file_write(node)
            elif isinstance(node, FileReadNode):
                self.compiler.files.compile_file_read(node)
            elif isinstance(node, ArrayLiteralNode):
                self.compiler.arrays.compile_literal(node)
            elif isinstance(node, ArrayAccessNode):
                self.compiler.arrays.compile_access(node)
            elif isinstance(node, ImportNode):
                if self.compiler.debug:
                    print(f"📦 Import statement for module '{node.module_name}' handled at top level.")
                pass
            else:
                result = self.compiler.expr.compile(node)
                if result is not None:
                    pass
        except Exception as e:
            print(f"Error compiling statement {type(node).__name__}: {e}")
            if self.compiler.debug:
                import traceback
                traceback.print_exc()
            raise

    # ---------- Variables ----------
    def compile_variable(self, node):
        # Cas d'un nouvel objet (NewNode)
        if isinstance(node.value, NewNode):
            value = self.compiler.oop.compile_new(node.value)
            alloca = self.compiler.builder.alloca(ir.PointerType(ir.IntType(8)), name=node.name)
            self.compiler.builder.store(value, alloca)
            self.compiler.variables[node.name] = alloca
            self.compiler.variable_types[node.name] = ir.PointerType(ir.IntType(8))
            self.compiler.is_array[node.name] = False
            if hasattr(node.value, 'class_name'):
                self.compiler.object_class[node.name] = node.value.class_name
            # ✅ GC : incrémenter la référence car la variable la possède
            self.compiler.builder.call(self.compiler.runtime_incref, [value])
            return

        # Cas d'un tableau
        if isinstance(node.value, ArrayLiteralNode):
            value = self.compiler.arrays.compile_literal(node.value)
            self.compiler.variables[node.name] = value
            self.compiler.is_array[node.name] = True
            self.compiler.array_sizes[node.name] = len(node.value.elements)
            self.compiler.array_length[node.name] = ir.Constant(ir.IntType(64), len(node.value.elements))
            self.compiler.array_values[node.name] = value
            return

        value = self.compiler.expr.compile(node.value)

        # Cas d'une chaîne
        if isinstance(node.value, StringNode):
            alloca = self.compiler.builder.alloca(ir.PointerType(ir.IntType(8)), name=node.name)
            value = self.compiler.builder.bitcast(value, ir.PointerType(ir.IntType(8)))
            self.compiler.builder.store(value, alloca)
            self.compiler.variables[node.name] = alloca
            self.compiler.variable_types[node.name] = ir.PointerType(ir.IntType(8))
            self.compiler.is_array[node.name] = False
            return

        elif node.type_name == 'string':
            alloca = self.compiler.builder.alloca(ir.PointerType(ir.IntType(8)), name=node.name)
            value = self.compiler.builder.bitcast(value, ir.PointerType(ir.IntType(8)))
            self.compiler.builder.store(value, alloca)
            self.compiler.variables[node.name] = alloca
            self.compiler.variable_types[node.name] = ir.PointerType(ir.IntType(8))
            self.compiler.is_array[node.name] = False
            return

        if isinstance(value.type, ir.PointerType) and value.type.pointee == ir.IntType(8):
            alloca = self.compiler.builder.alloca(ir.PointerType(ir.IntType(8)), name=node.name)
            self.compiler.builder.store(value, alloca)
            self.compiler.variables[node.name] = alloca
            self.compiler.variable_types[node.name] = ir.PointerType(ir.IntType(8))
            self.compiler.is_array[node.name] = False
            return

        # Cas d'un tableau (renvoyé par une expression)
        if not isinstance(node.value, ArrayLiteralNode):
            array_info = self.compiler.arrays.value_info(value)
            if array_info is not None:
                count_val, is_fixed = array_info
                self.compiler.variables[node.name] = value
                self.compiler.is_array[node.name] = True
                self.compiler.array_length[node.name] = count_val
                if is_fixed:
                    self.compiler.array_sizes[node.name] = value.type.pointee.count
                self.compiler.array_values[node.name] = value
                return

        is_real_type = node.type_name in ('real', 'float')

        if is_real_type or value.type == ir.DoubleType():
            value = self.compiler.types.coerce_to_double(value)
            alloca = self.compiler.builder.alloca(ir.DoubleType(), name=node.name)
            self.compiler.builder.store(value, alloca)
            self.compiler.variables[node.name] = alloca
            self.compiler.variable_types[node.name] = ir.DoubleType()
            self.compiler.is_array[node.name] = False
            return

        else:
            if str(value.type) == "i8*":
                alloca = self.compiler.builder.alloca(ir.PointerType(ir.IntType(8)), name=node.name)
                self.compiler.variable_types[node.name] = ir.PointerType(ir.IntType(8))
            else:
                alloca = self.compiler.builder.alloca(ir.IntType(64), name=node.name)
                self.compiler.variable_types[node.name] = ir.IntType(64)
                if isinstance(node.value, BooleanNode) or node.type_name == 'bool':
                    self.compiler.bool_variables.add(node.name)

            self.compiler.builder.store(value, alloca)
            self.compiler.variables[node.name] = alloca
            self.compiler.is_array[node.name] = False

    # ---------- Assignation ----------
    def compile_assignment(self, node):
        # Si on assigne un nouvel objet
        if isinstance(node.value, NewNode):
            value = self.compiler.oop.compile_new(node.value)
            alloca = self.compiler.builder.alloca(ir.PointerType(ir.IntType(8)), name=node.name)
            
            # Si la variable existait déjà et contenait un objet, décrémenter
            if node.name in self.compiler.variables:
                old_ptr = self.compiler.builder.load(self.compiler.variables[node.name])
                if node.name in self.compiler.object_class:
                    self.compiler.builder.call(self.compiler.runtime_decref, [old_ptr])
                    # Supprimer de object_class (sera réajouté si nécessaire)
                    # On le retire maintenant, on le remettra après stockage
                    del self.compiler.object_class[node.name]
            
            self.compiler.builder.store(value, alloca)
            self.compiler.variables[node.name] = alloca
            self.compiler.variable_types[node.name] = ir.PointerType(ir.IntType(8))
            self.compiler.is_array[node.name] = False
            if hasattr(node.value, 'class_name'):
                self.compiler.object_class[node.name] = node.value.class_name
            # ✅ Nouvelle référence
            self.compiler.builder.call(self.compiler.runtime_incref, [value])
            return

        value = self.compiler.expr.compile(node.value)

        if node.name in self.compiler.variables:
            if self.compiler.is_array.get(node.name, False):
                if self.compiler.debug:
                    print(f"ERROR: Cannot assign normal value to array '{node.name}'")
                return

            existing_alloca = self.compiler.variables[node.name]
            
            # Si l'ancienne valeur était un objet, décrémenter
            if node.name in self.compiler.object_class:
                old_ptr = self.compiler.builder.load(existing_alloca)
                self.compiler.builder.call(self.compiler.runtime_decref, [old_ptr])
                del self.compiler.object_class[node.name]   # On la retire temporairement

            if hasattr(existing_alloca.type, 'pointee'):
                expected_type = existing_alloca.type.pointee
                if expected_type == ir.PointerType(ir.IntType(8)):
                    if value.type == ir.IntType(64):
                        value = self.compiler.builder.inttoptr(value, ir.PointerType(ir.IntType(8)))
                    elif str(value.type) != "i8*":
                        value = self.compiler.utils.convert_to_string(value)
                        value = self.compiler.builder.bitcast(value, ir.PointerType(ir.IntType(8)))
                elif expected_type == ir.DoubleType() and value.type != ir.DoubleType():
                    value = self.compiler.types.coerce_to_double(value)
                elif expected_type == ir.IntType(64) and value.type != ir.IntType(64):
                    value = self.compiler.types.coerce_to_i64(value)
                elif str(expected_type) == "i8*" and str(value.type) != "i8*":
                    value = self.compiler.utils.convert_to_string(value)

            self.compiler.builder.store(value, existing_alloca)
            
            # Si la nouvelle valeur est un objet, incref et ajouter à object_class
            if isinstance(node.value, NewNode):
                self.compiler.object_class[node.name] = node.value.class_name
                self.compiler.builder.call(self.compiler.runtime_incref, [value])
            # Si c'est une chaîne, on ne fait rien (car chaîne = i8* mais pas objet)
            # Si c'est autre chose, on s'assure qu'on a retiré object_class (déjà fait)
        else:
            # Nouvelle variable
            array_info = self.compiler.arrays.value_info(value)
            if array_info is not None:
                count_val, is_fixed = array_info
                self.compiler.variables[node.name] = value
                self.compiler.is_array[node.name] = True
                self.compiler.array_length[node.name] = count_val
                if is_fixed:
                    self.compiler.array_sizes[node.name] = value.type.pointee.count
                self.compiler.array_values[node.name] = value
                return

            if str(value.type) == "i8*":
                alloca = self.compiler.builder.alloca(ir.PointerType(ir.IntType(8)), name=node.name)
                self.compiler.variable_types[node.name] = ir.PointerType(ir.IntType(8))
                if isinstance(node.value, NewNode):
                    self.compiler.object_class[node.name] = node.value.class_name
                    self.compiler.builder.call(self.compiler.runtime_incref, [value])
            elif value.type == ir.DoubleType():
                alloca = self.compiler.builder.alloca(ir.DoubleType(), name=node.name)
                self.compiler.variable_types[node.name] = ir.DoubleType()
            else:
                alloca = self.compiler.builder.alloca(ir.IntType(64), name=node.name)
                self.compiler.variable_types[node.name] = ir.IntType(64)

            self.compiler.builder.store(value, alloca)
            self.compiler.variables[node.name] = alloca
            self.compiler.is_array[node.name] = False

    # ---------- Print ----------
    def compile_print(self, node):
        print(f"🔍 [TRACE] compile_print appelé, node = {node}", file=sys.stderr)

        # Tableau
        if isinstance(node.value, IdentifierNode) and self.compiler.is_array.get(node.value.name, False):
            name = node.value.name
            array_ptr = self.compiler.variables[name]
            pointee = array_ptr.type.pointee
            is_fixed_array = isinstance(pointee, ir.ArrayType)

            if name in self.compiler.array_length:
                count_val = self.compiler.array_length[name]
            elif name in self.compiler.array_sizes:
                count_val = ir.Constant(ir.IntType(64), self.compiler.array_sizes[name])
            elif is_fixed_array:
                count_val = ir.Constant(ir.IntType(64), pointee.count)
            else:
                count_val = ir.Constant(ir.IntType(64), 0)

            self.compiler.arrays.print_array_runtime(array_ptr, count_val, is_fixed_array)
            return

        value = self.compiler.expr.compile(node.value)

        # Booléen
        if self._is_boolean_expression(node.value):
            print(f"🔍 [TRACE] Expression booléenne détectée, conversion en chaîne", file=sys.stderr)
            bool_str = self.compiler.utils.bool_to_string(value)
            fmt = self.compiler.utils.create_string("%s\n")
            fmt_ptr = self.compiler.builder.bitcast(fmt, ir.PointerType(ir.IntType(8)))
            self.compiler.builder.call(self.compiler.printf, [fmt_ptr, bool_str])
            return

        # Appels de fonctions qui retournent des chaînes
        if isinstance(node.value, CallNode):
            func_name = node.value.name.name if hasattr(node.value.name, 'name') else node.value.name
            if func_name in ('iqra_mlf', 'str', 'concat', 'type', 'input'):
                fmt = self.compiler.utils.create_string("%s\n")
                fmt_ptr = self.compiler.builder.bitcast(fmt, ir.PointerType(ir.IntType(8)))
                self.compiler.builder.call(self.compiler.printf, [fmt_ptr, value])
                return

        # Pointeur de chaîne
        if str(value.type) == "i8*":
            fmt = self.compiler.utils.create_string("%s\n")
            fmt_ptr = self.compiler.builder.bitcast(fmt, ir.PointerType(ir.IntType(8)))
            self.compiler.builder.call(self.compiler.printf, [fmt_ptr, value])
            return

        # Flottants
        if value.type == ir.DoubleType():
            fmt = self.compiler.utils.create_string("%.g\n")
            fmt_ptr = self.compiler.builder.bitcast(fmt, ir.PointerType(ir.IntType(8)))
            self.compiler.builder.call(self.compiler.printf, [fmt_ptr, value])
            return

        # Tableaux retournés par des fonctions
        if isinstance(node.value, CallNode):
            array_info = self.compiler.arrays.value_info(value)
            if array_info is not None:
                count_val, is_fixed = array_info
                self.compiler.arrays.print_array_runtime(value, count_val, is_fixed)
                return

        # Entiers par défaut
        fmt = self.compiler.utils.create_string("%lld\n")
        fmt_ptr = self.compiler.builder.bitcast(fmt, ir.PointerType(ir.IntType(8)))
        self.compiler.builder.call(self.compiler.printf, [fmt_ptr, value])

    # ---------- Input ----------
    def compile_input(self, node):
        temp_var = self.compiler.builder.alloca(ir.IntType(64), name="input_temp")
        fmt = self.compiler.utils.create_string("%lld")
        fmt_ptr = self.compiler.builder.bitcast(fmt, ir.PointerType(ir.IntType(8)))
        self.compiler.builder.call(self.compiler.scanf, [fmt_ptr, temp_var])
        return self.compiler.builder.load(temp_var)

    # ---------- Call ----------
    def compile_call(self, node):
        func_name = node.name.name if hasattr(node.name, 'name') else node.name

        if self.compiler.debug:
            print(f"  Calling function: {func_name}")

        # Built-in functions
        if func_name not in self.compiler.functions and func_name in self.compiler.builtin_functions:
            if func_name == 'len' and node.args:
                arg0 = node.args[0]
                name = arg0.name if hasattr(arg0, 'name') else None
                if name is not None and name in self.compiler.array_length:
                    return self.compiler.array_length[name]
            args = [self.compiler.expr.compile(arg) for arg in node.args]
            result = self.compiler.builtin_functions[func_name](args)
            if isinstance(result.type, ir.PointerType) and result.type.pointee == ir.IntType(64):
                result = self.compiler.builder.load(result)
            return result

        # User functions
        if func_name in self.compiler.functions:
            func = self.compiler.functions[func_name]
            is_array_flags = self.compiler.function_array_params.get(func_name, [])
            returned_param_index = self.compiler.function_return_array_param.get(func_name)
            args = []
            returned_length_val = None

            for i, arg in enumerate(node.args):
                if i < len(is_array_flags) and is_array_flags[i]:
                    ptr, length_val = self._get_array_ptr_and_length(arg)
                    args.append(ptr)
                    args.append(length_val)
                    if returned_param_index is not None and i == returned_param_index:
                        returned_length_val = length_val
                else:
                    arg_value = self.compiler.expr.compile(arg)
                    args.append(self.compiler.types.coerce_to_i64(arg_value))

            result = self.compiler.builder.call(func, args)
            if returned_length_val is not None:
                self.compiler._array_ptr_lengths[id(result)] = returned_length_val
            return result

        # Callback via variable
        if isinstance(func_name, str) and func_name in self.compiler.variables and not self.compiler.is_array.get(func_name, False):
            callee_i64 = self.compiler.builder.load(self.compiler.variables[func_name])
            arg_vals = []
            for a in node.args:
                v = self.compiler.expr.compile(a)
                arg_vals.append(self.compiler.types.coerce_to_i64(v))
            fn_type = ir.FunctionType(ir.IntType(64), [ir.IntType(64)] * len(arg_vals))
            fn_ptr_type = ir.PointerType(fn_type)
            fn_ptr = self.compiler.builder.inttoptr(callee_i64, fn_ptr_type)
            return self.compiler.builder.call(fn_ptr, arg_vals)

        if self.compiler.debug:
            print(f"Warning: Unknown function '{func_name}', returning 0")
        return ir.Constant(ir.IntType(64), 0)

    # ---------- Helpers ----------
    def _get_array_ptr_and_length(self, arg_node):
        value = self.compiler.expr.compile(arg_node)
        name = arg_node.name if hasattr(arg_node, 'name') else None

        if name is not None and name in self.compiler.array_length:
            length_val = self.compiler.array_length[name]
        elif hasattr(value, 'type') and hasattr(value.type, 'pointee') and isinstance(value.type.pointee, ir.ArrayType):
            length_val = ir.Constant(ir.IntType(64), value.type.pointee.count)
        else:
            length_val = ir.Constant(ir.IntType(64), 0)

        ptr_type = ir.PointerType(ir.IntType(64))
        if value.type != ptr_type:
            ptr = self.compiler.builder.bitcast(value, ptr_type)
        else:
            ptr = value

        return ptr, length_val