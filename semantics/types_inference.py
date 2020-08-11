from typing import Dict, List, Optional, Set
from collections import OrderedDict
import ast
from cmp import visitor
from utils import Context, Type, TypeVariable, FunctionType, Method, ErrorType, Scope, SemanticError, AttrMap, MethodMap
import typing

TypeGraph = typing.OrderedDict[Type, Set[Type]]


class TypeInferencer:
    def __init__(self, context: Context, scope: Scope, errors: List[str]):
        self.errors = errors
        self.context = context
        self.scope = scope

        self.substitutions: Dict[str, Type] = {}
        self.types_graph: TypeGraph = OrderedDict()

        self.functions: MethodMap = MethodMap(context)
        self.attributes: AttrMap = AttrMap(context)

        self.current_type: Type = None
        self.current_method: Method = None

    @visitor.on('node')
    def visit(self, node, scope: Scope):
        pass

    @visitor.when(ast.ProgramNode)
    def visit(self, node: ast.ProgramNode, scope: Scope) -> None:
        for class_decl in node.declarations:
            self.current_type = self.context.get_type(class_decl.id)
            self.visit(class_decl, scope.create_child())

        self.dfs_inference()
        print('Hello World!')

    @visitor.when(ast.ClassDeclarationNode)
    def visit(self, node: ast.ClassDeclarationNode, scope: Scope) -> None:
        attrs = [feature for feature in node.features if isinstance(feature, ast.AttrDeclarationNode)]
        methods = [feature for feature in node.features if isinstance(feature, ast.MethodDeclarationNode)]

        scope.define_variable('self', self.current_type)
        for attr in attrs:
            typex = self.visit(attr, scope)

        for method in methods:
            self.current_method = self.current_type.get_method(method.id)
            typex = self.visit(method, scope.create_child())

    @visitor.when(ast.AttrDeclarationNode)
    def visit(self, node: ast.AttrDeclarationNode, scope: Scope) -> Type:
        if node.expression is not None:
            expr_type = self.visit(node.expression, scope.create_child())
            attr_type = self.attributes.get_attribute(self.current_type, node.id)
            self.unify(attr_type, expr_type)
            return attr_type
        else:
            return self.attributes.get_attribute(self.current_type, node.id)

    @visitor.when(ast.MethodDeclarationNode)
    def visit(self, node: ast.MethodDeclarationNode, scope: Scope) -> FunctionType:
        function = self.functions.get_function(self.current_type, self.current_method.name)
        for param_type, param in zip(function.params_types, node.params):
            scope.define_variable(param.id, param_type)

        body_type = self.visit(node.body, scope)
        self.unify(function.return_type, body_type)
        return function

    @visitor.when(ast.ConditionalNode)
    def visit(self, node: ast.ConditionalNode, scope: Scope):
        bool_type = self.context.get_type('Bool')
        cond_type = self.visit(node.condition, scope)
        self.unify(bool_type, cond_type)
        then_type = self.visit(node.then_body, scope.create_child())
        else_type = self.visit(node.else_body, scope.create_child())
        return self.context.get_type('Object')

    @visitor.when(ast.CaseNode)
    def visit(self, node: ast.CaseNode, scope: Scope):
        _ = self.visit(node.case_expr, scope)
        types: List[Type] = []
        for option in node.options:
            child_scope = scope.create_child()
            child_scope.define_variable(option.id, self.context.get_type(option.type))
            types.append(self.visit(option.expr, child_scope))
        return self.context.get_type('Object')

    @visitor.when(ast.LetNode)
    def visit(self, node: ast.LetNode, scope: Scope):
        child_scope = scope.create_child()
        for var in node.var_decl_list:
            var_type = self.visit(var, child_scope)
        body_type = self.visit(node.in_expr, child_scope)
        return body_type

    @visitor.when(ast.AssignNode)
    def visit(self, node: ast.AssignNode, scope: Scope):
        expr_type = self.visit(node.expr, scope)
        var_info = scope.find_variable(node.id)
        if var_info is None:  # check if is an attribute
            var_type = self.attributes.get_attribute(self.current_type, node.id)
        else:
            var_type = var_info.type
        self.unify(var_type, expr_type)
        return var_type

    @visitor.when(ast.BlocksNode)
    def visit(self, node: ast.BlocksNode, scope: Scope):
        child_scope = scope.create_child()
        expr_type = self.context.get_type('Void')
        for expr in node.expr_list:
            expr_type = self.visit(expr, child_scope)
        return expr_type

    @visitor.when(ast.MethodCallNode)
    def visit(self, node: ast.MethodCallNode, scope: Scope):
        if node.expr is None:
            obj_type = self.current_type
        else:
            obj_type = self.visit(node.expr, scope)

        if node.type is None:
            typex = obj_type
        else:
            typex = self.context.get_type(node.type)

        # checks if the type is known
        if typex.name[0] == 't':
            self.errors.append('Inference error')
        else:
            function = self.functions.get_function(typex, node.id)
            args_type: List[Type] = []
            for arg in node.args:
                arg_type = self.visit(arg, scope)
                args_type.append(arg_type)
            self.unify(function, FunctionType(tuple(args_type), function.return_type))
            return function.return_type

    @visitor.when(ast.LoopNode)
    def visit(self, node: ast.LoopNode, scope: Scope):
        cond_type = self.visit(node.condition, scope)
        body_type = self.visit(node.body, scope.create_child())
        self.unify(self.context.get_type('Bool'), cond_type)
        return self.context.get_type('Object')

    @visitor.when(ast.VarDeclarationNode)
    def visit(self, node: ast.VarDeclarationNode, scope: Scope) -> Type:
        var_type = self.context.get_type(node.typex)
        if var_type.name == 'AUTO_TYPE':
            var_type = TypeVariable()
        if node.expr is not None:
            var_type = self.visit(node.expr, scope)
        scope.define_variable(node.id, var_type)
        return var_type

    @visitor.when(ast.ComparerNode)
    def visit(self, node: ast.ComparerNode, scope: Scope) -> Type:
        bool_type = self.context.get_type('Bool')
        int_type = self.context.get_type('Int')
        comparer_function = FunctionType((int_type, int_type), bool_type)
        left = self.visit(node.left, scope)
        right = self.visit(node.right, scope)
        self.unify(comparer_function, FunctionType((left, right), bool_type))
        return bool_type

    @visitor.when(ast.ArithmeticNode)
    def visit(self, node: ast.ArithmeticNode, scope: Scope) -> Type:
        int_type = self.context.get_type('Int')
        arith_function = FunctionType((int_type, int_type), int_type)
        left = self.visit(node.left, scope)
        right = self.visit(node.right, scope)
        self.unify(arith_function, FunctionType((left, right), int_type))
        return int_type

    @visitor.when(ast.VariableNode)
    def visit(self, node: ast.VariableNode, scope: Scope) -> Type:
        var_info = scope.find_variable(node.lex)
        if var_info is not None:
            return var_info.type
        var_type = self.attributes.get_attribute(self.current_type, node.lex)
        if var_type is None:
            return ErrorType()
        return var_type

    @visitor.when(ast.NotNode)
    def visit(self, node: ast.NotNode, scope: Scope) -> Type:
        bool_type = self.context.get_type('Bool')
        expr_type = self.visit(node.expr, scope)
        self.unify(bool_type, expr_type)
        return bool_type

    @visitor.when(ast.IsVoidNode)
    def visit(self, node: ast.IsVoidNode, scope: Scope) -> Type:
        bool_type = self.context.get_type('Bool')
        _ = self.visit(node.expr, scope)
        return bool_type

    @visitor.when(ast.ConstantNumNode)
    def visit(self, node: ast.ConstantNumNode, scope: Scope) -> Type:
        return self.context.get_type('Int')

    @visitor.when(ast.StringNode)
    def visit(self, node: ast.StringNode, scope: Scope) -> Type:
        return self.context.get_type('String')

    @visitor.when(ast.BooleanNode)
    def visit(self, node: ast.BooleanNode, scope: Scope) -> Type:
        return self.context.get_type('Bool')

    @visitor.when(ast.InstantiateNode)
    def visit(self, node: ast.InstantiateNode, scope: Scope) -> Type:
        return self.context.get_type(node.lex)

    def var_bind(self, type1, type2):
        if type1.name == type2.name:
            return  # self-reference
        try:
            self.types_graph[type1].add(type2)
        except:
            self.types_graph[type1] = {type2}
        try:
            self.types_graph[type2].add(type1)
        except:
            self.types_graph[type2] = {type1}

    def unify(self, type1: Type, type2: Type):
        if isinstance(type1, TypeVariable) or isinstance(type2, TypeVariable):
            self.var_bind(type1, type2)
        elif isinstance(type1, FunctionType) and isinstance(type2, FunctionType) \
                and len(type1.params_types) == len(type2.params_types):
            self.unify(type1.return_type, type2.return_type)
            for i, j in zip(type1.params_types, type2.params_types):
                self.unify(i, j)
        elif type1.name == type2.name or type2.conforms_to(type1) or type1.conforms_to(type2):
            pass
        else:
            raise Exception('Type mismatch')

    def dfs_inference(self):
        vertices: List[Type] = []
        for typex in self.types_graph:
            if isinstance(typex, TypeVariable):
                self.substitutions[typex.name] = ErrorType()
            else:
                vertices.append(typex)
            typex.visited = False
        for vertex in vertices:
            self.current_type = vertex
            if not vertex.visited:
                self.dfs_visit(vertex)

    def dfs_visit(self, vertex):
        if isinstance(vertex, TypeVariable):
            self.substitutions[vertex.name] = self.current_type
        elif not (vertex.conforms_to(self.current_type) or self.current_type.conforms_to(vertex)):
            raise SemanticError('Type inference error')

        vertex.visited = True
        for adj in self.types_graph[vertex]:
            if not adj.visited:
                self.dfs_visit(adj)
