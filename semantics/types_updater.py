from typing import Dict, List, Optional

from utils import Context, Scope, Type, FunctionType, TypeVariable
from cmp import visitor
import ast


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

    def get_function(self, typex: Type, func_name: str) -> Optional[FunctionType]:
        return self.aux_get_function(typex, typex, func_name)

    def aux_get_function(self, init_type: Type, typex: Type, func_name: str) -> Optional[FunctionType]:
        try:
            func_type = self.functions[typex.name, func_name]
            params_type = [init_type if param.name == 'SELF_TYPE' else param for param in func_type.params_types]
            return_type = init_type if func_type.return_type.name == 'SELF_TYPE' else func_type.return_type
            return FunctionType(tuple(params_type), return_type)
        except KeyError:
            if typex.parent is not None:
                return self.aux_get_function(init_type, typex.parent, func_name)

    def get_attribute(self, typex: Type, attr_name) -> Optional[Type]:
        return self.aux_get_attribute(typex, typex, attr_name)

    def aux_get_attribute(self, init_type: Type, typex: Type, attr_name) -> Optional[Type]:
        try:
            att_type = self.attributes[typex.name, attr_name]
            return init_type if att_type.name == 'SELF_TYPE' else att_type
        except KeyError:
            if typex.parent is not None:
                return self.aux_get_attribute(init_type, typex.parent, attr_name)

    @visitor.on('node')
    def visit(self, node, scope, index):
        pass

    @visitor.when(ast.ProgramNode)
    def visit(self, node: ast.ProgramNode, scope: Scope, index: int):
        for i, class_declaration in enumerate(node.declarations, ):
            self.current_type = self.context.get_type(class_declaration.id)
            self.visit(class_declaration, scope.children[i], 0)

    @visitor.when(ast.ClassDeclarationNode)
    def visit(self, node: ast.ClassDeclarationNode, scope: Scope, index: int):
        attrs = [feature for feature in node.features if isinstance(feature, ast.AttrDeclarationNode)]
        methods = [feature for feature in node.features if isinstance(feature, ast.MethodDeclarationNode)]

        index = 0
        for attr in attrs:
            index = self.visit(attr, scope, index)

        for index, method in enumerate(methods, index):
            self.visit(method, scope.children[index], 0)

    @visitor.when(ast.AttrDeclarationNode)
    def visit(self, node: ast.AttrDeclarationNode, scope: Scope, index: int) -> int:
        if node.typex == 'AUTO_TYPE':
            att_type = self.get_attribute(self.current_type, node.id)
            node.typex = self.subst[att_type.name].name

        if node.expression is not None:
            index = self.visit(node.expression, scope, index)
        return index

    @visitor.when(ast.MethodDeclarationNode)
    def visit(self, node: ast.MethodDeclarationNode, scope: Scope, index: int) -> int:
        function = self.get_function(self.current_type, node.id)
        for param, param_type in zip(node.params,function.params_types):
            if param.typex == 'AUTO_TYPE':
                param.typex = self.subst[param_type.name].name

        if node.type == 'AUTO_TYPE':
            node.type = self.subst[function.return_type.name].name

        if node.body is not None:
            index = self.visit(node.body, scope, index)
        return index

    @visitor.when(ast.ConditionalNode)
    def visit(self, node: ast.ConditionalNode, scope: Scope, index: int) -> int:
        index = self.visit(node.condition, scope, index)
        self.visit(node.then_body, scope.children[index], 0)
        self.visit(node.else_body, scope.children[index + 1], 0)
        return index + 1

    @visitor.when(ast.CaseNode)
    def visit(self, node: ast.CaseNode, scope: Scope, index: int) -> int:
        for index, option in enumerate(node.options, index):
            self.visit(option.expr, scope.children[index], 0)
        return index

    @visitor.when(ast.LetNode)
    def visit(self, node: ast.LetNode, scope: Scope, index: int) -> int:
        i = 0
        for var in node.var_decl_list:
            i = self.visit(var, scope.children[index], i)
        return index + 1

    @visitor.when(ast.AssignNode)
    def visit(self, node: ast.AssignNode, scope: Scope, index: int) -> int:
        index = self.visit(node.expr, scope, index)
        return index

    @visitor.when(ast.BlocksNode)
    def visit(self, node: ast.BlocksNode, scope: Scope, index: int) -> int:
        i = 0
        for expr in node.expr_list:
            i = self.visit(expr, scope.children[index], i)
        return index + 1

    @visitor.when(ast.MethodCallNode)
    def visit(self, node: ast.MethodCallNode, scope: Scope, index: int) -> int:
        for index, args in enumerate(node.args, index):
            index = self.visit(args, scope, index)
        return index

    @visitor.when(ast.LoopNode)
    def visit(self, node: ast.LoopNode, scope: Scope, index: int) -> int:
        index = self.visit(node.condition, scope, index)
        i = 0
        i = self.visit(node.body, scope.children[index], 0)
        return index + 1

    @visitor.when(ast.VarDeclarationNode)
    def visit(self, node: ast.VarDeclarationNode, scope: Scope, index: int) -> int:
        if node.typex == 'AUTO_TYPE':
            var_info = scope.find_variable(node.id)
            node.typex = self.subst[var_info.type.name].name

        if node.expr is not None:
            index = self.visit(node.expr, scope, index)
        return index

    @visitor.when(ast.BinaryNode)
    def visit(self, node: ast.BinaryNode, scope: Scope, index: int) -> int:
        index = self.visit(node.left, scope, index)
        index = self.visit(node.right, scope, index)
        return index

    @visitor.when(ast.NotNode)
    def visit(self, node: ast.NotNode, scope: Scope, index: int) -> int:
        index = self.visit(node.lex, scope, index)
        return index

    @visitor.when(ast.IsVoidNode)
    def visit(self, node: ast.IsVoidNode, scope: Scope, index: int) -> int:
        index = self.visit(node.lex, scope, index)
        return index

    @visitor.when(ast.ConstantNumNode)
    def visit(self, node: ast.ConstantNumNode, scope: Scope, index: int) -> int:
        return index

    @visitor.when(ast.StringNode)
    def visit(self, node: ast.StringNode, scope: Scope, index: int) -> int:
        return index

    @visitor.when(ast.BooleanNode)
    def visit(self, node: ast.BooleanNode, scope: Scope, index: int) -> int:
        return index

    @visitor.when(ast.InstantiateNode)
    def visit(self, node: ast.InstantiateNode, scope: Scope, index: int) -> int:
        return index



