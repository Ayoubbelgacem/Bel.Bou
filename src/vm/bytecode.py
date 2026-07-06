# src/vm/bytecode.py
from enum import Enum

class OpCode(Enum):
    LOAD_CONST = 1
    LOAD_VAR = 2
    STORE_VAR = 3
    ADD = 4
    SUB = 5
    MUL = 6
    DIV = 7
    PRINT = 8
    CALL = 9
    RETURN = 10
    JUMP = 11
    JUMP_IF_FALSE = 12
    COMPARE = 13
    HALT = 99

class Bytecode:
    def __init__(self):
        self.code = []
        self.constants = []
        self.variables = {}
    
    def add(self, opcode, arg=None):
        self.code.append((opcode, arg))
    
    def add_constant(self, value):
        if value not in self.constants:
            self.constants.append(value)
        return self.constants.index(value)
    
    def disassemble(self):
        print("Bytecode:")
        for i, (opcode, arg) in enumerate(self.code):
            print(f"  {i:3d}: {opcode.name} {arg if arg is not None else ''}")