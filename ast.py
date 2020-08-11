from typing import List


class Node:
    pass


class ProgramNode(Node):
    def __init__(self, declarations: List['ClassDeclarationNode']):
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
        self.params: List[VarDeclarationNode] = params
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
        self.expr = expression


class AssignNode(ExpressionNode):
    def __init__(self, idx, expr):
        self.id = idx
        self.expr = expr


class MethodCallNode(ExpressionNode):
    def __init__(self, expr=None, typex=None, idx=None, args=None):
        self.expr = expr
        self.type = typex
        self.id = idx
        self.args = args


class ConditionalNode(ExpressionNode):
    def __init__(self, condition: ExpressionNode, then_body: ExpressionNode, else_body: ExpressionNode):
        self.condition = condition
        self.then_body = then_body
        self.else_body = else_body


class LoopNode(ExpressionNode):
    def __init__(self, condition: ExpressionNode, body: ExpressionNode):
        self.condition = condition
        self.body = body


class LetNode(ExpressionNode):
    def __init__(self, var_decl_list: List[VarDeclarationNode], in_expr: ExpressionNode):
        self.var_decl_list = var_decl_list
        self.in_expr = in_expr


class CaseNode(ExpressionNode):
    def __init__(self, case_expr, options):
        self.case_expr = case_expr
        self.options: List[CaseOptionNode] = options


class CaseOptionNode(ExpressionNode):
    def __init__(self, idx, typex, expr):
        self.id = idx
        self.type = typex
        self.expr = expr


class BlocksNode(ExpressionNode):
    def __init__(self, expr_list):
        self.expr_list = expr_list


class AtomicNode(ExpressionNode):
    def __init__(self, lex):
        self.lex = lex


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


class ComparerNode(BinaryNode):
    pass


class ArithmeticNode(BinaryNode):
    pass


class ConstantNumNode(AtomicNode):
    pass


class StringNode(AtomicNode):
    pass


class VariableNode(AtomicNode):
    pass


class InstantiateNode(AtomicNode):
    pass


class PlusNode(ArithmeticNode):
    pass


class MinusNode(ArithmeticNode):
    pass


class StarNode(ArithmeticNode):
    pass


class DivNode(ArithmeticNode):
    pass


class LessNode(ComparerNode):
    pass


class LessOrEqualNode(ComparerNode):
    pass


class EqualsNode(ComparerNode):
    pass

# TODO:  ~ node
