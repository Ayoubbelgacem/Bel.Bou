"""
Programmation Orientée Objet pour le compilateur LLVM
"""

import llvmlite.ir as ir


class OOPHelper:
    """Gestion des classes, objets, méthodes, héritage"""

    def __init__(self, compiler):
        self.compiler = compiler

    def register_class(self, node):
        class_name = node.name
        self.compiler.class_methods[class_name] = {
            'node': node,
            'methods': node.methods,
            'properties': node.properties,
            'parent': node.parent
        }
        if self.compiler.debug:
            print(f"Registered class: {class_name}")

    def compile_class(self, node):
        from ...parser.ast import StringNode, NumberNode, BooleanNode
        
        class_name = node.name
        
        if self.compiler.debug:
            print(f"Compiling class: {class_name}")
        
        if self.compiler.builder is None:
            return None
        
        class_name_ptr = self.compiler.utils.create_string(class_name)
        parent_ptr = ir.Constant(ir.PointerType(ir.IntType(8)), None)
        
        if node.parent and node.parent in self.compiler.classes:
            parent_ptr = self.compiler.classes[node.parent]
        
        class_obj = self.compiler.builder.call(self.compiler.runtime_new_class, [class_name_ptr, parent_ptr])
        self.compiler.classes[class_name] = class_obj
        
        for prop_name, prop_value in node.properties.items():
            prop_name_ptr = self.compiler.utils.create_string(prop_name)
            
            if isinstance(prop_value, StringNode):
                prop_type_ptr = self.compiler.utils.create_string("string")
            elif isinstance(prop_value, NumberNode) and isinstance(prop_value.value, float):
                prop_type_ptr = self.compiler.utils.create_string("float")
            elif isinstance(prop_value, BooleanNode):
                prop_type_ptr = self.compiler.utils.create_string("bool")
            else:
                prop_type_ptr = self.compiler.utils.create_string("int")
            
            self.compiler.builder.call(self.compiler.runtime_add_field, [class_obj, prop_name_ptr, prop_type_ptr])
        
        compiled_methods = []
        for method in node.methods:
            func = self.compile_method(class_name, method)
            if func:
                compiled_methods.append((method.name, func))
        
        for method_name, func in compiled_methods:
            method_name_ptr = self.compiler.utils.create_string(method_name)
            func_ptr = self.compiler.builder.bitcast(func, ir.PointerType(ir.IntType(8)))
            self.compiler.builder.call(
                self.compiler.runtime_add_method,
                [class_obj, method_name_ptr, func_ptr]
            )
        
        return class_obj

    def compile_method(self, class_name, method_node):
        from ...parser.ast import ReturnNode
        
        method_name = method_node.name
        full_name = f"{class_name}_{method_name}"
        
        if self.compiler.debug:
            print(f"Compiling method: {full_name}")
        
        if self.compiler.builder is None:
            return None
        
        param_types = [
            ir.PointerType(ir.IntType(8)),
            ir.PointerType(ir.IntType(64)),
            ir.IntType(64)
        ]
        
        return_type = ir.IntType(64)
        func_type = ir.FunctionType(return_type, param_types)
        func = ir.Function(self.compiler.module, func_type, name=full_name)
        self.compiler.functions[full_name] = func
        
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
        old_object_class = self.compiler.object_class.copy()
        old_current_this = self.compiler.current_this_ptr
        
        self.compiler.builder = builder
        self.compiler.current_function = func
        self.compiler.variables = {}
        self.compiler.variable_types = {}
        self.compiler.is_array = {}
        self.compiler.array_sizes = {}
        self.compiler.array_length = {}
        self.compiler.array_values = {}
        self.compiler.function_args = {}
        self.compiler.object_class = {}
        self.compiler.loop_stack = []
        
        llvm_args = list(func.args)
        this_arg = llvm_args[0]
        args_arg = llvm_args[1]
        argc_arg = llvm_args[2]
        
        this_arg.name = "hetha"
        args_arg.name = "args"
        argc_arg.name = "argc"
        
        self.compiler.current_this_ptr = this_arg
        self.compiler.variables["hetha"] = this_arg
        self.compiler.object_class["hetha"] = class_name
        
        for i, param_name in enumerate(method_node.params):
            idx = ir.Constant(ir.IntType(32), i)
            arg_ptr = self.compiler.builder.gep(args_arg, [idx], inbounds=True)
            arg_val = self.compiler.builder.load(arg_ptr)
            
            alloca = builder.alloca(ir.IntType(64), name=param_name)
            builder.store(arg_val, alloca)
            self.compiler.variables[param_name] = alloca
            self.compiler.variable_types[param_name] = ir.IntType(64)
            self.compiler.is_array[param_name] = False
            self.compiler.function_args[param_name] = arg_val
        
        has_return = False
        for stmt in method_node.body:
            if isinstance(stmt, ReturnNode):
                has_return = True
            self.compiler.stmt.compile(stmt)
        
        if not has_return and not self.compiler.builder.block.is_terminated:
            self.compiler.builder.ret(ir.Constant(ir.IntType(64), 0))
        
        self.compiler.builder = old_builder
        self.compiler.current_function = old_function
        self.compiler.variables = old_variables
        self.compiler.variable_types = old_types
        self.compiler.is_array = old_is_array
        self.compiler.array_sizes = old_array_sizes
        self.compiler.array_length = old_array_length
        self.compiler.array_values = old_array_values
        self.compiler.object_class = old_object_class
        self.compiler.current_this_ptr = old_current_this
        
        return func

    def compile_new(self, node):
        class_name = node.class_name
        class_obj = self.compiler.classes.get(class_name)
        
        if not class_obj:
            if self.compiler.debug:
                print(f"WARNING: Unknown class '{class_name}'")
            return ir.Constant(ir.PointerType(ir.IntType(8)), None)
        
        args = []
        for arg in node.args:
            val = self.compiler.expr.compile(arg)
            args.append(self.compiler.types.coerce_to_i64(val))
        
        num_args = max(len(args), 1)
        args_array = self.compiler.builder.alloca(ir.ArrayType(ir.IntType(64), num_args))
        for i, arg_val in enumerate(args):
            ptr = self.compiler.builder.gep(args_array, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), i)])
            self.compiler.builder.store(arg_val, ptr)
        
        args_ptr = self.compiler.builder.bitcast(args_array, ir.PointerType(ir.IntType(64)))
        arg_count = ir.Constant(ir.IntType(64), len(args))
        
        obj = self.compiler.builder.call(self.compiler.runtime_new_object, [class_obj, args_ptr, arg_count])
        
        return obj

    def compile_method_call(self, node):
        object_name = node.object_name
        
        if isinstance(object_name, str):
            if object_name == "hetha":
                obj_ptr = self.compiler.current_this_ptr
                if obj_ptr is None:
                    obj_ptr = self.compiler.variables.get("hetha")
            else:
                obj_ptr = self.compiler.variables.get(object_name)
                if obj_ptr is None:
                    obj_ptr = self.compiler.function_args.get(object_name)
                
                if obj_ptr is not None and isinstance(obj_ptr.type, ir.PointerType):
                    pointee = obj_ptr.type.pointee
                    if isinstance(pointee, ir.PointerType):
                        obj_ptr = self.compiler.builder.load(obj_ptr)
                    elif pointee == ir.IntType(8):
                        pass
                    else:
                        obj_ptr = self.compiler.builder.load(obj_ptr)
        else:
            obj_ptr = self.compiler.expr.compile(object_name)
        
        if obj_ptr is None:
            if self.compiler.debug:
                print(f"WARNING: Cannot resolve object '{object_name}'")
            return ir.Constant(ir.IntType(64), 0)
        
        if isinstance(obj_ptr.type, ir.PointerType):
            pointee = obj_ptr.type.pointee
            if isinstance(pointee, ir.PointerType):
                obj_ptr = self.compiler.builder.load(obj_ptr)
            elif pointee == ir.IntType(8):
                pass
            elif pointee == ir.IntType(64):
                obj_ptr = self.compiler.builder.inttoptr(obj_ptr, ir.PointerType(ir.IntType(8)))
            else:
                obj_ptr = self.compiler.builder.bitcast(obj_ptr, ir.PointerType(ir.IntType(8)))
        elif obj_ptr.type == ir.IntType(64):
            obj_ptr = self.compiler.builder.inttoptr(obj_ptr, ir.PointerType(ir.IntType(8)))
        
        args = []
        for arg in node.args:
            val = self.compiler.expr.compile(arg)
            args.append(self.compiler.types.coerce_to_i64(val))
        
        num_args = max(len(args), 1)
        args_array = self.compiler.builder.alloca(ir.ArrayType(ir.IntType(64), num_args))
        for i, arg_val in enumerate(args):
            ptr = self.compiler.builder.gep(args_array, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), i)])
            self.compiler.builder.store(arg_val, ptr)
        
        args_ptr = self.compiler.builder.bitcast(args_array, ir.PointerType(ir.IntType(64)))
        arg_count = ir.Constant(ir.IntType(64), len(args))
        
        method_name_ptr = self.compiler.utils.create_string(node.method_name)
        result = self.compiler.builder.call(
            self.compiler.runtime_call_method,
            [obj_ptr, method_name_ptr, args_ptr, arg_count]
        )
        
        return result

    def compile_property(self, node):
        from ...parser.ast import StringNode, IdentifierNode
        
        if node.is_assignment:
            obj_ptr = self.compiler.current_this_ptr
            if obj_ptr is None:
                obj_ptr = self.compiler.variables.get("hetha")
                if obj_ptr is not None:
                    if isinstance(obj_ptr.type, ir.PointerType):
                        if isinstance(obj_ptr.type.pointee, ir.PointerType):
                            obj_ptr = self.compiler.builder.load(obj_ptr)
                        elif obj_ptr.type.pointee == ir.IntType(8):
                            pass
                        else:
                            obj_ptr = self.compiler.builder.load(obj_ptr)
            
            if obj_ptr is None:
                return self.compiler.expr.compile(node.value)
            
            if isinstance(obj_ptr.type, ir.PointerType):
                pointee = obj_ptr.type.pointee
                if isinstance(pointee, ir.PointerType):
                    obj_ptr = self.compiler.builder.load(obj_ptr)
                elif pointee == ir.IntType(8):
                    pass
                elif pointee == ir.IntType(64):
                    obj_ptr = self.compiler.builder.inttoptr(obj_ptr, ir.PointerType(ir.IntType(8)))
                else:
                    obj_ptr = self.compiler.builder.bitcast(obj_ptr, ir.PointerType(ir.IntType(8)))
            elif obj_ptr.type == ir.IntType(64):
                obj_ptr = self.compiler.builder.inttoptr(obj_ptr, ir.PointerType(ir.IntType(8)))
            
            prop_name_ptr = self.compiler.utils.create_string(node.name)
            value = self.compiler.expr.compile(node.value)
            
            if isinstance(node.value, StringNode) or str(value.type) == "i8*":
                if str(value.type) != "i8*":
                    value = self.compiler.utils.convert_to_string(value)
                self.compiler.builder.call(self.compiler.runtime_set_field_string, [obj_ptr, prop_name_ptr, value])
            else:
                value_i64 = self.compiler.types.coerce_to_i64(value)
                self.compiler.builder.call(self.compiler.runtime_set_field, [obj_ptr, prop_name_ptr, value_i64])
            
            return value
        else:
            if node.value is None:
                obj_ptr = self.compiler.current_this_ptr
                if obj_ptr is None:
                    obj_ptr = self.compiler.variables.get("hetha")
                    if obj_ptr is not None:
                        if isinstance(obj_ptr.type, ir.PointerType):
                            if isinstance(obj_ptr.type.pointee, ir.PointerType):
                                obj_ptr = self.compiler.builder.load(obj_ptr)
                            elif obj_ptr.type.pointee == ir.IntType(8):
                                pass
            elif isinstance(node.value, IdentifierNode):
                obj_ptr = self.compiler.variables.get(node.value.name)
                if obj_ptr is not None and isinstance(obj_ptr.type, ir.PointerType):
                    if isinstance(obj_ptr.type.pointee, ir.PointerType):
                        obj_ptr = self.compiler.builder.load(obj_ptr)
                    elif obj_ptr.type.pointee == ir.IntType(8):
                        pass
                    else:
                        obj_ptr = self.compiler.builder.load(obj_ptr)
            else:
                obj_ptr = self.compiler.expr.compile(node.value)
            
            if obj_ptr is None:
                return ir.Constant(ir.PointerType(ir.IntType(8)), None)
            
            if isinstance(obj_ptr.type, ir.PointerType):
                pointee = obj_ptr.type.pointee
                if isinstance(pointee, ir.PointerType):
                    obj_ptr = self.compiler.builder.load(obj_ptr)
                elif pointee == ir.IntType(8):
                    pass
                elif pointee == ir.IntType(64):
                    obj_ptr = self.compiler.builder.inttoptr(obj_ptr, ir.PointerType(ir.IntType(8)))
                else:
                    obj_ptr = self.compiler.builder.bitcast(obj_ptr, ir.PointerType(ir.IntType(8)))
            elif obj_ptr.type == ir.IntType(64):
                obj_ptr = self.compiler.builder.inttoptr(obj_ptr, ir.PointerType(ir.IntType(8)))
            
            prop_name_ptr = self.compiler.utils.create_string(node.name)
            
            string_result = self.compiler.builder.call(self.compiler.runtime_get_field_string, [obj_ptr, prop_name_ptr])
            
            is_string = self.compiler.builder.icmp_signed('!=', string_result, ir.Constant(ir.PointerType(ir.IntType(8)), None))
            
            int_result = self.compiler.builder.call(self.compiler.runtime_get_field, [obj_ptr, prop_name_ptr])
            
            string_block = self.compiler.current_function.append_basic_block("prop_string")
            int_block = self.compiler.current_function.append_basic_block("prop_int")
            end_block = self.compiler.current_function.append_basic_block("prop_end")
            
            result_alloca = self.compiler.builder.alloca(ir.PointerType(ir.IntType(8)), name="prop_result")
            
            self.compiler.builder.cbranch(is_string, string_block, int_block)
            
            self.compiler.builder.position_at_start(string_block)
            self.compiler.builder.store(string_result, result_alloca)
            self.compiler.builder.branch(end_block)
            
            self.compiler.builder.position_at_start(int_block)
            type_ptr = self.compiler.utils.create_string("int")
            int_as_string = self.compiler.builder.call(self.compiler.runtime_value_to_string, [int_result, type_ptr])
            self.compiler.builder.store(int_as_string, result_alloca)
            self.compiler.builder.branch(end_block)
            
            self.compiler.builder.position_at_start(end_block)
            result = self.compiler.builder.load(result_alloca)
            
            return result

    def compile_super(self, node):
        obj_ptr = self.compiler.current_this_ptr
        if obj_ptr is None:
            obj_ptr = self.compiler.variables.get("hetha")
            if obj_ptr is not None and isinstance(obj_ptr.type, ir.PointerType):
                if isinstance(obj_ptr.type.pointee, ir.PointerType):
                    obj_ptr = self.compiler.builder.load(obj_ptr)
        
        if obj_ptr is None:
            return ir.Constant(ir.IntType(64), 0)
        
        if isinstance(obj_ptr.type, ir.PointerType):
            pointee = obj_ptr.type.pointee
            if isinstance(pointee, ir.PointerType):
                obj_ptr = self.compiler.builder.load(obj_ptr)
            elif pointee == ir.IntType(8):
                pass
            elif pointee == ir.IntType(64):
                obj_ptr = self.compiler.builder.inttoptr(obj_ptr, ir.PointerType(ir.IntType(8)))
            else:
                obj_ptr = self.compiler.builder.bitcast(obj_ptr, ir.PointerType(ir.IntType(8)))
        elif obj_ptr.type == ir.IntType(64):
            obj_ptr = self.compiler.builder.inttoptr(obj_ptr, ir.PointerType(ir.IntType(8)))
        
        args = []
        for arg in node.args:
            val = self.compiler.expr.compile(arg)
            args.append(self.compiler.types.coerce_to_i64(val))
        
        num_args = max(len(args), 1)
        args_array = self.compiler.builder.alloca(ir.ArrayType(ir.IntType(64), num_args))
        for i, arg_val in enumerate(args):
            ptr = self.compiler.builder.gep(args_array, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), i)])
            self.compiler.builder.store(arg_val, ptr)
        
        args_ptr = self.compiler.builder.bitcast(args_array, ir.PointerType(ir.IntType(64)))
        arg_count = ir.Constant(ir.IntType(64), len(args))
        
        method_name_ptr = self.compiler.utils.create_string("jdid")
        result = self.compiler.builder.call(
            self.compiler.runtime_call_method,
            [obj_ptr, method_name_ptr, args_ptr, arg_count]
        )
        
        return result