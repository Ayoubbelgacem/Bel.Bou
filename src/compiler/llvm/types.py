"""
Gestion des types pour le compilateur LLVM
"""

import llvmlite.ir as ir


class TypesHelper:
    """Gestion des types et promotion"""

    def __init__(self, compiler):
        self.compiler = compiler

    def is_float_type(self, llvm_type):
        """Vérifie si le type est un float"""
        return llvm_type == ir.DoubleType()

    def promote_for_binop(self, left, right):
        """Promotion des types pour les opérations binaires"""
        left_is_float = self.is_float_type(left.type)
        right_is_float = self.is_float_type(right.type)
        if not left_is_float and not right_is_float:
            return left, right, False
        if not left_is_float and isinstance(left.type, ir.IntType):
            left = self.compiler.builder.sitofp(left, ir.DoubleType())
        if not right_is_float and isinstance(right.type, ir.IntType):
            right = self.compiler.builder.sitofp(right, ir.DoubleType())
        return left, right, True

    def coerce_to_double(self, value):
        """Convertit une valeur en double"""
        if value.type == ir.DoubleType():
            return value
        if isinstance(value.type, ir.IntType):
            return self.compiler.builder.sitofp(value, ir.DoubleType())
        return value

    def coerce_to_i64(self, value):
        """Convertit une valeur en i64"""
        t = value.type

        if t == ir.IntType(64):
            return value

        if isinstance(t, ir.PointerType):
            if str(t) == "i8*":
                return self.compiler.builder.ptrtoint(value, ir.IntType(64))
            return self.compiler.builder.ptrtoint(value, ir.IntType(64))

        if isinstance(t, ir.IntType):
            if t.width < 64:
                return self.compiler.builder.zext(value, ir.IntType(64))
            elif t.width > 64:
                return self.compiler.builder.trunc(value, ir.IntType(64))
            return value

        if t == ir.DoubleType():
            return self.compiler.builder.fptosi(value, ir.IntType(64))

        return value