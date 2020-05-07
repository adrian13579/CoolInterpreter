class Node:
    pass


class ProgramNode(Node):
    def __init__(self, declarations):
        self.declarations = declarations


class DeclarationNode(Node):
    pass


class ExpressionNode(Node):
    pass


class ClassDeclarationNode(DeclarationNode):
    def __init__(self, idx, features, parent=None):
        self.id = idx
        self.parent = parent
        self.features = features


class MethodDeclarationNode(DeclarationNode):
    def __init__(self, idx, params, return_type, body):
        self.id = idx
        self.params = params
        self.type = return_type
        self.body = body


class AttrDeclarationNode(DeclarationNode):
    def __init__(self, idx, typex, expression=None):
        self.id = idx
        self.typex = typex
        self.expression = expression


class VarDeclarationNode(ExpressionNode):
    def __init__(self, idx, typex, expression=None):
        self.id = idx
        self.typex = typex
        self.expression = expression


class AssignNode(ExpressionNode):
    def __init__(self, idx, expr):
        self.id = idx
        self.expr = expr


class MethodCallNode(ExpressionNode):
    def __init__(self, idx, args):
        self.id = idx
        self.args = args


class MethodCallTypeNode(ExpressionNode):
    def __init__(self, object_expr, typex, idx, args):
        self.id = idx
        self.args = args
        self.object_expr = object_expr
        self.typex = typex


class MethodCallNoTypeNode(ExpressionNode):
    def __init__(self, object_expr, idx, args):
        self.idx = idx
        self.args = args
        self.object_expr = object_expr


class ConditonalNode(ExpressionNode):
    def __init__(self, condition, then_body, else_body):
        self.condition = condition
        self.then_body = then_body
        self.else_body = else_body


class LoopNode(ExpressionNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body


class LetNode(ExpressionNode):
    def __init__(self, var_decl_list, in_expr):
        self.var_decl_list = var_decl_list
        self.in_expr = in_expr


class CaseNode(ExpressionNode):
    def __init__(self, case_expr, var_decl_list):
        self.case_expr = case_expr
        self.var_decl_list = var_decl_list


class AtomicNode(ExpressionNode):
    def __init__(self, expr):
        self.expr = expr


class IsVoidNode(AtomicNode):
    pass


class NotNode(AtomicNode):
    pass


class BooleanNode(AtomicNode):
    pass


class BinaryNode(ExpressionNode):
    def __init__(self, left, right):
        self.left = left
        self.right = right


class ConstantNumNode(AtomicNode):
    pass


class VariableNode(AtomicNode):
    pass


class InstantiateNode(AtomicNode):
    pass


class PlusNode(BinaryNode):
    pass


class MinusNode(BinaryNode):
    pass


class StarNode(BinaryNode):
    pass


class DivNode(BinaryNode):
    pass


class LessNode(BinaryNode):
    pass


class LessOrEqualNode(BinaryNode):
    pass


class EqualsNode(BinaryNode):
    pass

# TODO:  ~ node
