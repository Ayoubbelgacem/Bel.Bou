"""
Opérations sur fichiers pour le compilateur LLVM
"""

import llvmlite.ir as ir


class FilesHelper:
    """Gestion des opérations sur fichiers"""

    def __init__(self, compiler):
        self.compiler = compiler

    def compile_file_write(self, node):
        filename = self.compiler.expr.compile(node.filename)
        content = self.compiler.expr.compile(node.content)
        return self._do_file_write(filename, content)

    def compile_file_read(self, node):
        filename = self.compiler.expr.compile(node.filename)
        return self._do_file_read(filename)

    def call_iqra_mlf(self, args):
        if not args:
            return self.compiler.utils.create_string("")
        return self._do_file_read(args[0])

    def call_ikteb_fi_mlf(self, args):
        if len(args) < 2:
            return ir.Constant(ir.IntType(64), 0)
        return self._do_file_write(args[0], args[1])

    def _do_file_write(self, filename, content):
        if str(filename.type) != "i8*":
            filename = self.compiler.utils.convert_to_string(filename)
        if str(content.type) != "i8*":
            content = self.compiler.utils.convert_to_string(content)
        
        result = self.compiler.builder.call(self.compiler.runtime_file_write, [filename, content])
        
        success = self.compiler.builder.icmp_signed('!=', result, ir.Constant(ir.IntType(32), 0))
        
        ok_block = self.compiler.current_function.append_basic_block("file_write_ok")
        error_block = self.compiler.current_function.append_basic_block("file_write_error")
        end_block = self.compiler.current_function.append_basic_block("file_write_end")
        
        self.compiler.builder.cbranch(success, ok_block, error_block)
        
        self.compiler.builder.position_at_start(ok_block)
        msg_ok = self.compiler.utils.create_string("✅ Fichier écrit avec succès!\n")
        self.compiler.builder.call(self.compiler.printf, [self.compiler.builder.bitcast(msg_ok, ir.PointerType(ir.IntType(8)))])
        self.compiler.builder.branch(end_block)
        
        self.compiler.builder.position_at_start(error_block)
        msg_error = self.compiler.utils.create_string("❌ Erreur: Impossible d'écrire le fichier!\n")
        self.compiler.builder.call(self.compiler.printf, [self.compiler.builder.bitcast(msg_error, ir.PointerType(ir.IntType(8)))])
        self.compiler.builder.branch(end_block)
        
        self.compiler.builder.position_at_start(end_block)
        return ir.Constant(ir.IntType(64), 0)

    def _do_file_read(self, filename):
        if str(filename.type) != "i8*":
            filename = self.compiler.utils.convert_to_string(filename)
        
        result = self.compiler.builder.call(self.compiler.runtime_file_read, [filename])
        
        is_valid = self.compiler.builder.icmp_signed('!=', result, ir.Constant(ir.PointerType(ir.IntType(8)), None))
        
        ok_block = self.compiler.current_function.append_basic_block("file_read_ok")
        error_block = self.compiler.current_function.append_basic_block("file_read_error")
        end_block = self.compiler.current_function.append_basic_block("file_read_end")
        
        result_alloca = self.compiler.builder.alloca(ir.PointerType(ir.IntType(8)), name="file_content")
        
        self.compiler.builder.cbranch(is_valid, ok_block, error_block)
        
        self.compiler.builder.position_at_start(ok_block)
        self.compiler.builder.store(result, result_alloca)
        self.compiler.builder.branch(end_block)
        
        self.compiler.builder.position_at_start(error_block)
        error_msg = self.compiler.utils.create_string("❌ Erreur: Impossible de lire le fichier!\n")
        self.compiler.builder.call(self.compiler.printf, [self.compiler.builder.bitcast(error_msg, ir.PointerType(ir.IntType(8)))])
        empty_str = self.compiler.utils.create_string("")
        self.compiler.builder.store(empty_str, result_alloca)
        self.compiler.builder.branch(end_block)
        
        self.compiler.builder.position_at_start(end_block)
        return self.compiler.builder.load(result_alloca)