class ASTNode:
    pass

class ProgramNode(ASTNode):
    def __init__(self, statements):
        self.statements = statements


class VariableNode(ASTNode):
    def __init__(self, name, type_name, value):
        self.name = name
        self.type_name = type_name
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


class IfNode:
    def __init__(self, condition, then_body, else_body=None):
        self.condition = condition
        self.then_body = then_body
        self.else_body = else_body


class ForNode:
    def __init__(self, iterator, start, end, body):
        self.iterator = iterator
        self.start = start
        self.end = end
        self.body = body


class WhileNode:
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body


class FunctionNode:
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body


class ReturnNode:
    def __init__(self, value):
        self.value = value


class CallNode:
    def __init__(self, name, args):
        self.name = name
        self.args = args


class ClassNode:
    def __init__(self, name, parent, methods, properties):
        self.name = name
        self.parent = parent
        self.methods = methods
        self.properties = properties


class MethodNode:
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body


class NewNode:
    def __init__(self, class_name, args, target=None):
        self.class_name = class_name
        self.args = args
        self.target = target


class MethodCallNode:
    def __init__(self, object_name, method_name, args):
        self.object_name = object_name
        self.method_name = method_name
        self.args = args


class PropertyNode:
    def __init__(self, name, value, is_assignment=False):
        self.name = name
        self.value = value
        self.is_assignment = is_assignment


class ArrayLiteralNode:
    def __init__(self, elements):
        self.elements = elements


class ArrayAccessNode:
    def __init__(self, array_name, index, value=None, is_assignment=False):
        self.array_name = array_name
        self.index = index
        self.value = value
        self.is_assignment = is_assignment


class TryNode:
    def __init__(self, try_body, catch_var, catch_body, finally_body):
        self.try_body = try_body
        self.catch_var = catch_var
        self.catch_body = catch_body
        self.finally_body = finally_body


class ImportNode:
    def __init__(self, module):
        self.module = module


class FileWriteNode:
    def __init__(self, filename, content):
        self.filename = filename
        self.content = content


class FileReadNode:
    def __init__(self, filename):
        self.filename = filename


class BinOpNode:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right


class UnaryOpNode:
    def __init__(self, op, expr):
        self.op = op
        self.expr = expr


class NumberNode:
    def __init__(self, value):
        self.value = value


class StringNode:
    def __init__(self, value):
        self.value = value


class BooleanNode:
    def __init__(self, value):
        self.value = value


class NullNode:
    pass


class IdentifierNode:
    def __init__(self, name):
        self.name = name


class SuperNode:
    def __init__(self, args):
        self.args = args


class BreakNode:
    pass


class ContinueNode:
    pass