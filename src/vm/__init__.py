# src/vm/__init__.py
from src.vm.bytecode import Bytecode, OpCode
from src.vm.vm import VM
from src.vm.compiler import Compiler
from src.vm.closure import Closure, Environment
from src.vm.cache import VariableCache