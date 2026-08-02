"""
Gestion du runtime LLVM - Initialise les fonctions du runtime C
"""

import llvmlite.ir as ir


class RuntimeHelper:
    """Initialise et gère les fonctions du runtime"""

    def __init__(self, compiler):
        self.compiler = compiler

    def init(self):
        """Initialise le runtime"""
        if self.compiler.runtime_initialized:
            return
        
        i8_ptr = ir.PointerType(ir.IntType(8))
        i64 = ir.IntType(64)
        i64_ptr = ir.PointerType(i64)
        void = ir.VoidType()
        
        # --- Classes et objets ---
        self.compiler.runtime_new_class = self.declare(
            'boubel_new_class', i8_ptr, [i8_ptr, i8_ptr]
        )
        self.compiler.runtime_new_object = self.declare(
            'boubel_new_object', i8_ptr, [i8_ptr, i64_ptr, i64]
        )
        self.compiler.runtime_get_field = self.declare(
            'boubel_object_get_field', i64, [i8_ptr, i8_ptr]
        )
        self.compiler.runtime_set_field = self.declare(
            'boubel_object_set_field', void, [i8_ptr, i8_ptr, i64]
        )
        self.compiler.runtime_get_field_string = self.declare(
            'boubel_object_get_field_string', i8_ptr, [i8_ptr, i8_ptr]
        )
        self.compiler.runtime_set_field_string = self.declare(
            'boubel_object_set_field_string', void, [i8_ptr, i8_ptr, i8_ptr]
        )
        self.compiler.runtime_call_method = self.declare(
            'boubel_object_call_method', i64, [i8_ptr, i8_ptr, i64_ptr, i64]
        )
        self.compiler.runtime_free_object = self.declare(
            'boubel_free_object', void, [i8_ptr]
        )
        
        # --- Gestion des exceptions ---
        self.compiler.runtime_try_start = self.declare(
            'boubel_try_start', ir.IntType(32), []
        )
        self.compiler.runtime_try_end = self.declare(
            'boubel_try_end', ir.IntType(32), []
        )
        self.compiler.runtime_throw = self.declare(
            'boubel_throw', void, [i8_ptr, i64]
        )
        self.compiler.runtime_get_exception = self.declare(
            'boubel_get_exception', i8_ptr, []
        )
        self.compiler.runtime_exception_message = self.declare(
            'boubel_exception_message', i8_ptr, []
        )
        self.compiler.runtime_exception_pending = self.declare(
            'boubel_exception_pending', ir.IntType(32), []
        )
        
        # --- Callbacks ---
        self.compiler.runtime_create_callback = self.declare(
            'boubel_create_callback', i8_ptr, [i8_ptr]
        )
        self.compiler.runtime_create_closure = self.declare(
            'boubel_create_closure', i8_ptr, [i8_ptr, i64_ptr, i64]
        )
        self.compiler.runtime_call_callback = self.declare(
            'boubel_call_callback', i64, [i8_ptr, i64_ptr, i64]
        )
        self.compiler.runtime_free_callback = self.declare(
            'boubel_free_callback', void, [i8_ptr]
        )
        
        # --- Classes dynamiques ---
        self.compiler.runtime_add_field = self.declare(
            'boubel_class_add_field', void, [i8_ptr, i8_ptr, i8_ptr]
        )
        self.compiler.runtime_add_method = self.declare(
            'boubel_class_add_method', void, [i8_ptr, i8_ptr, i8_ptr]
        )
        
        # --- Fichiers ---
        self.compiler.runtime_file_write = self.declare(
            'boubel_file_write', ir.IntType(32), [i8_ptr, i8_ptr]
        )
        self.compiler.runtime_file_read = self.declare(
            'boubel_file_read', i8_ptr, [i8_ptr]
        )
        self.compiler.runtime_value_to_string = self.declare(
            'boubel_value_to_string', i8_ptr, [i64, i8_ptr]
        )
        self.compiler.runtime_len = self.declare(
            'boubel_len', i64, [i8_ptr, i8_ptr]
        )
        self.compiler.runtime_typeof = self.declare(
            'boubel_typeof', i8_ptr, [i8_ptr]
        )
        
        # --- GC ---
        self.compiler.runtime_incref = self.declare(
            'boubel_incref', void, [i8_ptr]
        )
        self.compiler.runtime_decref = self.declare(
            'boubel_decref', void, [i8_ptr]
        )

        # ✅ NOUVEAU : fonctions de temps
        self.compiler.runtime_time_now = self.declare(
            'boubel_time_now', i64, []
        )
        self.compiler.runtime_sleep = self.declare(
            'boubel_sleep', void, [i64]
        )

        self.compiler.runtime_initialized = True

    def declare(self, name, return_type, param_types):
        """Déclare une fonction du runtime"""
        func_type = ir.FunctionType(return_type, param_types)
        return ir.Function(self.compiler.module, func_type, name=name)