from typing import List
from cmp import visitor
from semantics import Context
import ast
from utils import CoolObject, Scope, VoidObject, Attribute


class Interpreter:
    def __init__(self, context: Context):
        self.context = context
        self.stack: List[CoolObject] = []
        self.current_object: CoolObject = None

    @visitor.on('node')
    def visit(self, node, scope: Scope):
        pass

    @visitor.when(ast.ProgramNode)
    def visit(self, node: ast.ProgramNode, scope: Scope) -> None:
        for class_decl in node.declarations:
            self.visit(class_decl, scope)

        self.current_object = CoolObject(self.context.get_type('Main'))
        scope.define_variable('self', self.current_object.type, self.current_object)
        self.visit(self.current_object.get_method('main', self.current_object.type).expression, scope)

    @visitor.when(ast.ClassDeclarationNode)
    def visit(self, node: ast.ClassDeclarationNode, scope: Scope) -> None:
        attributes = [feature for feature in node.features if isinstance(feature, ast.AttrDeclarationNode)]
        methods = [feature for feature in node.features if isinstance(feature, ast.MethodDeclarationNode)]

        current_type = self.context.get_type(node.id)
        for attr in attributes:
            type_attr = current_type.get_attribute(attr.id)
            type_attr.expression = attr.expression

        for method in methods:
            type_method = current_type.get_method(method.id)
            type_method.expression = method.body

    @visitor.when(ast.BlocksNode)
    def visit(self, node: ast.BlocksNode, scope: Scope) -> CoolObject:
        cool_object = VoidObject()
        for expr in node.expr_list:
            cool_object = self.visit(expr, scope)
        return cool_object

    @visitor.when(ast.ConditonalNode)
    def visit(self, node: ast.ConditonalNode, scope: Scope) -> CoolObject:
        condition = self.visit(node.condition, scope)
        if condition.value:
            return self.visit(node.then_body, scope)
        return self.visit(node.else_body, scope)

    @visitor.when(ast.LoopNode)
    def visit(self, node: ast.LoopNode, scope: Scope) -> VoidObject:
        child_scope = scope.create_child()
        while self.visit(node.condition, child_scope).value:
            self.visit(node.body, child_scope)
        return VoidObject()

    @visitor.when(ast.LetNode)
    def visit(self, node: ast.LetNode, scope: Scope) -> CoolObject:
        child_scope = scope.create_child()
        for var in node.var_decl_list:
            var_type = self.context.get_type(var.typex)
            var_object = self.visit(var.expr, child_scope)
            child_scope.define_variable(var.id, var_type, var_object)
        return self.visit(node.in_expr, child_scope)

    @visitor.when(ast.MethodCallNode)
    def visit(self, node: ast.MethodCallNode, scope: Scope) -> CoolObject:
        expr = self.visit(node.expr, scope) if node.expr is not None else self.current_object
        typex = self.context.get_type(node.type) if node.type is not None else expr.type
        method = expr.get_method(node.id, typex)

        new_scope = Scope()
        new_scope.define_variable('self', expr)
        for param_name, param_type, arg in zip(method.param_names, method.param_types, node.args):
            new_scope.define_variable(vname=param_name, vtype=param_type, value=self.visit(arg, scope))

        self.stack.append(self.current_object)
        self.current_object = expr
        method_return = self.visit(method.expression, new_scope)
        self.current_object = self.stack.pop()
        return method_return

    @visitor.when(ast.MethodDeclarationNode)
    def visit(self, node: ast.MethodDeclarationNode, scope: Scope) -> CoolObject:
        return VoidObject() if node.body is None else self.visit(node.body, scope)

    @visitor.when(ast.VariableNode)
    def visit(self, node: ast.VariableNode, scope: Scope) -> CoolObject:
        var = scope.find_variable(node.lex)
        if var is None:
            objectx = self.current_object.get_attribute(node.lex)
            if isinstance(objectx, Attribute):
                objectx = self.visit(objectx.expression, Scope())
                self.current_object.set_attibute(node.lex, objectx)
            return objectx
        return var.value

    @visitor.when(ast.AssignNode)
    def visit(self, node: ast.AssignNode, scope: Scope) -> CoolObject:
        expr = self.visit(node.expr, scope)
        var = scope.find_variable(node.id)
        if var is not None:
            var.value = expr
        else:
            self.current_object.set_attibute(node.id, expr)
        return expr

    @visitor.when(ast.ConstantNumNode)
    def visit(self, node: ast.ConstantNumNode, scope: Scope) -> CoolObject:
        return CoolObject(self.context.get_type('Int'), int(node.lex))

    @visitor.when(ast.InstantiateNode)
    def visit(self, node: ast.InstantiateNode, scope: Scope) -> CoolObject:
        return CoolObject(self.context.get_type(node.lex))

    @visitor.when(ast.BooleanNode)
    def visit(self, node: ast.BooleanNode, scope: Scope) -> CoolObject:
        return CoolObject(self.context.get_type('Bool'), node.lex == 'true')

    @visitor.when(ast.StringNode)
    def visit(self, node: ast.StringNode, scope: Scope) -> CoolObject:
        return CoolObject(self.context.get_type('String'), node.lex)

    @visitor.when(ast.BinaryNode)
    def visit(self, node: ast.BinaryNode, scope: Scope) -> CoolObject:
        left = self.visit(node.left, scope)
        right = self.visit(node.right, scope)
        a = self.operate(node, left.value, right.value)
        print(a.value)
        return a
        # return self.operate(node, left.value, right.value)

    @visitor.on('node')
    def operate(self, node, left, right) -> CoolObject:
        pass

    @visitor.when(ast.PlusNode)
    def operate(self, node, left, right):
        return CoolObject(self.context.get_type('Int'), left + right)

    @visitor.when(ast.MinusNode)
    def operate(self, node, left, right):
        return CoolObject(self.context.get_type('Int'), left - right)

    @visitor.when(ast.StarNode)
    def operate(self, node, left, right):
        return CoolObject(self.context.get_type('Int'), left * right)

    @visitor.when(ast.DivNode)
    def operate(self, node, left, right):
        return CoolObject(self.context.get_type('Int'), left / right)

    @visitor.when(ast.EqualsNode)
    def operate(self, node, left, right):
        return CoolObject(self.context.get_type('Bool'), left == right)

    @visitor.when(ast.LessOrEqualNode)
    def operate(self, node, left, right):
        return CoolObject(self.context.get_type('Bool'), left <= right)

    @visitor.when(ast.LessNode)
    def operate(self, node, left, right):
        return CoolObject(self.context.get_type('Bool'), left < right)
