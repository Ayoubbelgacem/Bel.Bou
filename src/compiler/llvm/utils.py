"""
Fonctions utilitaires pour le compilateur LLVM
"""

import llvmlite.ir as ir
import os


class UtilsHelper:
    """Fonctions utilitaires"""

    def __init__(self, compiler):
        self.compiler = compiler

    def create_string(self, string):
        """Crée une constante de chaîne"""
        if string.startswith('"') and string.endswith('"'):
            string = string[1:-1]

        if string in self.compiler.string_constants:
            global_var = self.compiler.string_constants[string]
            return self.compiler.builder.bitcast(global_var, ir.PointerType(ir.IntType(8)))

        bytes_data = string.encode('utf-8') + b'\x00'
        str_type = ir.ArrayType(ir.IntType(8), len(bytes_data))
        str_constant = ir.Constant(str_type, list(bytes_data))

        var_name = f"str_{len(self.compiler.string_constants)}"
        global_var = ir.GlobalVariable(self.compiler.module, str_type, name=var_name)
        global_var.initializer = str_constant
        global_var.global_constant = True
        global_var.align = 1

        self.compiler.string_constants[string] = global_var

        return self.compiler.builder.bitcast(global_var, ir.PointerType(ir.IntType(8)))

    def concat_strings(self, left, right):
        """Concatène deux chaînes"""
        buffer_size = 4096
        buffer_type = ir.ArrayType(ir.IntType(8), buffer_size)
        buffer_alloca = self.compiler.builder.alloca(buffer_type, name="concat_buf")
        buffer_ptr = self.compiler.builder.bitcast(buffer_alloca, ir.PointerType(ir.IntType(8)))

        left_str = self.convert_to_string(left)
        right_str = self.convert_to_string(right)

        format_str = self.create_string("%s%s")
        format_ptr = self.compiler.builder.bitcast(format_str, ir.PointerType(ir.IntType(8)))
        self.compiler.builder.call(self.compiler.sprintf, [buffer_ptr, format_ptr, left_str, right_str])

        return buffer_ptr

    def convert_to_string(self, value):
        """Convertit une valeur en chaîne"""
        array_info = self.compiler.arrays.value_info(value)
        if array_info is not None:
            count_val, is_fixed = array_info
            return self.compiler.arrays.array_ptr_to_string(value, count_val, is_fixed)

        if value.type == ir.DoubleType():
            buffer_size = 256
            buffer_type = ir.ArrayType(ir.IntType(8), buffer_size)
            buffer_alloca = self.compiler.builder.alloca(buffer_type, name="str_buf_f")
            buffer_ptr = self.compiler.builder.bitcast(buffer_alloca, ir.PointerType(ir.IntType(8)))
            format_str = self.create_string("%g")
            format_ptr = self.compiler.builder.bitcast(format_str, ir.PointerType(ir.IntType(8)))
            self.compiler.builder.call(self.compiler.sprintf, [buffer_ptr, format_ptr, value])
            return buffer_ptr

        if str(value.type) == "i8*":
            return value

        if isinstance(value.type, ir.PointerType):
            if value.type.pointee == ir.IntType(64):
                value = self.compiler.builder.load(value)
            else:
                buffer_size = 256
                buffer_type = ir.ArrayType(ir.IntType(8), buffer_size)
                buffer_alloca = self.compiler.builder.alloca(buffer_type, name="str_buf")
                buffer_ptr = self.compiler.builder.bitcast(buffer_alloca, ir.PointerType(ir.IntType(8)))

                addr = self.compiler.builder.ptrtoint(value, ir.IntType(64))
                format_str = self.create_string("%lld")
                format_ptr = self.compiler.builder.bitcast(format_str, ir.PointerType(ir.IntType(8)))
                self.compiler.builder.call(self.compiler.sprintf, [buffer_ptr, format_ptr, addr])
                return buffer_ptr

        if isinstance(value.type, ir.IntType):
            buffer_size = 256
            buffer_type = ir.ArrayType(ir.IntType(8), buffer_size)
            buffer_alloca = self.compiler.builder.alloca(buffer_type, name="str_buf")
            buffer_ptr = self.compiler.builder.bitcast(buffer_alloca, ir.PointerType(ir.IntType(8)))

            if value.type.width < 64:
                value = self.compiler.builder.zext(value, ir.IntType(64))
            elif value.type.width > 64:
                value = self.compiler.builder.trunc(value, ir.IntType(64))

            format_str = self.create_string("%lld")
            format_ptr = self.compiler.builder.bitcast(format_str, ir.PointerType(ir.IntType(8)))
            self.compiler.builder.call(self.compiler.sprintf, [buffer_ptr, format_ptr, value])
            return buffer_ptr

        return self.create_string("<valeur>")

    def bool_to_string(self, value):
        """Convertit une valeur booléenne en 'True' ou 'False'"""
        value64 = self.compiler.types.coerce_to_i64(value)
        cond = self.compiler.builder.icmp_signed('!=', value64, ir.Constant(ir.IntType(64), 0))
        true_str = self.create_string("True")
        false_str = self.create_string("False")
        return self.compiler.builder.select(cond, true_str, false_str)

    def declare_external_functions(self):
        """Déclare les fonctions externes (printf, etc.)"""
        module = self.compiler.module
        
        printf_type = ir.FunctionType(ir.IntType(32), [ir.PointerType(ir.IntType(8))], var_arg=True)
        self.compiler.printf = ir.Function(module, printf_type, name="printf")
        
        puts_type = ir.FunctionType(ir.IntType(32), [ir.PointerType(ir.IntType(8))])
        self.compiler.puts = ir.Function(module, puts_type, name="puts")
        
        strlen_type = ir.FunctionType(ir.IntType(64), [ir.PointerType(ir.IntType(8))])
        self.compiler.strlen = ir.Function(module, strlen_type, name="strlen")
        
        atoi_type = ir.FunctionType(ir.IntType(32), [ir.PointerType(ir.IntType(8))])
        self.compiler.atoi = ir.Function(module, atoi_type, name="atoi")
        
        atof_type = ir.FunctionType(ir.DoubleType(), [ir.PointerType(ir.IntType(8))])
        self.compiler.atof = ir.Function(module, atof_type, name="atof")
        
        scanf_type = ir.FunctionType(ir.IntType(32), [ir.PointerType(ir.IntType(8))], var_arg=True)
        self.compiler.scanf = ir.Function(module, scanf_type, name="scanf")
        
        sprintf_type = ir.FunctionType(ir.IntType(32), [ir.PointerType(ir.IntType(8)), ir.PointerType(ir.IntType(8))], var_arg=True)
        self.compiler.sprintf = ir.Function(module, sprintf_type, name="sprintf")

        self.compiler.set_console_cp = None
        if os.name == 'nt':
            set_console_cp_type = ir.FunctionType(ir.IntType(32), [ir.IntType(32)])
            self.compiler.set_console_cp = ir.Function(module, set_console_cp_type, name="SetConsoleOutputCP")