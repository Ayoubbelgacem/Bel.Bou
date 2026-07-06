# src/parser/ast.py
class ASTNode:
    pass

class ProgramNode(ASTNode):
    def __init__(self, statements):
        self.statements = statements

class VariableNode(ASTNode):
    def __init__(self, name, type, value):
        self.name = name
        self.type = type
        self.value = value

class AssignmentNode(ASTNode):
    def __init__(self, name, value):
        self.name = name
        self.value = value

class PrintNode(ASTNode):
    def __init__(self, value):
        self.value = value

class InputNode(ASTNode):
    def __init__(self, prompt):
        self.prompt = prompt

class NumberNode(ASTNode):
    def __init__(self, value):
        self.value = value

class StringNode(ASTNode):
    def __init__(self, value):
        self.value = value

class BooleanNode(ASTNode):
    def __init__(self, value):
        self.value = value

class NullNode(ASTNode):
    def __init__(self):
        pass
    
    def __repr__(self):
        return "NullNode()"

class IdentifierNode(ASTNode):
    def __init__(self, name):
        self.name = name

class BinOpNode(ASTNode):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class IfNode(ASTNode):
    def __init__(self, condition, then_body, else_body=None):
        self.condition = condition
        self.then_body = then_body
        self.else_body = else_body

class ForNode(ASTNode):
    def __init__(self, iterator, start, end, body):
        self.iterator = iterator
        self.start = start
        self.end = end
        self.body = body

class WhileNode(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class FunctionNode(ASTNode):
    def __init__(self, name, params, body, return_type=None):
        self.name = name
        self.params = params
        self.body = body
        self.return_type = return_type

class ReturnNode(ASTNode):
    def __init__(self, value):
        self.value = value

class CallNode(ASTNode):
    def __init__(self, name, args):
        self.name = name
        self.args = args

class ClassNode(ASTNode):
    def __init__(self, name, parent, methods, properties):
        self.name = name
        self.parent = parent
        self.methods = methods
        self.properties = properties

class MethodNode(ASTNode):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body

class PropertyNode(ASTNode):
    def __init__(self, name, value, is_assignment=False):
        self.name = name
        self.value = value
        self.is_assignment = is_assignment

class MethodCallNode(ASTNode):
    def __init__(self, object_name, method_name, args):
        self.object_name = object_name
        self.method_name = method_name
        self.args = args

class NewNode(ASTNode):
    def __init__(self, class_name, args):
        self.class_name = class_name
        self.args = args

class ThisNode(ASTNode):
    pass

class SuperNode(ASTNode):
    def __init__(self, args):
        self.args = args

class TryNode(ASTNode):
    def __init__(self, try_body, catch_var, catch_body, finally_body):
        self.try_body = try_body
        self.catch_var = catch_var
        self.catch_body = catch_body
        self.finally_body = finally_body

class ImportNode(ASTNode):
    def __init__(self, module):
        self.module = module

class ArrayNode(ASTNode):
    def __init__(self, name, elements, type=None):
        self.name = name
        self.elements = elements
        self.type = type

class ArrayLiteralNode(ASTNode):
    def __init__(self, elements):
        self.elements = elements

class ArrayAccessNode(ASTNode):
    def __init__(self, array_name, index, value=None, is_assignment=False):
        self.array_name = array_name
        self.index = index
        self.value = value
        self.is_assignment = is_assignment

class FileWriteNode(ASTNode):
    def __init__(self, filename, content):
        self.filename = filename
        self.content = content

class FileReadNode(ASTNode):
    def __init__(self, filename):
        self.filename = filename
class UnaryOpNode(ASTNode):
    def __init__(self, op, expr):
        self.op = op
        self.expr = expr