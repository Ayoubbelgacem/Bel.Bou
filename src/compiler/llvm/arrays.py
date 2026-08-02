"""
Gestion des tableaux pour le compilateur LLVM
"""

import llvmlite.ir as ir


class ArraysHelper:
    """Gestion des tableaux"""

    def __init__(self, compiler):
        self.compiler = compiler

    def value_info(self, value):
        if self.is_pointer(value):
            return ir.Constant(ir.IntType(64), value.type.pointee.count), True
        dyn_len = self.get_dynamic_length(value)
        if dyn_len is not None:
            return dyn_len, False
        return None

    def is_pointer(self, value):
        return (hasattr(value, 'type') and hasattr(value.type, 'pointee')
                and isinstance(value.type.pointee, ir.ArrayType))

    def get_dynamic_length(self, value):
        return self.compiler._array_ptr_lengths.get(id(value))

    def array_ptr_to_string(self, array_ptr, count_val, is_fixed_array):
        buffer_size = 4096
        buffer_type = ir.ArrayType(ir.IntType(8), buffer_size)
        buffer_alloca = self.compiler.builder.alloca(buffer_type, name="array_str_buf")
        buffer_ptr = self.compiler.builder.bitcast(buffer_alloca, ir.PointerType(ir.IntType(8)))

        pos_alloca = self.compiler.builder.alloca(ir.IntType(64), name="array_str_pos")
        self.compiler.builder.store(ir.Constant(ir.IntType(64), 0), pos_alloca)

        idx_alloca = self.compiler.builder.alloca(ir.IntType(64), name="array_str_idx")
        self.compiler.builder.store(ir.Constant(ir.IntType(64), 0), idx_alloca)

        def _sprintf_and_advance(fmt_str, *extra_args):
            pos = self.compiler.builder.load(pos_alloca)
            dest_ptr = self.compiler.builder.gep(buffer_ptr, [pos], inbounds=True)
            fmt_ptr = self.compiler.utils.create_string(fmt_str)
            written = self.compiler.builder.call(self.compiler.sprintf, [dest_ptr, fmt_ptr, *extra_args])
            written64 = self.compiler.builder.sext(written, ir.IntType(64))
            new_pos = self.compiler.builder.add(pos, written64)
            self.compiler.builder.store(new_pos, pos_alloca)

        _sprintf_and_advance("[")

        check_block = self.compiler.current_function.append_basic_block("astr_check")
        body_block = self.compiler.current_function.append_basic_block("astr_body")
        comma_block = self.compiler.current_function.append_basic_block("astr_comma")
        after_comma_block = self.compiler.current_function.append_basic_block("astr_after_comma")
        end_block = self.compiler.current_function.append_basic_block("astr_end")

        self.compiler.builder.branch(check_block)

        self.compiler.builder.position_at_start(check_block)
        idx = self.compiler.builder.load(idx_alloca)
        cond = self.compiler.builder.icmp_signed("<", idx, count_val)
        self.compiler.builder.cbranch(cond, body_block, end_block)

        self.compiler.builder.position_at_start(body_block)
        idx = self.compiler.builder.load(idx_alloca)
        idx32 = self.compiler.builder.trunc(idx, ir.IntType(32))

        if is_fixed_array:
            elem_ptr = self.compiler.builder.gep(array_ptr, [ir.Constant(ir.IntType(32), 0), idx32], inbounds=True)
        else:
            elem_ptr = self.compiler.builder.gep(array_ptr, [idx32], inbounds=True)
        elem_val = self.compiler.builder.load(elem_ptr)

        elem_str = self.compiler.utils.convert_to_string(elem_val)
        _sprintf_and_advance("%s", elem_str)

        idx_plus1 = self.compiler.builder.add(idx, ir.Constant(ir.IntType(64), 1))
        has_more = self.compiler.builder.icmp_signed("<", idx_plus1, count_val)
        self.compiler.builder.store(idx_plus1, idx_alloca)
        self.compiler.builder.cbranch(has_more, comma_block, after_comma_block)

        self.compiler.builder.position_at_start(comma_block)
        _sprintf_and_advance(", ")
        self.compiler.builder.branch(after_comma_block)

        self.compiler.builder.position_at_start(after_comma_block)
        self.compiler.builder.branch(check_block)

        self.compiler.builder.position_at_start(end_block)
        _sprintf_and_advance("]")

        return buffer_ptr

    def print_array_runtime(self, array_ptr, count_val, is_fixed_array):
        open_str = self.compiler.utils.create_string("[")
        format_ptr = self.compiler.builder.bitcast(open_str, ir.PointerType(ir.IntType(8)))
        self.compiler.builder.call(self.compiler.printf, [format_ptr])

        idx_alloca = self.compiler.builder.alloca(ir.IntType(64), name="print_idx")
        self.compiler.builder.store(ir.Constant(ir.IntType(64), 0), idx_alloca)

        check_block = self.compiler.current_function.append_basic_block("parr_check")
        body_block = self.compiler.current_function.append_basic_block("parr_body")
        comma_block = self.compiler.current_function.append_basic_block("parr_comma")
        after_comma_block = self.compiler.current_function.append_basic_block("parr_after_comma")
        end_block = self.compiler.current_function.append_basic_block("parr_end")

        self.compiler.builder.branch(check_block)

        self.compiler.builder.position_at_start(check_block)
        idx = self.compiler.builder.load(idx_alloca)
        cond = self.compiler.builder.icmp_signed("<", idx, count_val)
        self.compiler.builder.cbranch(cond, body_block, end_block)

        self.compiler.builder.position_at_start(body_block)
        idx = self.compiler.builder.load(idx_alloca)
        idx32 = self.compiler.builder.trunc(idx, ir.IntType(32))
        if is_fixed_array:
            elem_ptr = self.compiler.builder.gep(array_ptr, [ir.Constant(ir.IntType(32), 0), idx32], inbounds=True)
        else:
            elem_ptr = self.compiler.builder.gep(array_ptr, [idx32], inbounds=True)
        elem_val = self.compiler.builder.load(elem_ptr)

        elem_str = self.compiler.utils.convert_to_string(elem_val)
        fmt_str = self.compiler.utils.create_string("%s")
        fmt_ptr = self.compiler.builder.bitcast(fmt_str, ir.PointerType(ir.IntType(8)))
        self.compiler.builder.call(self.compiler.printf, [fmt_ptr, elem_str])

        idx_plus1 = self.compiler.builder.add(idx, ir.Constant(ir.IntType(64), 1))
        has_more = self.compiler.builder.icmp_signed("<", idx_plus1, count_val)
        self.compiler.builder.store(idx_plus1, idx_alloca)
        self.compiler.builder.cbranch(has_more, comma_block, after_comma_block)

        self.compiler.builder.position_at_start(comma_block)
        comma_str = self.compiler.utils.create_string(", ")
        comma_ptr = self.compiler.builder.bitcast(comma_str, ir.PointerType(ir.IntType(8)))
        self.compiler.builder.call(self.compiler.printf, [comma_ptr])
        self.compiler.builder.branch(after_comma_block)

        self.compiler.builder.position_at_start(after_comma_block)
        self.compiler.builder.branch(check_block)

        self.compiler.builder.position_at_start(end_block)
        close_str = self.compiler.utils.create_string("]\n")
        close_ptr = self.compiler.builder.bitcast(close_str, ir.PointerType(ir.IntType(8)))
        self.compiler.builder.call(self.compiler.printf, [close_ptr])

    def compile_literal(self, node):
        num_elements = len(node.elements)
        if num_elements == 0:
            num_elements = 1
        
        array_type = ir.ArrayType(ir.IntType(64), num_elements)
        array_alloca = self.compiler.builder.alloca(array_type, name="array")
        
        zero = ir.Constant(ir.IntType(64), 0)
        for i in range(num_elements):
            idx = ir.Constant(ir.IntType(32), i)
            ptr = self.compiler.builder.gep(array_alloca, [ir.Constant(ir.IntType(32), 0), idx], inbounds=True)
            self.compiler.builder.store(zero, ptr)
        
        for i, elem in enumerate(node.elements):
            value = self.compiler.expr.compile(elem)
            
            if value is None:
                value = ir.Constant(ir.IntType(64), 0)
            
            if isinstance(value.type, ir.PointerType):
                if value.type.pointee == ir.IntType(64):
                    value = self.compiler.builder.load(value)
                else:
                    value = self.compiler.builder.ptrtoint(value, ir.IntType(64))
            elif value.type == ir.DoubleType():
                value = self.compiler.builder.fptosi(value, ir.IntType(64))
            elif str(value.type) == "i8*":
                value = self.compiler.builder.ptrtoint(value, ir.IntType(64))
            elif isinstance(value.type, ir.IntType) and value.type.width != 64:
                if value.type.width < 64:
                    value = self.compiler.builder.zext(value, ir.IntType(64))
                else:
                    value = self.compiler.builder.trunc(value, ir.IntType(64))
            
            value = self.compiler.types.coerce_to_i64(value)
            
            idx = ir.Constant(ir.IntType(32), i)
            ptr = self.compiler.builder.gep(array_alloca, [ir.Constant(ir.IntType(32), 0), idx], inbounds=True)
            self.compiler.builder.store(value, ptr)
        
        return array_alloca

    def compile_access(self, node):
        if hasattr(node.array_name, "name"):
            array_name = node.array_name.name
        else:
            array_name = str(node.array_name)

        if array_name not in self.compiler.variables:
            if self.compiler.debug:
                print(f"Array '{array_name}' not found")
            return ir.Constant(ir.IntType(64), 0)

        array_ptr = self.compiler.variables[array_name]

        if not hasattr(array_ptr.type, 'pointee'):
            if self.compiler.debug:
                print(f"ERROR: '{array_name}' has no pointee type")
            return ir.Constant(ir.IntType(64), 0)

        pointee = array_ptr.type.pointee

        if isinstance(pointee, ir.ArrayType):
            is_fixed_array = True
        elif pointee == ir.IntType(64):
            is_fixed_array = False
        else:
            if self.compiler.debug:
                print(f"WARNING: '{array_name}' is not an array (got {pointee}), returning 0")
            return ir.Constant(ir.IntType(64), 0)

        index = self.compiler.expr.compile(node.index)

        if index.type != ir.IntType(32):
            index = self.compiler.builder.trunc(index, ir.IntType(32))

        if is_fixed_array:
            element_ptr = self.compiler.builder.gep(array_ptr, [ir.Constant(ir.IntType(32), 0), index], inbounds=True)
        else:
            element_ptr = self.compiler.builder.gep(array_ptr, [index], inbounds=True)

        if getattr(node, "is_assignment", False):
            value = self.compiler.expr.compile(node.value)
            self.compiler.builder.store(value, element_ptr)
            return value

        return self.compiler.builder.load(element_ptr)