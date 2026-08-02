"""
LLVM Backend for Bel.Bou Native Compiler
Phase 8: Native Compiler (LLVM Implementation)
"""

import os
import sys
import subprocess
import tempfile
from typing import Optional, List, Dict, Any
from pathlib import Path

try:
    import llvmlite.ir as ir
    import llvmlite.binding as llvm
    LLVM_AVAILABLE = True
except ImportError:
    LLVM_AVAILABLE = False

class LLVMBackend:
    """LLVM backend for code generation"""
    
    def __init__(self, debug=False):
        if not LLVM_AVAILABLE:
            raise ImportError("llvmlite is required. Install with: pip install llvmlite")
        
        self.debug = debug
        self._init_llvm()
        
        # Module and builder
        self.module = None
        self.builder = None
        self.current_function = None
        
        # Symbol tables
        self.symbols = {}  # variables
        self.functions = {}  # functions
        self.string_constants = {}
        self.loop_stack = []
        
        # Type mapping
        self.type_map = {
            'int': ir.IntType(64),
            'float': ir.DoubleType(),
            'bool': ir.IntType(1),
            'string': ir.PointerType(ir.IntType(8)),
            'void': ir.VoidType()
        }
        
        # Built-in functions
        self.builtin_functions = {}
    
    def _init_llvm(self):
        """Initialize LLVM environment"""
        llvm.initialize()
        llvm.initialize_native_target()
        llvm.initialize_native_asmprinter()
        
        # Create target machine
        self.target = llvm.Target.from_default_triple()
        self.target_machine = self.target.create_target_machine()
        self.triple = llvm.get_default_triple()
        
        if self.debug:
            print(f"✅ LLVM initialized with target: {self.triple}")
    
    def create_module(self, name: str = "boubel_module"):
        """Create a new LLVM module"""
        self.module = ir.Module(name=name)
        self.module.triple = self.triple
        
        # Add system library functions
        self._declare_external_functions()
        
        return self.module
    
    def _declare_external_functions(self):
        """Declare external C functions we need"""
        # printf
        printf_ty = ir.FunctionType(
            ir.IntType(32),
            [ir.PointerType(ir.IntType(8))],
            var_arg=True
        )
        self.printf = ir.Function(self.module, printf_ty, name="printf")
        
        # scanf
        scanf_ty = ir.FunctionType(
            ir.IntType(32),
            [ir.PointerType(ir.IntType(8))],
            var_arg=True
        )
        self.scanf = ir.Function(self.module, scanf_ty, name="scanf")
        
        # puts
        puts_ty = ir.FunctionType(
            ir.IntType(32),
            [ir.PointerType(ir.IntType(8))]
        )
        self.puts = ir.Function(self.module, puts_ty, name="puts")
        
        # malloc/free
        malloc_ty = ir.FunctionType(
            ir.PointerType(ir.IntType(8)),
            [ir.IntType(64)]
        )
        self.malloc = ir.Function(self.module, malloc_ty, name="malloc")
        
        free_ty = ir.FunctionType(
            ir.VoidType(),
            [ir.PointerType(ir.IntType(8))]
        )
        self.free = ir.Function(self.module, free_ty, name="free")
        
        # exit
        exit_ty = ir.FunctionType(
            ir.VoidType(),
            [ir.IntType(32)]
        )
        self.exit = ir.Function(self.module, exit_ty, name="exit")
    
    def compile_ast(self, ast_node) -> str:
        """
        Compile AST to LLVM IR
        
        Args:
            ast_node: AST root node
            
        Returns:
            str: LLVM IR as string
        """
        self.create_module()
        
        # Create main function
        main_ty = ir.FunctionType(ir.IntType(32), [])
        main_func = ir.Function(self.module, main_ty, name="main")
        
        # Create entry block
        entry_block = main_func.append_basic_block(name="entry")
        self.builder = ir.IRBuilder(entry_block)
        self.current_function = main_func
        
        # Visit AST nodes
        self._visit(ast_node)
        
        # Return 0
        self.builder.ret(ir.Constant(ir.IntType(32), 0))
        
        # Optimize
        self._optimize_module()
        
        if self.debug:
            print("\n📄 LLVM IR Generated:")
            print("-" * 50)
            print(str(self.module))
            print("-" * 50)
        
        return str(self.module)
    
    def _visit(self, node):
        """Visit an AST node"""
        if node is None:
            return
        
        # Import AST node types
        from src.parser.ast import (
            ProgramNode, VariableNode, AssignmentNode, PrintNode,
            InputNode, IfNode, ForNode, WhileNode, ReturnNode,
            CallNode, FunctionNode, BreakNode, ContinueNode,
            NumberNode, StringNode, BooleanNode, NullNode,
            IdentifierNode, BinOpNode, UnaryOpNode, ArrayLiteralNode,
            ArrayAccessNode, FileWriteNode, FileReadNode
        )
        
        if isinstance(node, ProgramNode):
            for stmt in node.statements:
                if not isinstance(stmt, FunctionNode):
                    self._visit(stmt)
        
        elif isinstance(node, FunctionNode):
            self._compile_function(node)
        
        elif isinstance(node, VariableNode):
            self._compile_variable(node)
        
        elif isinstance(node, AssignmentNode):
            self._compile_assignment(node)
        
        elif isinstance(node, PrintNode):
            self._compile_print(node)
        
        elif isinstance(node, InputNode):
            self._compile_input(node)
        
        elif isinstance(node, IfNode):
            self._compile_if(node)
        
        elif isinstance(node, ForNode):
            self._compile_for(node)
        
        elif isinstance(node, WhileNode):
            self._compile_while(node)
        
        elif isinstance(node, ReturnNode):
            self._compile_return(node)
        
        elif isinstance(node, CallNode):
            self._compile_call(node)
        
        elif isinstance(node, BreakNode):
            self._compile_break()
        
        elif isinstance(node, ContinueNode):
            self._compile_continue()
        
        else:
            # Expression
            self._compile_expression(node)
    
    def _compile_function(self, func_node):
        """Compile a function"""
        param_types = [ir.IntType(64) for _ in func_node.params]
        func_type = ir.FunctionType(ir.IntType(64), param_types)
        
        func = ir.Function(self.module, func_type, name=func_node.name)
        self.functions[func_node.name] = func
        
        # Save old context
        old_builder = self.builder
        old_function = self.current_function
        old_symbols = self.symbols.copy()
        
        # Create new context
        block = func.append_basic_block(name="entry")
        self.builder = ir.IRBuilder(block)
        self.current_function = func
        self.symbols = {}
        
        # Store parameters
        for i, arg in enumerate(func.args):
            arg.name = func_node.params[i]
            alloca = self.builder.alloca(ir.IntType(64), name=func_node.params[i])
            self.builder.store(arg, alloca)
            self.symbols[func_node.params[i]] = alloca
        
        # Compile body
        for stmt in func_node.body:
            self._visit(stmt)
        
        # Add return if missing
        if not self.builder.block.is_terminated:
            self.builder.ret(ir.Constant(ir.IntType(64), 0))
        
        # Restore context
        self.builder = old_builder
        self.current_function = old_function
        self.symbols = old_symbols
    
    def _compile_variable(self, node):
        """Compile variable declaration"""
        value = self._compile_expression(node.value)
        alloca = self.builder.alloca(ir.IntType(64), name=node.name)
        self.builder.store(value, alloca)
        self.symbols[node.name] = alloca
    
    def _compile_assignment(self, node):
        """Compile assignment"""
        value = self._compile_expression(node.value)
        
        if node.name in self.symbols:
            self.builder.store(value, self.symbols[node.name])
        else:
            alloca = self.builder.alloca(ir.IntType(64), name=node.name)
            self.builder.store(value, alloca)
            self.symbols[node.name] = alloca
    
    def _compile_print(self, node):
        """Compile print statement"""
        value = self._compile_expression(node.value)
        
        # Format string
        format_str = self._create_global_string("%lld\n")
        format_ptr = self.builder.bitcast(format_str, ir.PointerType(ir.IntType(8)))
        
        # Call printf
        self.builder.call(self.printf, [format_ptr, value])
    
    def _compile_input(self, node):
        """Compile input statement"""
        # For now, return 0
        return ir.Constant(ir.IntType(64), 0)
    
    def _compile_if(self, node):
        """Compile if statement"""
        condition = self._compile_expression(node.condition)
        cond_bool = self.builder.icmp_signed('!=', condition, 
                                            ir.Constant(ir.IntType(64), 0))
        
        then_block = self.current_function.append_basic_block(name="then")
        else_block = self.current_function.append_basic_block(name="else")
        end_block = self.current_function.append_basic_block(name="endif")
        
        self.builder.cbranch(cond_bool, then_block, else_block)
        
        # Then block
        self.builder.position_at_start(then_block)
        for stmt in node.then_body:
            self._visit(stmt)
        if not self.builder.block.is_terminated:
            self.builder.branch(end_block)
        
        # Else block
        self.builder.position_at_start(else_block)
        if node.else_body:
            if isinstance(node.else_body, list):
                for stmt in node.else_body:
                    self._visit(stmt)
            else:
                self._visit(node.else_body)
        if not self.builder.block.is_terminated:
            self.builder.branch(end_block)
        
        self.builder.position_at_start(end_block)
    
    def _compile_for(self, node):
        """Compile for loop"""
        # Initialize iterator
        start_val = self._compile_expression(node.start)
        iter_alloca = self.builder.alloca(ir.IntType(64), name=node.iterator)
        self.builder.store(start_val, iter_alloca)
        self.symbols[node.iterator] = iter_alloca
        
        start_block = self.current_function.append_basic_block(name="for_start")
        body_block = self.current_function.append_basic_block(name="for_body")
        end_block = self.current_function.append_basic_block(name="for_end")
        
        self.loop_stack.append((start_block, end_block))
        
        self.builder.branch(start_block)
        self.builder.position_at_start(start_block)
        
        # Check condition
        current = self.builder.load(iter_alloca)
        end_val = self._compile_expression(node.end)
        cond = self.builder.icmp_signed('<=', current, end_val)
        self.builder.cbranch(cond, body_block, end_block)
        
        # Body
        self.builder.position_at_start(body_block)
        for stmt in node.body:
            self._visit(stmt)
        if not self.builder.block.is_terminated:
            # Increment
            current = self.builder.load(iter_alloca)
            inc = self.builder.add(current, ir.Constant(ir.IntType(64), 1))
            self.builder.store(inc, iter_alloca)
            self.builder.branch(start_block)
        
        self.builder.position_at_start(end_block)
        self.loop_stack.pop()
        
        # Clean up
        del self.symbols[node.iterator]
    
    def _compile_while(self, node):
        """Compile while loop"""
        start_block = self.current_function.append_basic_block(name="while_start")
        body_block = self.current_function.append_basic_block(name="while_body")
        end_block = self.current_function.append_basic_block(name="while_end")
        
        self.loop_stack.append((start_block, end_block))
        
        self.builder.branch(start_block)
        self.builder.position_at_start(start_block)
        
        condition = self._compile_expression(node.condition)
        cond_bool = self.builder.icmp_signed('!=', condition,
                                            ir.Constant(ir.IntType(64), 0))
        self.builder.cbranch(cond_bool, body_block, end_block)
        
        self.builder.position_at_start(body_block)
        for stmt in node.body:
            self._visit(stmt)
        if not self.builder.block.is_terminated:
            self.builder.branch(start_block)
        
        self.builder.position_at_start(end_block)
        self.loop_stack.pop()
    
    def _compile_return(self, node):
        """Compile return statement"""
        value = self._compile_expression(node.value)
        self.builder.ret(value)
    
    def _compile_call(self, node):
        """Compile function call"""
        func_name = node.name.name if hasattr(node.name, 'name') else node.name
        
        if func_name in self.functions:
            args = [self._compile_expression(arg) for arg in node.args]
            return self.builder.call(self.functions[func_name], args)
        
        # Built-in functions
        if func_name == 'len':
            if node.args:
                return self._compile_len(node.args[0])
            return ir.Constant(ir.IntType(64), 0)
        
        # Unknown function
        return ir.Constant(ir.IntType(64), 0)
    
    def _compile_len(self, arg):
        """Compile len() function"""
        # For strings, use strlen
        if isinstance(arg, StringNode):
            return ir.Constant(ir.IntType(64), len(arg.value))
        
        # For arrays, use array size
        if isinstance(arg, ArrayLiteralNode):
            return ir.Constant(ir.IntType(64), len(arg.elements))
        
        return ir.Constant(ir.IntType(64), 0)
    
    def _compile_break(self):
        """Compile break statement"""
        if self.loop_stack:
            _, end_block = self.loop_stack[-1]
            self.builder.branch(end_block)
    
    def _compile_continue(self):
        """Compile continue statement"""
        if self.loop_stack:
            start_block, _ = self.loop_stack[-1]
            self.builder.branch(start_block)
    
    def _compile_expression(self, node):
        """Compile an expression"""
        from src.parser.ast import (
            NumberNode, StringNode, BooleanNode, NullNode,
            IdentifierNode, BinOpNode, UnaryOpNode, CallNode,
            ArrayLiteralNode, ArrayAccessNode
        )
        
        if node is None:
            return ir.Constant(ir.IntType(64), 0)
        
        if isinstance(node, NumberNode):
            return ir.Constant(ir.IntType(64), node.value)
        
        elif isinstance(node, StringNode):
            return self._create_global_string(node.value)
        
        elif isinstance(node, BooleanNode):
            return ir.Constant(ir.IntType(64), 1 if node.value else 0)
        
        elif isinstance(node, NullNode):
            return ir.Constant(ir.IntType(64), 0)
        
        elif isinstance(node, IdentifierNode):
            if node.name in self.symbols:
                return self.builder.load(self.symbols[node.name])
            return ir.Constant(ir.IntType(64), 0)
        
        elif isinstance(node, BinOpNode):
            left = self._compile_expression(node.left)
            right = self._compile_expression(node.right)
            return self._compile_binop(node.op, left, right)
        
        elif isinstance(node, UnaryOpNode):
            value = self._compile_expression(node.expr)
            op = node.op.value if hasattr(node.op, 'value') else str(node.op)
            if op in ['MINUS', '-']:
                return self.builder.neg(value)
            elif op in ['NOT', '!']:
                is_zero = self.builder.icmp_signed('==', value,
                                                   ir.Constant(ir.IntType(64), 0))
                return self.builder.zext(is_zero, ir.IntType(64))
            return value
        
        elif isinstance(node, CallNode):
            return self._compile_call(node)
        
        elif isinstance(node, ArrayLiteralNode):
            return ir.Constant(ir.IntType(64), len(node.elements))
        
        else:
            return ir.Constant(ir.IntType(64), 0)
    
    def _compile_binop(self, op, left, right):
        """Compile binary operation"""
        op_value = op.value if hasattr(op, 'value') else str(op)
        
        if op_value in ['PLUS', '+']:
            return self.builder.add(left, right)
        elif op_value in ['MINUS', '-']:
            return self.builder.sub(left, right)
        elif op_value in ['STAR', '*']:
            return self.builder.mul(left, right)
        elif op_value in ['SLASH', '/']:
            return self.builder.sdiv(left, right)
        elif op_value in ['MOD', '%']:
            return self.builder.srem(left, right)
        elif op_value in ['EQUAL_EQUAL', '==']:
            cmp = self.builder.icmp_signed('==', left, right)
            return self.builder.zext(cmp, ir.IntType(64))
        elif op_value in ['NOT_EQUAL', '!=']:
            cmp = self.builder.icmp_signed('!=', left, right)
            return self.builder.zext(cmp, ir.IntType(64))
        elif op_value in ['GREATER', '>']:
            cmp = self.builder.icmp_signed('>', left, right)
            return self.builder.zext(cmp, ir.IntType(64))
        elif op_value in ['LESS', '<']:
            cmp = self.builder.icmp_signed('<', left, right)
            return self.builder.zext(cmp, ir.IntType(64))
        elif op_value in ['GREATER_EQUAL', '>=']:
            cmp = self.builder.icmp_signed('>=', left, right)
            return self.builder.zext(cmp, ir.IntType(64))
        elif op_value in ['LESS_EQUAL', '<=']:
            cmp = self.builder.icmp_signed('<=', left, right)
            return self.builder.zext(cmp, ir.IntType(64))
        elif op_value in ['AND', '&&']:
            return self.builder.and_(left, right)
        elif op_value in ['OR', '||']:
            return self.builder.or_(left, right)
        else:
            return self.builder.add(left, right)
    
    def _create_global_string(self, value: str) -> ir.Constant:
        """Create a global string constant"""
        # Remove quotes if present
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        
        # Check cache
        if value in self.string_constants:
            return self.string_constants[value]
        
        # Create string
        bytes_data = value.encode('utf-8') + b'\x00'
        str_type = ir.ArrayType(ir.IntType(8), len(bytes_data))
        str_constant = ir.Constant(str_type, list(bytes_data))
        
        # Create global variable
        var_name = f"str_{len(self.string_constants)}"
        global_var = ir.GlobalVariable(self.module, str_type, name=var_name)
        global_var.initializer = str_constant
        global_var.global_constant = True
        
        # Cache
        self.string_constants[value] = global_var
        
        # Return pointer to string
        return self.builder.bitcast(global_var, ir.PointerType(ir.IntType(8)))
    
    def _optimize_module(self, optimization_level: int = 2):
        """Optimize LLVM module"""
        try:
            pm_builder = llvm.PassManagerBuilder()
            pm_builder.opt_level = optimization_level
            pm_builder.size_level = 0
            
            pm = llvm.ModulePassManager()
            pm_builder.populate(pm)
            
            pm.run(self.module)
        except Exception as e:
            if self.debug:
                print(f"⚠️  Optimization warning: {e}")
    
    def compile_to_object(self, output_file: str):
        """Compile LLVM IR to object file"""
        with open(output_file, 'wb') as f:
            f.write(self.target_machine.emit_object(self.module))
    
    def compile_to_assembly(self, output_file: str):
        """Compile LLVM IR to assembly"""
        with open(output_file, 'w') as f:
            f.write(self.target_machine.emit_assembly(self.module))
    
    def link_executable(self, object_files: List[str], output_file: str):
        """Link object files into executable"""
        linker = 'gcc' if os.name != 'nt' else 'clang'
        cmd = [linker, '-o', output_file] + object_files
        
        if os.name != 'nt':
            cmd.append('-lm')
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"Linking failed: {result.stderr}")
        
        return result
    
    def compile_and_link(self, ast, output_file: str, optimize: bool = True):
        """Full compilation pipeline"""
        # Generate IR
        ir_code = self.compile_ast(ast)
        
        # Temporary files
        with tempfile.NamedTemporaryFile(suffix='.o', delete=False) as obj_file:
            obj_path = obj_file.name
        
        with tempfile.NamedTemporaryFile(suffix='.ll', delete=False) as ir_file:
            ir_path = ir_file.name
            ir_file.write(ir_code.encode('utf-8'))
        
        try:
            # Compile to object
            self.compile_to_object(obj_path)
            
            # Link
            self.link_executable([obj_path], output_file)
            
            if self.debug:
                print(f"✅ Native executable generated: {output_file}")
            
        finally:
            # Cleanup
            for path in [ir_path, obj_path]:
                if os.path.exists(path):
                    try:
                        os.unlink(path)
                    except:
                        pass