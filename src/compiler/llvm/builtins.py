"""
Fonctions built-in pour le compilateur LLVM
Support : len, str, int, float, type, print, input, sum, max, min, abs, concat,
          time_now, sleep, to_json
"""

import llvmlite.ir as ir


class BuiltinsHelper:
    """Fonctions built-in.

    IMPORTANT : `args` reçu par chaque méthode call_xxx est déjà une liste
    de valeurs LLVM IR compilées (voir StatementsHelper.compile_call :
    `args = [self.compiler.expr.compile(arg) for arg in node.args]` est fait
    AVANT d'appeler ces méthodes). Il ne faut donc JAMAIS refaire
    `self.compiler.expr.compile(args[0])` ici -- args[0] n'est pas un nœud
    AST, c'est déjà une ir.Value. Refaire compile() dessus ne correspond à
    aucun type de nœud reconnu et retombe silencieusement sur
    ir.Constant(ir.IntType(64), 0), ce qui a causé la régression Phase 17
    (len()/str()/int() renvoyant toujours 0 ou 0-like).
    """

    def __init__(self, compiler):
        self.compiler = compiler

    # ===== len =====
    def call_len(self, args):
        if not args:
            return ir.Constant(ir.IntType(64), 0)

        value = args[0]

        if hasattr(value, 'type') and hasattr(value.type, 'pointee'):
            pointee = value.type.pointee
            if isinstance(pointee, ir.ArrayType):
                return ir.Constant(ir.IntType(64), pointee.count)

        if str(value.type) == "i8*":
            return self.compiler.builder.call(self.compiler.strlen, [value])

        if isinstance(value.type, ir.PointerType) and value.type.pointee == ir.IntType(64):
            len_ptr = self.compiler.builder.gep(value, [ir.Constant(ir.IntType(32), 0)])
            return self.compiler.builder.load(len_ptr)

        return ir.Constant(ir.IntType(64), 0)

    # ===== str =====
    def call_str(self, args):
        if not args:
            return self.compiler.utils.create_string("")
        value = args[0]

        if isinstance(value.type, ir.IntType):
            buffer_size = 256
            buffer_type = ir.ArrayType(ir.IntType(8), buffer_size)
            buffer_alloca = self.compiler.builder.alloca(buffer_type, name="str_buf")
            buffer_ptr = self.compiler.builder.bitcast(buffer_alloca, ir.PointerType(ir.IntType(8)))

            if value.type.width < 64:
                value = self.compiler.builder.zext(value, ir.IntType(64))
            elif value.type.width > 64:
                value = self.compiler.builder.trunc(value, ir.IntType(64))

            format_str = self.compiler.utils.create_string("%lld")
            format_ptr = self.compiler.builder.bitcast(format_str, ir.PointerType(ir.IntType(8)))
            self.compiler.builder.call(self.compiler.sprintf, [buffer_ptr, format_ptr, value])
            return buffer_ptr

        return self.compiler.utils.convert_to_string(value)

    # ===== int =====
    def call_int(self, args):
        if not args:
            return ir.Constant(ir.IntType(64), 0)

        value = args[0]

        if value.type == ir.IntType(64):
            return value

        if isinstance(value.type, ir.IntType):
            if value.type.width < 64:
                return self.compiler.builder.zext(value, ir.IntType(64))
            elif value.type.width > 64:
                return self.compiler.builder.trunc(value, ir.IntType(64))
            return value

        if isinstance(value.type, ir.PointerType):
            if str(value.type) == "i8*":
                atoi_result = self.compiler.builder.call(self.compiler.atoi, [value])
                return self.compiler.builder.sext(atoi_result, ir.IntType(64))
            return self.compiler.builder.ptrtoint(value, ir.IntType(64))

        if value.type == ir.DoubleType():
            return self.compiler.builder.fptosi(value, ir.IntType(64))

        return ir.Constant(ir.IntType(64), 0)

    # ===== float =====
    def call_float(self, args):
        if not args:
            return ir.Constant(ir.DoubleType(), 0.0)
        value = args[0]
        if value.type == ir.DoubleType():
            return value
        if isinstance(value.type, ir.PointerType):
            return self.compiler.builder.call(self.compiler.atof, [value])
        return self.compiler.types.coerce_to_double(value)

    # ===== type =====
    def call_type(self, args):
        if not args:
            return self.compiler.utils.create_string("unknown")

        value = args[0]

        if self.compiler.arrays.value_info(value) is not None:
            return self.compiler.utils.create_string("array")

        if value.type == ir.DoubleType():
            return self.compiler.utils.create_string("float")
        elif str(value.type) == "i8*":
            return self.compiler.utils.create_string("str")
        elif isinstance(value.type, ir.IntType):
            if value.type.width == 64:
                if isinstance(value, ir.Constant):
                    if value.constant in (0, 1):
                        return self.compiler.utils.create_string("bool")
            return self.compiler.utils.create_string("int")
        else:
            return self.compiler.utils.create_string("unknown")

    # ===== print =====
    def call_print(self, args):
        for arg in args:
            if str(arg.type) == "i8*":
                format_str = self.compiler.utils.create_string("%s\n")
            elif arg.type == ir.DoubleType():
                format_str = self.compiler.utils.create_string("%g\n")
            else:
                format_str = self.compiler.utils.create_string("%lld\n")
            format_ptr = self.compiler.builder.bitcast(format_str, ir.PointerType(ir.IntType(8)))
            self.compiler.builder.call(self.compiler.printf, [format_ptr, arg])
        return ir.Constant(ir.IntType(64), 0)

    # ===== input =====
    def call_input(self, args):
        temp_var = self.compiler.builder.alloca(ir.IntType(64), name="input_temp")
        format_str = self.compiler.utils.create_string("%lld")
        format_ptr = self.compiler.builder.bitcast(format_str, ir.PointerType(ir.IntType(8)))
        self.compiler.builder.call(self.compiler.scanf, [format_ptr, temp_var])
        return self.compiler.builder.load(temp_var)

    # ===== sum (avec vrai parcours de tableau) =====
    def call_sum(self, args):
        if not args:
            return ir.Constant(ir.IntType(64), 0)
        arg = args[0]
        if isinstance(arg.type, ir.PointerType):
            length = None
            is_fixed_array = False
            for name, var in self.compiler.variables.items():
                if var == arg and self.compiler.is_array.get(name, False):
                    if name in self.compiler.array_length:
                        length = self.compiler.array_length[name]
                    elif name in self.compiler.array_sizes:
                        length = ir.Constant(ir.IntType(64), self.compiler.array_sizes[name])
                    break
            if hasattr(arg, 'type') and hasattr(arg.type, 'pointee'):
                if isinstance(arg.type.pointee, ir.ArrayType):
                    is_fixed_array = True
                    if length is None:
                        length = ir.Constant(ir.IntType(64), arg.type.pointee.count)
            if length is not None:
                return self._sum_array(arg, length, is_fixed_array)
            return ir.Constant(ir.IntType(64), 0)
        result = args[0]
        for arg in args[1:]:
            result = self.compiler.builder.add(result, arg)
        return result

    def _sum_array(self, array_ptr, length, is_fixed_array=False):
        loop_block = self.compiler.current_function.append_basic_block("sum_loop")
        body_block = self.compiler.current_function.append_basic_block("sum_body")
        end_block = self.compiler.current_function.append_basic_block("sum_end")
        result_alloca = self.compiler.builder.alloca(ir.IntType(64), name="sum_result")
        self.compiler.builder.store(ir.Constant(ir.IntType(64), 0), result_alloca)
        idx_alloca = self.compiler.builder.alloca(ir.IntType(64), name="sum_idx")
        self.compiler.builder.store(ir.Constant(ir.IntType(64), 0), idx_alloca)
        self.compiler.builder.branch(loop_block)
        self.compiler.builder.position_at_start(loop_block)
        idx = self.compiler.builder.load(idx_alloca)
        cond = self.compiler.builder.icmp_signed('<', idx, length)
        self.compiler.builder.cbranch(cond, body_block, end_block)
        self.compiler.builder.position_at_start(body_block)
        idx = self.compiler.builder.load(idx_alloca)
        idx32 = self.compiler.builder.trunc(idx, ir.IntType(32))
        if is_fixed_array:
            elem_ptr = self.compiler.builder.gep(array_ptr, [ir.Constant(ir.IntType(32), 0), idx32], inbounds=True)
        else:
            elem_ptr = self.compiler.builder.gep(array_ptr, [idx32], inbounds=True)
        elem_val = self.compiler.builder.load(elem_ptr)
        current_sum = self.compiler.builder.load(result_alloca)
        new_sum = self.compiler.builder.add(current_sum, elem_val)
        self.compiler.builder.store(new_sum, result_alloca)
        new_idx = self.compiler.builder.add(idx, ir.Constant(ir.IntType(64), 1))
        self.compiler.builder.store(new_idx, idx_alloca)
        self.compiler.builder.branch(loop_block)
        self.compiler.builder.position_at_start(end_block)
        result = self.compiler.builder.load(result_alloca)
        return result

    # ===== max (avec vrai parcours de tableau) =====
    def call_max(self, args):
        if not args:
            return ir.Constant(ir.IntType(64), 0)
        arg = args[0]
        if isinstance(arg.type, ir.PointerType):
            length = None
            is_fixed_array = False
            for name, var in self.compiler.variables.items():
                if var == arg and self.compiler.is_array.get(name, False):
                    if name in self.compiler.array_length:
                        length = self.compiler.array_length[name]
                    elif name in self.compiler.array_sizes:
                        length = ir.Constant(ir.IntType(64), self.compiler.array_sizes[name])
                    break
            if hasattr(arg, 'type') and hasattr(arg.type, 'pointee'):
                if isinstance(arg.type.pointee, ir.ArrayType):
                    is_fixed_array = True
                    if length is None:
                        length = ir.Constant(ir.IntType(64), arg.type.pointee.count)
            if length is not None:
                return self._max_array(arg, length, is_fixed_array)
            return ir.Constant(ir.IntType(64), 0)
        result = args[0]
        for arg in args[1:]:
            cmp = self.compiler.builder.icmp_signed('>', arg, result)
            result = self.compiler.builder.select(cmp, arg, result)
        return result

    def _max_array(self, array_ptr, length, is_fixed_array=False):
        loop_block = self.compiler.current_function.append_basic_block("max_loop")
        body_block = self.compiler.current_function.append_basic_block("max_body")
        end_block = self.compiler.current_function.append_basic_block("max_end")
        if is_fixed_array:
            first_ptr = self.compiler.builder.gep(array_ptr, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), 0)], inbounds=True)
        else:
            first_ptr = self.compiler.builder.gep(array_ptr, [ir.Constant(ir.IntType(32), 0)], inbounds=True)
        first_val = self.compiler.builder.load(first_ptr)
        max_alloca = self.compiler.builder.alloca(ir.IntType(64), name="max_val")
        self.compiler.builder.store(first_val, max_alloca)
        idx_alloca = self.compiler.builder.alloca(ir.IntType(64), name="max_idx")
        self.compiler.builder.store(ir.Constant(ir.IntType(64), 1), idx_alloca)
        self.compiler.builder.branch(loop_block)
        self.compiler.builder.position_at_start(loop_block)
        idx = self.compiler.builder.load(idx_alloca)
        cond = self.compiler.builder.icmp_signed('<', idx, length)
        self.compiler.builder.cbranch(cond, body_block, end_block)
        self.compiler.builder.position_at_start(body_block)
        idx = self.compiler.builder.load(idx_alloca)
        idx32 = self.compiler.builder.trunc(idx, ir.IntType(32))
        if is_fixed_array:
            elem_ptr = self.compiler.builder.gep(array_ptr, [ir.Constant(ir.IntType(32), 0), idx32], inbounds=True)
        else:
            elem_ptr = self.compiler.builder.gep(array_ptr, [idx32], inbounds=True)
        elem_val = self.compiler.builder.load(elem_ptr)
        current_max = self.compiler.builder.load(max_alloca)
        is_greater = self.compiler.builder.icmp_signed('>', elem_val, current_max)
        new_max = self.compiler.builder.select(is_greater, elem_val, current_max)
        self.compiler.builder.store(new_max, max_alloca)
        new_idx = self.compiler.builder.add(idx, ir.Constant(ir.IntType(64), 1))
        self.compiler.builder.store(new_idx, idx_alloca)
        self.compiler.builder.branch(loop_block)
        self.compiler.builder.position_at_start(end_block)
        result = self.compiler.builder.load(max_alloca)
        return result

    # ===== min (avec vrai parcours de tableau) =====
    def call_min(self, args):
        if not args:
            return ir.Constant(ir.IntType(64), 0)
        arg = args[0]
        if isinstance(arg.type, ir.PointerType):
            length = None
            is_fixed_array = False
            for name, var in self.compiler.variables.items():
                if var == arg and self.compiler.is_array.get(name, False):
                    if name in self.compiler.array_length:
                        length = self.compiler.array_length[name]
                    elif name in self.compiler.array_sizes:
                        length = ir.Constant(ir.IntType(64), self.compiler.array_sizes[name])
                    break
            if hasattr(arg, 'type') and hasattr(arg.type, 'pointee'):
                if isinstance(arg.type.pointee, ir.ArrayType):
                    is_fixed_array = True
                    if length is None:
                        length = ir.Constant(ir.IntType(64), arg.type.pointee.count)
            if length is not None:
                return self._min_array(arg, length, is_fixed_array)
            return ir.Constant(ir.IntType(64), 0)
        result = args[0]
        for arg in args[1:]:
            cmp = self.compiler.builder.icmp_signed('<', arg, result)
            result = self.compiler.builder.select(cmp, arg, result)
        return result

    def _min_array(self, array_ptr, length, is_fixed_array=False):
        loop_block = self.compiler.current_function.append_basic_block("min_loop")
        body_block = self.compiler.current_function.append_basic_block("min_body")
        end_block = self.compiler.current_function.append_basic_block("min_end")
        if is_fixed_array:
            first_ptr = self.compiler.builder.gep(array_ptr, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), 0)], inbounds=True)
        else:
            first_ptr = self.compiler.builder.gep(array_ptr, [ir.Constant(ir.IntType(32), 0)], inbounds=True)
        first_val = self.compiler.builder.load(first_ptr)
        min_alloca = self.compiler.builder.alloca(ir.IntType(64), name="min_val")
        self.compiler.builder.store(first_val, min_alloca)
        idx_alloca = self.compiler.builder.alloca(ir.IntType(64), name="min_idx")
        self.compiler.builder.store(ir.Constant(ir.IntType(64), 1), idx_alloca)
        self.compiler.builder.branch(loop_block)
        self.compiler.builder.position_at_start(loop_block)
        idx = self.compiler.builder.load(idx_alloca)
        cond = self.compiler.builder.icmp_signed('<', idx, length)
        self.compiler.builder.cbranch(cond, body_block, end_block)
        self.compiler.builder.position_at_start(body_block)
        idx = self.compiler.builder.load(idx_alloca)
        idx32 = self.compiler.builder.trunc(idx, ir.IntType(32))
        if is_fixed_array:
            elem_ptr = self.compiler.builder.gep(array_ptr, [ir.Constant(ir.IntType(32), 0), idx32], inbounds=True)
        else:
            elem_ptr = self.compiler.builder.gep(array_ptr, [idx32], inbounds=True)
        elem_val = self.compiler.builder.load(elem_ptr)
        current_min = self.compiler.builder.load(min_alloca)
        is_less = self.compiler.builder.icmp_signed('<', elem_val, current_min)
        new_min = self.compiler.builder.select(is_less, elem_val, current_min)
        self.compiler.builder.store(new_min, min_alloca)
        new_idx = self.compiler.builder.add(idx, ir.Constant(ir.IntType(64), 1))
        self.compiler.builder.store(new_idx, idx_alloca)
        self.compiler.builder.branch(loop_block)
        self.compiler.builder.position_at_start(end_block)
        result = self.compiler.builder.load(min_alloca)
        return result

    # ===== abs =====
    def call_abs(self, args):
        if not args:
            return ir.Constant(ir.IntType(64), 0)
        value = args[0]
        is_negative = self.compiler.builder.icmp_signed('<', value, ir.Constant(ir.IntType(64), 0))
        neg_value = self.compiler.builder.neg(value)
        return self.compiler.builder.select(is_negative, neg_value, value)

    # ===== concat =====
    def call_concat(self, args):
        if len(args) != 2:
            return self.compiler.utils.create_string("")
        return self.compiler.utils.concat_strings(args[0], args[1])

    # ============================================================
    # PHASE 17 : time_now, sleep, to_json
    # ============================================================

    def call_time_now(self, args):
        """Appelle boubel_time_now() déclaré dans le runtime."""
        return self.compiler.builder.call(self.compiler.runtime_time_now, [])

    def call_sleep(self, args):
        """Appelle boubel_sleep(seconds). `args[0]` est déjà une valeur IR
        (voir note en tête de fichier) -- on la coerce juste en i64."""
        if not args:
            return ir.Constant(ir.IntType(64), 0)
        seconds_i64 = self.compiler.types.coerce_to_i64(args[0])
        self.compiler.builder.call(self.compiler.runtime_sleep, [seconds_i64])
        return ir.Constant(ir.IntType(64), 0)

    def call_to_json(self, args):
        """Renvoie une chaîne 'null' (implémentation minimale à enrichir plus
        tard -- convertir un tableau/valeur en JSON nécessite un vrai
        parcours typé, non trivial avec le typage i64 opaque de ce backend)."""
        return self.compiler.utils.create_string("null")