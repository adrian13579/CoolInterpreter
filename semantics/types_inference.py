from typing import Dict, List, Union, Optional

import ast
from cmp import visitor
from utils import Context, Type, TypeVariable, FunctionType, Method, ErrorType, Scope

Subst = Dict[str, Type]


class TypeInferencer:
    def __init__(self, context: Context, scope: Scope, errors: List[str]):
        self.errors = errors
        self.context = context
        self.scope = scope

        self.functions: Dict[(str, str), FunctionType] = self.collect_functions(context)
        self.attributes: Dict[(str, str), Type] = self.collect_attributes(context)

        self.current_type: Type = None
        self.current_method: Method = None

    @staticmethod
    def collect_attributes(context: Context):
        attributes: Dict[(str, str), Type] = {}
        for typex in context.types.values():
            for attr in typex.attributes:
                attr_type = TypeVariable() if attr.type.name == 'AUTO_TYPE' else attr.type
                attributes[typex.name, attr.name] = attr_type
        return attributes

    @staticmethod
    def collect_functions(context: Context):
        functions: Dict[(str, str), FunctionType] = {}
        for typex in context.types.values():
            for method in typex.methods:
                param_types: List[Type] = []
                for param in method.param_types:
                    if param.name == 'AUTO_TYPE':
                        param_types.append(TypeVariable())
                    else:
                        param_types.append(param)
                return_type = TypeVariable() if method.return_type.name == 'AUTO_TYPE' else method.return_type
                functions[typex.name, method.name] = FunctionType(param_types, return_type)
        return functions

    def get_function(self, typex: Type, func_name: str) -> Optional[FunctionType]:
        return self.aux_get_function(typex, typex, func_name)

    def aux_get_function(self, init_type: Type, typex: Type, func_name: str) -> Optional[FunctionType]:
        try:
            func_type = self.functions[typex.name, func_name]
            params_type = [init_type if param.name == 'SELF_TYPE' else param for param in func_type.params_types]
            return_type = init_type if func_type.return_type.name == 'SELF_TYPE' else func_type.return_type
            return FunctionType(params_type, return_type)
        except KeyError:
            if typex.parent is not None:
                return self.aux_get_function(init_type, typex.parent, func_name)

    def get_atribute(self, typex: Type, attr_name) -> Optional[Type]:
        return self.aux_get_attribute(typex, typex, attr_name)

    def aux_get_attribute(self, init_type: Type, typex: Type, attr_name) -> Optional[Type]:
        try:
            att_type = self.attributes[typex.name, attr_name]
            return init_type if att_type.name == 'SELF_TYPE' else att_type
        except KeyError:
            if typex.parent is not None:
                return self.aux_get_attribute(init_type, typex.parent, attr_name)

    @visitor.on('node')
    def visit(self, node, scope: Scope):
        pass

    @visitor.when(ast.ProgramNode)
    def visit(self, node: ast.ProgramNode, scope: Scope) -> None:
        for class_decl in node.declarations:
            self.current_type = self.context.get_type(class_decl.id)
            self.visit(class_decl, scope.create_child())

    @visitor.when(ast.ClassDeclarationNode)
    def visit(self, node: ast.ClassDeclarationNode, scope: Scope) -> None:
        attrs = [feature for feature in node.features if isinstance(feature, ast.AttrDeclarationNode)]
        methods = [feature for feature in node.features if isinstance(feature, ast.MethodDeclarationNode)]

        scope.define_variable('self', self.current_type)

        subst: Subst = {}
        for attr in attrs:
            typex, new_subst = self.visit(attr, scope)
            subst = self.compound_subst([subst, new_subst])
            self.apply_subst_to_env(subst)

        for method in methods:
            self.current_method = self.current_type.get_method(method.id)
            typex, new_subst = self.visit(method, scope.create_child())
            subst = self.compound_subst([subst, new_subst])
            self.apply_subst_to_env(subst)

    @visitor.when(ast.AttrDeclarationNode)
    def visit(self, node: ast.AttrDeclarationNode, scope: Scope) -> (Type, Subst):
        if node.expression is not None:
            expr_type, subst1 = self.visit(node.expression, scope.create_child())
            attr_type = self.attributes[node.id]
            subst2 = self.unify(attr_type, expr_type)
            attr_type = self.apply_subst_to_type(subst2, attr_type)
            return attr_type, self.compound_subst([subst1, subst2])
        else:
            return self.get_atribute(self.current_type, node.id), {}

    @visitor.when(ast.MethodDeclarationNode)
    def visit(self, node: ast.MethodDeclarationNode, scope: Scope) -> (FunctionType, Subst):
        function = self.get_function(self.current_type, self.current_method.name)
        for param_type, param in zip(function.params_types, node.params):
            scope.define_variable(param.id, param_type)

        body_type, subst1 = self.visit(node.body, scope)
        self.apply_subst_to_scope(subst1, scope)
        infer_param = [self.apply_subst_to_type(subst1, typex) for typex in function.params_types]
        subst2 = self.unify(function, FunctionType(infer_param, body_type))
        function_type = self.apply_subst_to_type(subst2, function)

        return function_type, self.compound_subst([subst1, subst2])

    @visitor.when(ast.ConditionalNode)
    def visit(self, node: ast.ConditionalNode, scope: Scope):
        bool_type = self.context.get_type('Bool')
        cond_type, subst1 = self.visit(node.condition, scope)
        subst2 = self.unify(bool_type, cond_type)
        then_type, subst3 = self.visit(node.then_body, scope.create_child())
        else_type, subst4 = self.visit(node.else_body, scope.create_child())
        subst = self.compound_subst([subst1, subst2, subst3, subst4])
        return self.context.get_type('Object'), subst

    @visitor.when(ast.LetNode)
    def visit(self, node: ast.LetNode, scope: Scope) -> (Type, Subst):
        subst: Subst = {}
        child_scope = scope.create_child()
        for var in node.var_decl_list:
            var_type, subst1 = self.visit(var, child_scope)
            # child_scope.define_variable(var.id, var_type)
            subst = self.compound_subst([subst, subst1])

        body_type, subst2 = self.visit(node.in_expr, child_scope)
        subst = self.compound_subst([subst, subst2])
        return body_type, subst

    @visitor.when(ast.AssignNode)
    def visit(self, node: ast.AssignNode, scope: Scope) -> (Type, Subst):
        expr_type, subst1 = self.visit(node.expr, scope.create_child())
        var_info = scope.find_variable(node.id)
        if var_info is None:  # check if is an attribute
            var_type = self.get_atribute(self.current_type, node.id)
        else:
            var_type = var_info.type
        subst2 = self.unify(var_type, expr_type)
        var_type = self.apply_subst_to_type(subst2, var_type)
        return var_type, self.compound_subst([subst1, subst2])

    @visitor.when(ast.BlocksNode)
    def visit(self, node: ast.BlocksNode, scope: Scope) -> (Type, Subst):
        child_scope = scope.create_child()
        expr_type = self.context.get_type('Void')
        subst1: Subst = {}
        for expr in node.expr_list:
            expr_type, subst2 = self.visit(expr, child_scope)
            subst1 = self.compound_subst([subst1, subst2])
        return expr_type, subst1

    @visitor.when(ast.MethodCallNode)
    def visit(self, node: ast.MethodCallNode, scope: Scope) -> (Type, Subst):
        if node.expr is None:
            obj_type, subst1 = self.current_type, {}
        else:
            obj_type, subst1 = self.visit(node.expr, scope)

        if node.type is None:
            typex = obj_type
        else:
            typex = self.context.get_type(node.type)

        # checks if the type is known
        if typex.name[0] == 't':
            self.errors.append('Inference error')
        else:
            function = self.get_function(typex, node.id)
            args_type: List[Type] = []
            for arg in node.args:
                arg_type, subst2 = self.visit(arg, scope)
                subst1 = self.compound_subst([subst1, subst2])
                args_type.append(arg_type)
            subst2 = self.unify(function, FunctionType(args_type, function.return_type))
            function_type = self.apply_subst_to_type(subst2, function)
            subst1 = self.compound_subst([subst1, subst2])
            return_type = self.apply_subst_to_type(subst1, function_type.return_type)
            subst2 = self.unify(function_type.return_type, return_type)
            return return_type, self.compound_subst([subst1, subst2])

    @visitor.when(ast.LoopNode)
    def visit(self, node: ast.LoopNode, scope: Scope) -> (Type, Subst):
        cond_type, subst1 = self.visit(node.condition, scope)
        body_type, subst2 = self.visit(node.body, scope.create_child())
        subst1 = self.compound_subst([subst1, subst2])
        subst2 = self.unify(self.context.get_type('Bool'), cond_type)
        return self.context.get_type('Object'), self.compound_subst([subst1, subst2])

    @visitor.when(ast.VarDeclarationNode)
    def visit(self, node: ast.VarDeclarationNode, scope: Scope) -> (Type, Subst):
        subst: Subst = {}
        var_type = self.context.get_type(node.typex)
        if var_type.name == 'AUTO_TYPE':
            var_type = TypeVariable()
        if node.expr is not None:
            infer_type, subst = self.visit(node.expr, scope)
            subst = self.compound_subst([self.unify(var_type, infer_type), subst])
            var_type = self.apply_subst_to_type(subst, var_type)
        scope.define_variable(node.id, var_type)
        return var_type, subst

    @visitor.when(ast.ComparerNode)
    def visit(self, node: ast.ComparerNode, scope: Scope) -> (Type, Subst):
        bool_type = self.context.get_type('Bool')
        int_type = self.context.get_type('Int')
        comparer_function = FunctionType([int_type, int_type], bool_type)
        left, subst1 = self.visit(node.left, scope)
        right, subst2 = self.visit(node.right, scope)

        subst1 = self.compound_subst([subst1, subst2])
        subst2 = self.unify(comparer_function, FunctionType([left, right], bool_type))

        return bool_type, self.compound_subst([subst1, subst2])

    @visitor.when(ast.ArithmeticNode)
    def visit(self, node: ast.ArithmeticNode, scope: Scope) -> (Type, Subst):
        int_type = self.context.get_type('Int')
        arith_function = FunctionType([int_type, int_type], int_type)
        left, subst1 = self.visit(node.left, scope)
        right, subst2 = self.visit(node.right, scope)

        subst1 = self.compound_subst([subst1, subst2])
        subst2 = self.unify(arith_function, FunctionType([left, right], int_type))

        return int_type, self.compound_subst([subst1, subst2])

    @visitor.when(ast.VariableNode)
    def visit(self, node: ast.VariableNode, scope: Scope) -> (Type, Subst):
        var_info = scope.find_variable(node.lex)
        if var_info is not None:
            return var_info.type, {}
        var_type = self.get_atribute(self.current_type, node.lex)
        if var_type is None:
            return ErrorType(), {}
        return var_type, {}

    @visitor.when(ast.NotNode)
    def visit(self, node: ast.NotNode, scope: Scope) -> (Type, Subst):
        return self.context.get_type('Bool'), {}

    @visitor.when(ast.IsVoidNode)
    def visit(self, node: ast.IsVoidNode, scope: Scope) -> (Type, Subst):
        return self.context.get_type('Bool'), {}

    @visitor.when(ast.ConstantNumNode)
    def visit(self, node: ast.ConstantNumNode, scope: Scope) -> (Type, Subst):
        return self.context.get_type('Int'), {}

    @visitor.when(ast.StringNode)
    def visit(self, node: ast.StringNode, scope: Scope) -> (Type, Subst):
        return self.context.get_type('String'), {}

    @visitor.when(ast.BooleanNode)
    def visit(self, node: ast.BooleanNode, scope: Scope) -> (Type, Subst):
        return self.context.get_type('Bool'), {}

    @visitor.when(ast.InstantiateNode)
    def visit(self, node: ast.InstantiateNode, scope: Scope) -> (Type, Subst):
        return self.context.get_type(node.lex), {}

    def apply_subst_to_env(self, subst: Subst) -> None:
        self.apply_subst_to_scope(subst, self.scope)
        self.apply_subst_to_functions(subst)
        self.apply_subst_to_attr(subst)

    def apply_subst_to_scope(self, subst: Subst, scope: Scope) -> None:
        for var_info in scope.locals:
            var_info.type = self.apply_subst_to_type(subst, var_info.type)
        for child in scope.children:
            self.apply_subst_to_scope(subst, child)

    def apply_subst_to_functions(self, subst: Subst) -> None:
        for name in self.functions:
            typex = self.functions[name]
            self.functions[name] = self.apply_subst_to_type(subst, typex)

    def apply_subst_to_attr(self, subst: Subst) -> None:
        for name in self.attributes:
            typex = self.attributes[name]
            self.attributes[name] = self.apply_subst_to_type(subst, typex)

    def apply_subst_to_type(self, subst: Subst, typex: Type) -> Union[Type, FunctionType, TypeVariable]:
        if isinstance(typex, TypeVariable):
            try:
                return subst[typex.name]
            except KeyError:
                return typex
        elif isinstance(typex, FunctionType):
            params_types: List[Type] = []

            for param in typex.params_types:
                params_types.append(self.apply_subst_to_type(subst, param))
            return_type = self.apply_subst_to_type(subst, typex.return_type)

            return FunctionType(params_types, return_type)
        elif isinstance(typex, Type):
            return typex
        else:
            raise TypeError()

    def contains(self, typex: Type, name: str) -> bool:
        if isinstance(typex, TypeVariable):
            return typex.name == name
        elif isinstance(typex, FunctionType):
            for param in typex.params_types:
                if self.contains(param, name):
                    return True
            return self.contains(typex.return_type, name)
        elif isinstance(typex, Type):
            return False
        else:
            raise TypeError()

    def var_bind(self, name: str, typex: Type) -> Subst:
        if isinstance(typex, TypeVariable) and typex.name == name:
            return {}
        elif self.contains(typex, name):
            raise Exception('Self-reference')
        else:
            return {name: typex}

    def unify(self, type1: Type, type2: Type) -> Subst:
        if isinstance(type1, TypeVariable):
            return self.var_bind(type1.name, type2)
        elif isinstance(type2, TypeVariable):
            return self.var_bind(type2.name, type1)
        elif isinstance(type1, FunctionType) and isinstance(type2, FunctionType) \
                and len(type1.params_types) == len(type2.params_types):
            substitutions: List[Subst] = []
            for i, j in zip(type1.params_types, type2.params_types):
                substitutions.append(self.unify(i, j))
            substitutions.append(self.unify(type1.return_type, type2.return_type))
            return self.compound_subst(substitutions)
        elif isinstance(type1, Type) and isinstance(type2, Type):
            if type1.name == type2.name or type2.conforms_to(type1) or type1.conforms_to(type2):
                return {}
        else:
            raise Exception('Type mismatch')

    def compound_subst(self, substitutions: List[Subst]) -> Subst:
        result: Subst = {}
        for subst in substitutions:
            result = self.aux_compound_subst(result, subst)
        return result

    def aux_compound_subst(self, s1: Subst, s2: Subst) -> Subst:
        result: Subst = {}
        for name in s1:
            typex = s1[name]
            if isinstance(typex, TypeVariable):
                result[name] = self.apply_subst_to_type(s2, typex)
            else:
                result[name] = typex
        return {**result, **s2}


