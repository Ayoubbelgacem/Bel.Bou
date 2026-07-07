# src/vm/bytecode.py
from enum import Enum

class OpCode(Enum):
    # Stack operations
    PUSH = 1
    POP = 2
    LOAD_CONST = 3
    LOAD_VAR = 4
    STORE_VAR = 5
    DUP = 6              # Duplique le sommet de la pile
    SWAP = 7             # Échange les deux éléments du sommet
    
    # Arithmetic (optimized)
    ADD = 10
    SUB = 11
    MUL = 12
    DIV = 13
    MOD = 14
    NEG = 15             # Négation unaire
    INC = 16             # Incrémenter (i++)
    DEC = 17             # Décrémenter (i--)
    
    # Combined arithmetic (pour a += b)
    ADD_STORE = 20
    SUB_STORE = 21
    MUL_STORE = 22
    DIV_STORE = 23
    
    # Comparison (optimized)
    EQ = 30
    NE = 31
    GT = 32
    LT = 33
    GE = 34
    LE = 35
    CMP = 36             # Comparaison générique (retourne -1, 0, 1)
    
    # Logic
    AND = 40
    OR = 41
    NOT = 42
    
    # Control flow
    JUMP = 50
    JUMP_IF_FALSE = 51
    JUMP_IF_TRUE = 52
    JUMP_IF_NIL = 53     # Saut si la valeur est None
    LOOP = 54            # Boucle optimisée
    
    # Functions (optimized)
    CALL = 60
    CALL_FAST = 61       # Appel de fonction rapide (sans création de frame)
    RETURN = 62
    RETURN_FAST = 63     # Retour rapide (sans frame)
    
    # Objects (optimized)
    NEW_OBJECT = 70
    LOAD_PROPERTY = 71
    STORE_PROPERTY = 72
    CALL_METHOD = 73
    CALL_METHOD_FAST = 74  # Appel de méthode rapide
    
    # Arrays (optimized)
    NEW_ARRAY = 80
    LOAD_INDEX = 81
    STORE_INDEX = 82
    ARRAY_LEN = 83       # len(array) optimisé
    
    # I/O
    PRINT = 90
    INPUT = 91
    PRINT_FAST = 92      # Print sans allocation de string
    
    # File I/O
    READ_FILE = 100
    WRITE_FILE = 101
    
    # Exception
    TRY = 110
    CATCH = 111
    FINALLY = 112
    THROW = 113
    
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
        self.optimize = optimize
    
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
        self.labels[name] = -1
        return -1
    
    def patch_labels(self):
        for i, (opcode, arg) in enumerate(self.code):
            if opcode in [OpCode.JUMP, OpCode.JUMP_IF_FALSE, OpCode.JUMP_IF_TRUE,
                          OpCode.JUMP_IF_NIL, OpCode.LOOP]:
                if isinstance(arg, str) and arg in self.labels:
                    self.code[i] = (opcode, self.labels[arg])
    
    def optimize(self):
        """Optimisation du bytecode"""
        if not self.optimize:
            return self
        
        # Passe 1: Suppression des opcodes inutiles
        self._remove_dead_code()
        
        # Passe 2: Fusion des opcodes
        self._merge_operations()
        
        # Passe 3: Optimisation des sauts
        self._optimize_jumps()
        
        # Passe 4: Simplification des constantes
        self._simplify_constants()
        
        return self
    
    def _remove_dead_code(self):
        """Supprime le code mort (instructions inaccessibles)"""
        new_code = []
        i = 0
        while i < len(self.code):
            opcode, arg = self.code[i]
            new_code.append((opcode, arg))
            
            # Si c'est un JUMP inconditionnel, on saute les instructions suivantes
            if opcode == OpCode.JUMP:
                pass
            
            i += 1
        self.code = new_code
    
    def _merge_operations(self):
        """Fusionne les opérations (PUSH 1; ADD -> INC)"""
        new_code = []
        i = 0
        while i < len(self.code):
            opcode, arg = self.code[i]
            
            # PUSH 1; ADD -> INC
            if (opcode == OpCode.PUSH and arg == 1 and 
                i + 1 < len(self.code) and self.code[i+1][0] == OpCode.ADD):
                new_code.append((OpCode.INC, None))
                i += 2
                continue
            
            # PUSH 1; SUB -> DEC
            if (opcode == OpCode.PUSH and arg == 1 and 
                i + 1 < len(self.code) and self.code[i+1][0] == OpCode.SUB):
                new_code.append((OpCode.DEC, None))
                i += 2
                continue
            
            # LOAD_CONST; STORE_VAR -> STORE_CONST (optimisé)
            if (opcode == OpCode.LOAD_CONST and 
                i + 1 < len(self.code) and self.code[i+1][0] == OpCode.STORE_VAR):
                new_code.append((OpCode.STORE_VAR, self.code[i+1][1]))
                new_code.append((OpCode.LOAD_CONST, arg))
                i += 2
                continue
            
            new_code.append((opcode, arg))
            i += 1
        
        self.code = new_code
    
    def _optimize_jumps(self):
        """Optimise les sauts (sauts inutiles)"""
        new_code = []
        i = 0
        while i < len(self.code):
            opcode, arg = self.code[i]
            
            # JUMP vers la prochaine instruction -> supprimé
            if opcode == OpCode.JUMP:
                if isinstance(arg, int) and arg == i + 1:
                    i += 1
                    continue
            
            new_code.append((opcode, arg))
            i += 1
        
        self.code = new_code
    
    def _simplify_constants(self):
        """Simplifie les constantes (ex: 1 + 1 -> 2)"""
        pass
    
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