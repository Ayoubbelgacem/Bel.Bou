# src/vm/bytecode.py
from enum import Enum

class OpCode(Enum):
    # Stack operations
    PUSH = 1
    POP = 2
    LOAD_CONST = 3
    LOAD_VAR = 4
    STORE_VAR = 5
    
    # Arithmetic
    ADD = 10
    SUB = 11
    MUL = 12
    DIV = 13
    MOD = 14
    
    # Comparison
    EQ = 20
    NE = 21
    GT = 22
    LT = 23
    GE = 24
    LE = 25
    
    # Logic
    AND = 30
    OR = 31
    NOT = 32
    
    # Control flow
    JUMP = 40
    JUMP_IF_FALSE = 41
    JUMP_IF_TRUE = 42
    
    # Functions
    CALL = 50
    RETURN = 51
    
    # Objects
    NEW_OBJECT = 60
    LOAD_PROPERTY = 61
    STORE_PROPERTY = 62
    CALL_METHOD = 63
    
    # Arrays
    NEW_ARRAY = 70
    LOAD_INDEX = 71
    STORE_INDEX = 72
    
    # I/O
    PRINT = 80
    INPUT = 81
    
    # File I/O
    READ_FILE = 90
    WRITE_FILE = 91
    
    # Exception
    TRY = 100
    CATCH = 101
    FINALLY = 102
    THROW = 103
    
    HALT = 99
    
    def __str__(self):
        return self.name

class Bytecode:
    def __init__(self):
        self.code = []
        self.constants = []
        self.labels = {}
        self.functions = {}
        self.classes = {}
    
    def add(self, opcode, arg=None):
        self.code.append((opcode, arg))
    
    def add_constant(self, value):
        if value not in self.constants:
            self.constants.append(value)
        return self.constants.index(value)
    
    def add_label(self, name):
        self.labels[name] = len(self.code)
    
    def resolve_label(self, name):
        if name in self.labels:
            return self.labels[name]
        # Si le label n'existe pas encore, on le crée (forward reference)
        self.labels[name] = -1
        return -1
    
    def patch_labels(self):
        """Patch les labels forward references"""
        for i, (opcode, arg) in enumerate(self.code):
            if opcode in [OpCode.JUMP, OpCode.JUMP_IF_FALSE, OpCode.JUMP_IF_TRUE]:
                if isinstance(arg, str) and arg in self.labels:
                    self.code[i] = (opcode, self.labels[arg])
    
    def disassemble(self):
        print("\n" + "="*60)
        print("BYTECODE GENERATED:")
        print("="*60)
        
        print("\nConstants:")
        for i, const in enumerate(self.constants):
            print(f"  {i}: {repr(const)}")
        
        print("\nLabels:")
        for name, pos in self.labels.items():
            print(f"  {name}: {pos}")
        
        print("\nInstructions:")
        for i, (opcode, arg) in enumerate(self.code):
            if arg is not None:
                if isinstance(arg, int) and arg < len(self.constants) and opcode == OpCode.LOAD_CONST:
                    const = self.constants[arg] if arg < len(self.constants) else arg
                    print(f"  {i:4d}: {opcode.name} {arg} ({repr(const)})")
                else:
                    print(f"  {i:4d}: {opcode.name} {arg}")
            else:
                print(f"  {i:4d}: {opcode.name}")
        print("="*60 + "\n")
        return self.code