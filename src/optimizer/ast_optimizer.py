"""
Optimiseur d'AST pour Bou.Bel
Effectue des transformations statiques pour accélérer l'exécution
"""

from src.parser.ast import (
    ProgramNode, VariableNode, AssignmentNode, PrintNode, InputNode,
    IfNode, ForNode, WhileNode, FunctionNode, ReturnNode, CallNode,
    ClassNode, MethodNode, NewNode, MethodCallNode, PropertyNode,
    ArrayLiteralNode, ArrayAccessNode, TryNode, ImportNode,
    FileWriteNode, FileReadNode, BinOpNode, UnaryOpNode,
    NumberNode, StringNode, BooleanNode, NullNode, IdentifierNode,
    SuperNode, BreakNode, ContinueNode, ASTNode
)


class ASTOptimizer:
    """
    Optimiseur d'AST :
    - Constant folding (réduction des constantes)
    - Dead code elimination (suppression de code inutile)
    - Simplification des conditions constantes
    """

    def __init__(self, debug=False):
        self.debug = debug

    def optimize(self, node):
        """Point d'entrée : optimise l'AST complet"""
        if isinstance(node, ProgramNode):
            new_statements = []
            for stmt in node.statements:
                opt_stmt = self._optimize_node(stmt)
                if opt_stmt is not None:
                    # Aplatir si c'est une liste
                    if isinstance(opt_stmt, list):
                        new_statements.extend(opt_stmt)
                    else:
                        new_statements.append(opt_stmt)
            return ProgramNode(new_statements)
        else:
            return self._optimize_node(node)

    def _optimize_node(self, node):
        """Optimise un nœud individuel (visiteur)"""
        if node is None:
            return None

        method_name = f'_optimize_{type(node).__name__}'
        method = getattr(self, method_name, None)
        if method:
            result = method(node)
            if self.debug:
                print(f"Optimized {type(node).__name__} -> {type(result).__name__ if result else 'None'}")
            return result
        else:
            # Pour les autres nœuds, on visite récursivement leurs enfants
            return self._visit_children(node)

    def _visit_children(self, node):
        """Visite récursivement les attributs qui sont des ASTNode ou des listes"""
        for attr_name in dir(node):
            if attr_name.startswith('_'):
                continue
            attr = getattr(node, attr_name)
            if isinstance(attr, ASTNode):
                # Optimiser le nœud enfant
                new_attr = self._optimize_node(attr)
                setattr(node, attr_name, new_attr)
            elif isinstance(attr, list):
                # Optimiser chaque élément de la liste
                new_list = []
                for item in attr:
                    if isinstance(item, ASTNode):
                        new_item = self._optimize_node(item)
                        if new_item is not None:
                            # Aplatir si c'est une liste
                            if isinstance(new_item, list):
                                new_list.extend(new_item)
                            else:
                                new_list.append(new_item)
                    else:
                        new_list.append(item)
                setattr(node, attr_name, new_list)
        return node

    # ---------- Optimisations spécifiques ----------

    def _optimize_NumberNode(self, node):
        return node

    def _optimize_StringNode(self, node):
        return node

    def _optimize_BooleanNode(self, node):
        return node

    def _optimize_IdentifierNode(self, node):
        return node

    def _optimize_NullNode(self, node):
        return node

    def _optimize_ArrayLiteralNode(self, node):
        # Optimiser chaque élément
        new_elements = [self._optimize_node(elem) for elem in node.elements]
        return ArrayLiteralNode(new_elements)

    def _optimize_ArrayAccessNode(self, node):
        index = self._optimize_node(node.index)
        if node.is_assignment:
            value = self._optimize_node(node.value)
            return ArrayAccessNode(node.array_name, index, value, True)
        return ArrayAccessNode(node.array_name, index)

    def _optimize_BinOpNode(self, node):
        left = self._optimize_node(node.left)
        right = self._optimize_node(node.right)

        # Constant folding si les deux sont des nombres
        if isinstance(left, NumberNode) and isinstance(right, NumberNode):
            op = node.op.value if hasattr(node.op, 'value') else str(node.op)
            if op in ('PLUS', '+'):
                return NumberNode(left.value + right.value)
            elif op in ('MINUS', '-'):
                return NumberNode(left.value - right.value)
            elif op in ('STAR', '*'):
                return NumberNode(left.value * right.value)
            elif op in ('SLASH', '/'):
                if right.value == 0:
                    return BinOpNode(left, node.op, right)
                return NumberNode(left.value / right.value)
            elif op in ('MOD', '%'):
                if right.value == 0:
                    return BinOpNode(left, node.op, right)
                return NumberNode(left.value % right.value)
            elif op in ('EQUAL_EQUAL', '=='):
                return BooleanNode(left.value == right.value)
            elif op in ('NOT_EQUAL', '!='):
                return BooleanNode(left.value != right.value)
            elif op in ('GREATER', '>'):
                return BooleanNode(left.value > right.value)
            elif op in ('LESS', '<'):
                return BooleanNode(left.value < right.value)
            elif op in ('GREATER_EQUAL', '>='):
                return BooleanNode(left.value >= right.value)
            elif op in ('LESS_EQUAL', '<='):
                return BooleanNode(left.value <= right.value)
            elif op in ('AND', '&&'):
                return BooleanNode(left.value and right.value)
            elif op in ('OR', '||'):
                return BooleanNode(left.value or right.value)

        # Si les deux sont des booléens, réduire AND/OR
        if isinstance(left, BooleanNode) and isinstance(right, BooleanNode):
            op = node.op.value if hasattr(node.op, 'value') else str(node.op)
            if op in ('AND', '&&'):
                return BooleanNode(left.value and right.value)
            elif op in ('OR', '||'):
                return BooleanNode(left.value or right.value)

        return BinOpNode(left, node.op, right)

    def _optimize_UnaryOpNode(self, node):
        expr = self._optimize_node(node.expr)
        op = node.op.value if hasattr(node.op, 'value') else str(node.op)
        if isinstance(expr, NumberNode):
            if op in ('MINUS', '-'):
                return NumberNode(-expr.value)
        if isinstance(expr, BooleanNode):
            if op in ('NOT', '!'):
                return BooleanNode(not expr.value)
        return UnaryOpNode(node.op, expr)

    def _optimize_IfNode(self, node):
        condition = self._optimize_node(node.condition)
        # Optimiser les corps en listes
        then_body = []
        for stmt in node.then_body:
            opt_stmt = self._optimize_node(stmt)
            if opt_stmt is not None:
                if isinstance(opt_stmt, list):
                    then_body.extend(opt_stmt)
                else:
                    then_body.append(opt_stmt)

        else_body = []
        if node.else_body:
            if isinstance(node.else_body, list):
                for stmt in node.else_body:
                    opt_stmt = self._optimize_node(stmt)
                    if opt_stmt is not None:
                        if isinstance(opt_stmt, list):
                            else_body.extend(opt_stmt)
                        else:
                            else_body.append(opt_stmt)
            else:
                # Si l'else_body est un seul nœud (ex: un autre IfNode)
                opt_stmt = self._optimize_node(node.else_body)
                if opt_stmt is not None:
                    if isinstance(opt_stmt, list):
                        else_body.extend(opt_stmt)
                    else:
                        else_body.append(opt_stmt)

        # Si la condition est constante, on peut supprimer une branche
        if isinstance(condition, BooleanNode):
            if condition.value:
                # Garder seulement then_body
                return then_body if then_body else None
            else:
                # Garder seulement else_body
                return else_body if else_body else None

        # Sinon, créer un nouveau IfNode avec les corps optimisés
        return IfNode(condition, then_body, else_body if else_body else None)

    def _optimize_WhileNode(self, node):
        condition = self._optimize_node(node.condition)
        body = []
        for stmt in node.body:
            opt_stmt = self._optimize_node(stmt)
            if opt_stmt is not None:
                if isinstance(opt_stmt, list):
                    body.extend(opt_stmt)
                else:
                    body.append(opt_stmt)

        # Si condition est toujours false, supprimer la boucle
        if isinstance(condition, BooleanNode) and not condition.value:
            return None

        return WhileNode(condition, body)

    def _optimize_ForNode(self, node):
        start = self._optimize_node(node.start)
        end = self._optimize_node(node.end)
        body = []
        for stmt in node.body:
            opt_stmt = self._optimize_node(stmt)
            if opt_stmt is not None:
                if isinstance(opt_stmt, list):
                    body.extend(opt_stmt)
                else:
                    body.append(opt_stmt)
        return ForNode(node.iterator, start, end, body)

    def _optimize_ReturnNode(self, node):
        value = self._optimize_node(node.value)
        return ReturnNode(value)

    def _optimize_PrintNode(self, node):
        value = self._optimize_node(node.value)
        return PrintNode(value)

    def _optimize_AssignmentNode(self, node):
        value = self._optimize_node(node.value)
        return AssignmentNode(node.name, value)

    def _optimize_VariableNode(self, node):
        value = self._optimize_node(node.value)
        return VariableNode(node.name, node.type_name, value)

    def _optimize_CallNode(self, node):
        args = [self._optimize_node(arg) for arg in node.args]
        return CallNode(node.name, args)

    def _optimize_MethodCallNode(self, node):
        args = [self._optimize_node(arg) for arg in node.args]
        return MethodCallNode(node.object_name, node.method_name, args)

    def _optimize_NewNode(self, node):
        args = [self._optimize_node(arg) for arg in node.args]
        return NewNode(node.class_name, args, node.target)

    def _optimize_PropertyNode(self, node):
        if node.is_assignment:
            value = self._optimize_node(node.value)
            return PropertyNode(node.name, value, True)
        return node

    def _optimize_TryNode(self, node):
        try_body = []
        for stmt in node.try_body:
            opt_stmt = self._optimize_node(stmt)
            if opt_stmt is not None:
                if isinstance(opt_stmt, list):
                    try_body.extend(opt_stmt)
                else:
                    try_body.append(opt_stmt)
        catch_body = []
        for stmt in node.catch_body:
            opt_stmt = self._optimize_node(stmt)
            if opt_stmt is not None:
                if isinstance(opt_stmt, list):
                    catch_body.extend(opt_stmt)
                else:
                    catch_body.append(opt_stmt)
        finally_body = []
        for stmt in node.finally_body:
            opt_stmt = self._optimize_node(stmt)
            if opt_stmt is not None:
                if isinstance(opt_stmt, list):
                    finally_body.extend(opt_stmt)
                else:
                    finally_body.append(opt_stmt)
        return TryNode(try_body, node.catch_var, catch_body, finally_body)

    def _optimize_FileWriteNode(self, node):
        filename = self._optimize_node(node.filename)
        content = self._optimize_node(node.content)
        return FileWriteNode(filename, content)

    def _optimize_FileReadNode(self, node):
        filename = self._optimize_node(node.filename)
        return FileReadNode(filename)

    def _optimize_SuperNode(self, node):
        args = [self._optimize_node(arg) for arg in node.args]
        return SuperNode(args)

    # Les nœuds suivants sont laissés tels quels (pas d'optimisation)
    def _optimize_ClassNode(self, node):
        return node

    def _optimize_MethodNode(self, node):
        return node

    def _optimize_ImportNode(self, node):
        return node

    def _optimize_BreakNode(self, node):
        return node

    def _optimize_ContinueNode(self, node):
        return node

    def _optimize_InputNode(self, node):
        return node