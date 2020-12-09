from typing import Dict, List

from semantics.utils import Context, Scope, Type, TypeVariable
from cmp import visitor
import cool_ast


class TypesUpdater:
    def __init__(self,
                 context: Context,
                 scope: Scope,
                 functions,
                 attributes,
                 subst: Dict[str, Type],
                 errors: List[str]):
        self.context = context
        self.scope = scope
        self.functions = functions
        self.attributes = attributes
        self.subst = subst
        self.errors = errors
        self.current_type: Type = None
        self.change = False

    @visitor.on('node')
    def visit(self, node, scope, index):
        pass

    @visitor.when(cool_ast.ProgramNode)
    def visit(self, node: cool_ast.ProgramNode, scope: Scope, index: int):
        for i, class_declaration in enumerate(node.declarations, ):
            self.current_type = self.context.get_type(class_declaration.id)
            self.visit(class_declaration, scope.children[i], 0)

    @visitor.when(cool_ast.ClassDeclarationNode)
    def visit(self, node: cool_ast.ClassDeclarationNode, scope: Scope, index: int):
        attrs = [feature for feature in node.features if isinstance(feature, cool_ast.AttrDeclarationNode)]
        methods = [feature for feature in node.features if isinstance(feature, cool_ast.MethodDeclarationNode)]

        index = 0
        for attr in attrs:
            index = self.visit(attr, scope, index)

        for index, method in enumerate(methods, index):
            self.visit(method, scope.children[index], 0)

    @visitor.when(cool_ast.AttrDeclarationNode)
    def visit(self, node: cool_ast.AttrDeclarationNode, scope: Scope, index: int) -> int:
        if node.typex == 'AUTO_TYPE':
            att_type = self.attributes.get_attribute(self.current_type, node.id)
            try:
                node.typex = self.subst[att_type.name].name
                self.change = True
            except KeyError:
                pass

        if node.expression is not None:
            index = self.visit(node.expression, scope, index)
        return index

    @visitor.when(cool_ast.MethodDeclarationNode)
    def visit(self, node: cool_ast.MethodDeclarationNode, scope: Scope, index: int) -> int:
        function = self.functions.get_function(self.current_type, node.id)
        for param, param_type in zip(node.params, function.params_types):
            if param.typex == 'AUTO_TYPE':
                try:
                    param.typex = self.subst[param_type.name].name
                    self.change = True
                except KeyError:
                    pass

        if node.type == 'AUTO_TYPE':
            try:
                node.type = self.subst[function.return_type.name].name
                self.change = True
            except KeyError:
                pass

        if node.body is not None:
            index = self.visit(node.body, scope, index)
        return index

    @visitor.when(cool_ast.ConditionalNode)
    def visit(self, node: cool_ast.ConditionalNode, scope: Scope, index: int) -> int:
        index = self.visit(node.condition, scope, index)
        self.visit(node.then_body, scope.children[index], 0)
        self.visit(node.else_body, scope.children[index + 1], 0)
        return index + 1

    @visitor.when(cool_ast.CaseNode)
    def visit(self, node: cool_ast.CaseNode, scope: Scope, index: int) -> int:
        for index, option in enumerate(node.options, index):
            self.visit(option.expr, scope.children[index], 0)
        return index

    @visitor.when(cool_ast.LetNode)
    def visit(self, node: cool_ast.LetNode, scope: Scope, index: int) -> int:
        i = 0
        for var in node.var_decl_list:
            i = self.visit(var, scope.children[index], i)
        self.visit(node.in_expr, scope.children[index], i)
        return index + 1

    @visitor.when(cool_ast.AssignNode)
    def visit(self, node: cool_ast.AssignNode, scope: Scope, index: int) -> int:
        index = self.visit(node.expr, scope, index)
        return index

    @visitor.when(cool_ast.BlocksNode)
    def visit(self, node: cool_ast.BlocksNode, scope: Scope, index: int) -> int:
        i = 0
        for expr in node.expr_list:
            i = self.visit(expr, scope.children[index], i)
        return index + 1

    @visitor.when(cool_ast.MethodCallNode)
    def visit(self, node: cool_ast.MethodCallNode, scope: Scope, index: int) -> int:
        for index, args in enumerate(node.args, index):
            index = self.visit(args, scope, index)
        return index

    @visitor.when(cool_ast.LoopNode)
    def visit(self, node: cool_ast.LoopNode, scope: Scope, index: int) -> int:
        index = self.visit(node.condition, scope, index)
        i = self.visit(node.body, scope.children[index], 0)
        return index + 1

    @visitor.when(cool_ast.VarDeclarationNode)
    def visit(self, node: cool_ast.VarDeclarationNode, scope: Scope, index: int) -> int:
        if node.typex == 'AUTO_TYPE':
            var_info = scope.find_variable(node.id)
            if isinstance(var_info.type, TypeVariable):
                try:
                    node.typex = self.subst[var_info.type.name].name
                    self.change = True
                except KeyError:
                    pass
            else:
                node.typex = var_info.type.name

        if node.expr is not None:
            index = self.visit(node.expr, scope, index)
        return index

    @visitor.when(cool_ast.BinaryNode)
    def visit(self, node: cool_ast.BinaryNode, scope: Scope, index: int) -> int:
        index = self.visit(node.left, scope, index)
        index = self.visit(node.right, scope, index)
        return index

    @visitor.when(cool_ast.UnaryNode)
    def visit(self, node: cool_ast.NotNode, scope: Scope, index: int) -> int:
        index = self.visit(node.expr, scope, index)
        return index

    @visitor.when(cool_ast.AtomicNode)
    def visit(self, node: cool_ast.AtomicNode, scope: Scope, index: int) -> int:
        return index
