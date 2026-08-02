# src/vm/compiler.py
import os
from src.vm.bytecode import Bytecode, OpCode
from src.parser.ast import *

class Compiler:
    # Noms des fonctions builtin gérées nativement par la VM (_call_builtin).
    # Elles ne sont jamais présentes dans self.bytecode.functions, donc il
    # faut les traiter comme des cibles d'appel statiques valides, au même
    # titre que les fonctions utilisateur, sinon `len(x)`, `str(x)`, etc.
    # tombent à tort dans le chemin d'appel dynamique. On y ajoute aussi les
    # built-ins liés aux modules (time_now, sleep, to_json) pour éviter
    # qu'un module stdlib redéfinissant une fonction du même nom n'écrase
    # silencieusement le comportement natif de la VM.
    BUILTIN_FUNCTIONS = {
        'len', 'str', 'int', 'float', 'type', 'sum', 'max', 'min',
        'time_now', 'sleep', 'to_json',
    }

    # ikteb_fi_mlf(...)/iqra_mlf(...) sont analysés par le parseur comme de
    # simples CallNode (et non FileWriteNode/FileReadNode) : on les traduit
    # directement vers les opcodes WRITE_FILE/READ_FILE.
    FILE_CALL_OPCODES = {
        'ikteb_fi_mlf': OpCode.WRITE_FILE,
        'iqra_mlf': OpCode.READ_FILE,
    }

    def __init__(self, search_paths=None):
        self.bytecode = Bytecode(optimize=True)
        self.current_function = None
        self.loop_stack = []
        self.temp_var_count = 0
        self.types = {}
        self.current_class_name = None
        self.current_class_parent = None
        # Chemins de recherche des modules (.bou). 'modules' et '.' sont
        # toujours inclus par défaut, comme dans LLVMCompiler.
        self.search_paths = (search_paths or []) + ['modules', '.']
        # Modules déjà résolus à la compilation (protection contre les
        # imports circulaires et les doubles imports).
        self._imported_modules = set()

    def compile(self, node):
        self.visit(node)
        self.bytecode.add(OpCode.HALT)
        self.bytecode.patch_labels()
        self.bytecode.optimize()
        return self.bytecode

    def visit(self, node):
        if node is None:
            return
        node_type = node.__class__.__name__
        visit_method = getattr(self, f'visit_{node_type}', None)
        if visit_method:
            return visit_method(node)
        raise Exception(f"Unsupported node type in compiler: {node_type}")

    def visit_ProgramNode(self, node):
        main_label = "__main_entry__"
        self.bytecode.add(OpCode.JUMP, main_label)

        # FIX (imports) : on résout TOUS les imports en premier, à la
        # compilation. _import_module() compile le module directement dans
        # CE MÊME self.bytecode (pas un Bytecode séparé), donc les fonctions
        # importées obtiennent des offsets 'start' cohérents avec le code
        # qui sera réellement exécuté par la VM. C'est indispensable :
        # compiler un module dans un Bytecode à part puis copier juste son
        # dict `functions` (comme le faisait l'ancienne VM._import_module)
        # produit des 'start' qui pointent dans le MAUVAIS tableau
        # d'instructions -> la VM saute n'importe où -> boucle infinie.
        for stmt in node.statements:
            if isinstance(stmt, ImportNode):
                self._import_module(stmt.module_name)

        # Hoisting des fonctions/classes du programme principal (inchangé).
        for stmt in node.statements:
            if isinstance(stmt, (FunctionNode, ClassNode)):
                self.visit(stmt)

        self.bytecode.add_label(main_label)

        # Le reste du programme (les ImportNode sont déjà résolus, on les
        # ignore ici pour ne pas les recompiler/exécuter au runtime).
        for stmt in node.statements:
            if not isinstance(stmt, (FunctionNode, ClassNode, ImportNode)):
                self.visit(stmt)

    # ------------------------------------------------------------------
    # IMPORT (jib) — résolution à la compilation
    # ------------------------------------------------------------------
    def _find_module_file(self, module_name):
        for base in self.search_paths:
            candidate1 = os.path.join(base, f"{module_name}.bou")
            if os.path.exists(candidate1):
                return candidate1
            candidate2 = os.path.join(base, module_name, f"{module_name}.bou")
            if os.path.exists(candidate2):
                return candidate2
        return None

    def _import_module(self, module_name):
        if module_name in self._imported_modules:
            return
        self._imported_modules.add(module_name)

        filepath = self._find_module_file(module_name)
        if filepath is None:
            raise FileNotFoundError(
                f"Module '{module_name}' introuvable dans {self.search_paths}"
            )

        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()

        # Imports tardifs pour éviter les cycles d'import Python entre
        # src.vm.compiler et src.lexer/src.parser.
        from src.lexer.tokenizer import Tokenizer
        from src.parser.parser import Parser

        # ✅ FIX (diagnostic) : on enveloppe le tokenizing/parsing du module
        # pour préciser DANS QUEL FICHIER l'erreur se produit. Sans ça, une
        # erreur de syntaxe dans un module importé (ex: wa9t.bou, json.bou)
        # remonte avec juste "line X, col Y" sans dire de quel fichier il
        # s'agit, ce qui rend le débogage des modules stdlib très pénible.
        try:
            tokenizer = Tokenizer(source)
            tokens = tokenizer.tokenize()
            parser_obj = Parser(tokens)
            module_ast = parser_obj.parse()
        except Exception as e:
            raise Exception(
                f"Erreur en compilant le module '{module_name}' "
                f"(fichier: {filepath}): {e}"
            ) from e

        for stmt in module_ast.statements:
            if isinstance(stmt, ImportNode):
                # Imports transitifs : un module peut lui-même importer
                # d'autres modules.
                self._import_module(stmt.module_name)
            elif isinstance(stmt, FunctionNode):
                # Ne jamais laisser un module stdlib écraser un builtin
                # natif de la VM (time_now, sleep, to_json, len, ...).
                if stmt.name in self.BUILTIN_FUNCTIONS:
                    continue
                # Ne pas recompiler une fonction déjà définie (par le
                # programme principal ou un module importé précédemment) :
                # le premier import/la définition existante gagne.
                if stmt.name not in self.bytecode.functions:
                    self.visit(stmt)
            elif isinstance(stmt, ClassNode):
                if stmt.name not in self.bytecode.classes:
                    self.visit(stmt)
            # Les autres statements top-level d'un module (variables,
            # print, etc.) sont ignorés : un module ne doit pas exécuter
            # de code de premier niveau à l'import, seulement fournir des
            # définitions de fonctions/classes.

    def visit_ImportNode(self, node):
        # Filet de sécurité : normalement déjà traité par visit_ProgramNode
        # avant le hoisting, mais si un ImportNode apparaît ailleurs
        # (imbriqué), on le résout quand même ici plutôt que d'émettre un
        # opcode runtime cassé.
        self._import_module(node.module_name)

    def visit_VariableNode(self, node):
        self.visit(node.value)
        self.bytecode.add(OpCode.STORE_VAR, node.name)
        if node.type_name:
            self.types[node.name] = node.type_name

    def visit_AssignmentNode(self, node):
        self.visit(node.value)
        self.bytecode.add(OpCode.STORE_VAR, node.name)

    def visit_PrintNode(self, node):
        self.visit(node.value)
        self.bytecode.add(OpCode.PRINT)
        self.bytecode.add(OpCode.POP)

    def visit_InputNode(self, node):
        if node.prompt:
            self.visit(node.prompt)
        else:
            self.bytecode.add(OpCode.PUSH, "")
        self.bytecode.add(OpCode.INPUT)

    def visit_IfNode(self, node):
        label_else = f"if_else_{len(self.bytecode.code)}"
        label_end = f"if_end_{len(self.bytecode.code)}"
        self.visit(node.condition)
        self.bytecode.add(OpCode.JUMP_IF_FALSE, label_else)
        for stmt in node.then_body:
            self.visit(stmt)
        self.bytecode.add(OpCode.JUMP, label_end)
        self.bytecode.add_label(label_else)
        if node.else_body:
            if isinstance(node.else_body, list):
                for stmt in node.else_body:
                    self.visit(stmt)
            elif isinstance(node.else_body, IfNode):
                self.visit(node.else_body)
        self.bytecode.add_label(label_end)

    def visit_ForNode(self, node):
        start_label = f"for_start_{len(self.bytecode.code)}"
        end_label = f"for_end_{len(self.bytecode.code)}"
        self.visit(node.start)
        self.bytecode.add(OpCode.STORE_VAR, node.iterator)
        self.bytecode.add_label(start_label)
        self.bytecode.add(OpCode.LOAD_VAR, node.iterator)
        self.visit(node.end)
        self.bytecode.add(OpCode.LE)
        self.bytecode.add(OpCode.JUMP_IF_FALSE, end_label)
        for stmt in node.body:
            self.visit(stmt)
        self.bytecode.add(OpCode.LOAD_VAR, node.iterator)
        self.bytecode.add(OpCode.INC)
        self.bytecode.add(OpCode.STORE_VAR, node.iterator)
        self.bytecode.add(OpCode.JUMP, start_label)
        self.bytecode.add_label(end_label)

    def visit_WhileNode(self, node):
        start_label = f"while_start_{len(self.bytecode.code)}"
        end_label = f"while_end_{len(self.bytecode.code)}"
        self.bytecode.add_label(start_label)
        self.visit(node.condition)
        self.bytecode.add(OpCode.JUMP_IF_FALSE, end_label)
        for stmt in node.body:
            self.visit(stmt)
        self.bytecode.add(OpCode.JUMP, start_label)
        self.bytecode.add_label(end_label)

    def visit_FunctionNode(self, node):
        self.bytecode.add_label(node.name)
        start = len(self.bytecode.code)
        self.bytecode.functions[node.name] = {
            'params': node.params,
            'start': start,
            'name': node.name
        }
        for stmt in node.body:
            self.visit(stmt)
        self.bytecode.add(OpCode.PUSH, None)
        self.bytecode.add(OpCode.RETURN)

    def visit_ReturnNode(self, node):
        self.visit(node.value)
        self.bytecode.add(OpCode.RETURN)

    def visit_CallNode(self, node):
        if isinstance(node.name, str):
            name = node.name
        elif isinstance(node.name, IdentifierNode):
            name = node.name.name
        else:
            name = None

        # Cas spécial : lecture/écriture de fichier.
        if name in self.FILE_CALL_OPCODES:
            for arg in node.args:
                self.visit(arg)
            self.bytecode.add(self.FILE_CALL_OPCODES[name])
            return

        # Un IdentifierNode en position d'appel n'est un "nom de fonction
        # statique" que s'il correspond à une fonction RÉELLEMENT déclarée
        # (self.bytecode.functions, grâce au hoisting) ou à un builtin natif
        # de la VM. Sinon, c'est une variable locale qui CONTIENT une
        # référence de fonction et il faut la charger dynamiquement.
        if name is not None and (name in self.bytecode.functions or name in self.BUILTIN_FUNCTIONS):
            func_name = name
        else:
            func_name = None

        for arg in node.args:
            self.visit(arg)

        if func_name is not None:
            self.bytecode.add(OpCode.CALL, func_name)
        else:
            if isinstance(node.name, str):
                self.bytecode.add(OpCode.LOAD_VAR, node.name)
            elif isinstance(node.name, IdentifierNode):
                self.bytecode.add(OpCode.LOAD_VAR, node.name.name)
            else:
                self.visit(node.name)
            self.bytecode.add(OpCode.CALL)

    def visit_ClassNode(self, node):
        self.current_class_name = node.name
        self.current_class_parent = node.parent
        methods = {}
        for method in node.methods:
            func_name = f"{node.name}_{method.name}"
            func_node = FunctionNode(func_name, ['hetha'] + method.params, method.body)
            self.visit(func_node)
            methods[method.name] = {
                'func_name': func_name,
                'params': method.params,
            }
        self.bytecode.classes[node.name] = {
            'parent': node.parent,
            'methods': methods,
            'properties': node.properties
        }
        self.current_class_name = None
        self.current_class_parent = None

    def visit_NewNode(self, node):
        for arg in node.args:
            self.visit(arg)
        self.bytecode.add(OpCode.PUSH, node.class_name)
        self.bytecode.add(OpCode.NEW_OBJECT, len(node.args))

    def visit_MethodCallNode(self, node):
        for arg in node.args:
            self.visit(arg)
        if isinstance(node.object_name, str):
            self.bytecode.add(OpCode.LOAD_VAR, node.object_name)
        else:
            self.visit(node.object_name)
        self.bytecode.add(OpCode.CALL_METHOD, (node.method_name, len(node.args)))

    def visit_PropertyNode(self, node):
        if node.is_assignment:
            self.bytecode.add(OpCode.LOAD_VAR, "hetha")
            self.visit(node.value)
            self.bytecode.add(OpCode.STORE_PROPERTY, node.name)
            self.bytecode.add(OpCode.POP)
        else:
            if node.value is not None:
                self.visit(node.value)
            else:
                self.bytecode.add(OpCode.LOAD_VAR, "hetha")
            self.bytecode.add(OpCode.LOAD_PROPERTY, node.name)

    def visit_SuperNode(self, node):
        if self.current_class_parent:
            parent_func_name = f"{self.current_class_parent}_jdid"
            self.bytecode.add(OpCode.LOAD_VAR, "hetha")
            for arg in node.args:
                self.visit(arg)
            self.bytecode.add(OpCode.CALL, parent_func_name)
            self.bytecode.add(OpCode.POP)
        else:
            pass

    def visit_TryNode(self, node):
        catch_label = f"catch_{len(self.bytecode.code)}"
        finally_label = f"finally_{len(self.bytecode.code)}"
        self.bytecode.add(OpCode.TRY, catch_label)
        for stmt in node.try_body:
            self.visit(stmt)
        self.bytecode.add(OpCode.CATCH)
        self.bytecode.add(OpCode.JUMP, finally_label)
        self.bytecode.add_label(catch_label)
        if node.catch_var:
            self.bytecode.add(OpCode.STORE_VAR, node.catch_var)
        else:
            self.bytecode.add(OpCode.POP)
        for stmt in node.catch_body:
            self.visit(stmt)
        self.bytecode.add_label(finally_label)
        for stmt in node.finally_body:
            self.visit(stmt)

    def visit_BinOpNode(self, node):
        self.visit(node.left)
        self.visit(node.right)
        op_map = {
            "PLUS": OpCode.ADD,
            "MINUS": OpCode.SUB,
            "STAR": OpCode.MUL,
            "SLASH": OpCode.DIV,
            "MOD": OpCode.MOD,
            "EQUAL_EQUAL": OpCode.EQ,
            "NOT_EQUAL": OpCode.NE,
            "GREATER": OpCode.GT,
            "LESS": OpCode.LT,
            "GREATER_EQUAL": OpCode.GE,
            "LESS_EQUAL": OpCode.LE,
            "AND": OpCode.AND,
            "OR": OpCode.OR,
        }
        op_value = node.op.value if hasattr(node.op, 'value') else str(node.op)
        if op_value in op_map:
            self.bytecode.add(op_map[op_value])
        else:
            raise Exception(f"Unsupported binary operator: {op_value}")

    def visit_UnaryOpNode(self, node):
        self.visit(node.expr)
        op_value = node.op.value if hasattr(node.op, 'value') else str(node.op)
        if op_value == "MINUS":
            self.bytecode.add(OpCode.NEG)
        elif op_value == "NOT":
            self.bytecode.add(OpCode.NOT)
        else:
            raise Exception(f"Unsupported unary operator: {op_value}")

    def visit_NumberNode(self, node):
        idx = self.bytecode.add_constant(node.value)
        self.bytecode.add(OpCode.LOAD_CONST, idx)

    def visit_StringNode(self, node):
        idx = self.bytecode.add_constant(node.value)
        self.bytecode.add(OpCode.LOAD_CONST, idx)

    def visit_BooleanNode(self, node):
        idx = self.bytecode.add_constant(node.value)
        self.bytecode.add(OpCode.LOAD_CONST, idx)

    def visit_NullNode(self, node):
        self.bytecode.add(OpCode.PUSH, None)

    def visit_IdentifierNode(self, node):
        self.bytecode.add(OpCode.LOAD_VAR, node.name)

    def visit_ArrayAccessNode(self, node):
        if isinstance(node.array_name, IdentifierNode):
            self.visit(node.array_name)
        else:
            self.bytecode.add(OpCode.LOAD_VAR, node.array_name)
        self.visit(node.index)
        if node.is_assignment:
            self.visit(node.value)
            self.bytecode.add(OpCode.STORE_INDEX)
            self.bytecode.add(OpCode.POP)
        else:
            self.bytecode.add(OpCode.LOAD_INDEX)

    def visit_ArrayLiteralNode(self, node):
        for elem in node.elements:
            self.visit(elem)
        self.bytecode.add(OpCode.NEW_ARRAY, len(node.elements))

    def visit_BreakNode(self, node):
        pass

    def visit_ContinueNode(self, node):
        pass

    def visit_FileWriteNode(self, node):
        self.visit(node.filename)
        self.visit(node.content)
        self.bytecode.add(OpCode.WRITE_FILE)

    def visit_FileReadNode(self, node):
        self.visit(node.filename)
        self.bytecode.add(OpCode.READ_FILE)