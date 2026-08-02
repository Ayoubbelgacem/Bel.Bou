# src/vm/bytecode.py
from enum import Enum

class OpCode(Enum):
    PUSH = 1
    POP = 2
    LOAD_CONST = 3
    LOAD_VAR = 4
    STORE_VAR = 5
    DUP = 6
    SWAP = 7
    ADD = 10
    SUB = 11
    MUL = 12
    DIV = 13
    MOD = 14
    NEG = 15
    INC = 16
    DEC = 17
    ADD_STORE = 20
    SUB_STORE = 21
    MUL_STORE = 22
    DIV_STORE = 23
    EQ = 30
    NE = 31
    GT = 32
    LT = 33
    GE = 34
    LE = 35
    CMP = 36
    AND = 40
    OR = 41
    NOT = 42
    JUMP = 50
    JUMP_IF_FALSE = 51
    JUMP_IF_TRUE = 52
    JUMP_IF_NIL = 53
    LOOP = 54
    CALL = 60
    CALL_FAST = 61
    RETURN = 62
    RETURN_FAST = 63
    NEW_OBJECT = 70
    LOAD_PROPERTY = 71
    STORE_PROPERTY = 72
    CALL_METHOD = 73
    CALL_METHOD_FAST = 74
    NEW_ARRAY = 80
    LOAD_INDEX = 81
    STORE_INDEX = 82
    ARRAY_LEN = 83
    PRINT = 90
    INPUT = 91
    PRINT_FAST = 92
    READ_FILE = 100
    WRITE_FILE = 101
    TRY = 110
    CATCH = 111
    FINALLY = 112
    THROW = 113
    IMPORT = 114          # 👈 NOUVEAU
    HALT = 99

    def __str__(self):
        return self.name

class Bytecode:
    def __init__(self, optimize=True):
        self.code = []
        self.constants = []
        self.labels = {}
        self.functions = {}
        self.classes = {}
        self.optimize_enabled = optimize

    def add(self, opcode, arg=None):
        self.code.append((opcode, arg))

    def add_constant(self, value):
        for i, existing in enumerate(self.constants):
            if type(existing) == type(value) and existing == value:
                return i
        self.constants.append(value)
        return len(self.constants) - 1

    def add_label(self, name):
        self.labels[name] = len(self.code)

    def resolve_label(self, name):
        if name in self.labels:
            return self.labels[name]
        self.labels[name] = -1
        return -1

    def patch_labels(self):
        for i, (opcode, arg) in enumerate(self.code):
            if opcode in (OpCode.JUMP, OpCode.JUMP_IF_FALSE, OpCode.JUMP_IF_TRUE,
                          OpCode.JUMP_IF_NIL, OpCode.LOOP, OpCode.TRY):
                if isinstance(arg, str) and arg in self.labels:
                    self.code[i] = (opcode, self.labels[arg])

    def optimize(self):
        return self

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
                    const = self.constants[arg]
                    print(f"  {i:4d}: {opcode.name} {arg} ({repr(const)})")
                else:
                    print(f"  {i:4d}: {opcode.name} {arg}")
            else:
                print(f"  {i:4d}: {opcode.name}")
        print("="*60 + "\n")
        return self.code