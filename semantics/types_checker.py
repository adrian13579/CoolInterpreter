from typing import List
import cool_ast
from cmp import visitor
from semantics.utils import Context, Type, Method, ErrorType, Attribute, Scope, VariableInfo, SemanticError, SelfType
from semantics.errors import *


class TypeChecker:
    def __init__(self, context: Context, errors=None):
        if errors is None:
            errors = []
        self.context = context
        self.current_type = None
        self.current_method = None
        self.errors = errors

    @visitor.on('node')
    def visit(self, node, scope):
        pass

    @visitor.when(cool_ast.ProgramNode)
    def visit(self, node: cool_ast.ProgramNode, scope: Scope = None):
        if scope is None:
            scope = Scope()
        for declaration in node.declarations:
            self.visit(declaration, scope.create_child())
        return scope

    @visitor.when(cool_ast.ClassDeclarationNode)
    def visit(self, node: cool_ast.ClassDeclarationNode, scope: Scope):
        self.current_type: Type = self.context.get_type(node.id)
        scope.define_variable('self', SelfType(self.current_type))

        for feature in node.features:
            self.visit(feature, scope)

    @visitor.when(cool_ast.AttrDeclarationNode)
    def visit(self, node: cool_ast.AttrDeclarationNode, scope: Scope):
        att_type: Type = self.context.get_type(node.typex)  # if node.typex != 'SELF_TYPE' else self.current_type
        if node.expression is not None:
            expr_type: Type = self.visit(node.expression, scope)
            if not expr_type.conforms_to(att_type):
                self.errors.append(INCOMPATIBLE_TYPES % (expr_type.name, att_type.name))

    @visitor.when(cool_ast.MethodDeclarationNode)
    def visit(self, node: cool_ast.MethodDeclarationNode, scope: Scope):
        self.current_method: Method = self.current_type.get_method(node.id)
        try:
            parent_method = self.current_type.get_method(node.id)
            if parent_method.return_type != self.current_method.return_type:
                self.errors.append(WRONG_SIGNATURE % (node.id, self.current_type.parent.name))
            else:
                if len(parent_method.param_types) != len(self.current_method.param_types):
                    self.errors.append(WRONG_SIGNATURE % (node.id, self.current_type.parent.name))
                else:
                    for i, j in zip(parent_method.param_types, self.current_method.param_types):
                        if i != j:
                            self.errors.append(WRONG_SIGNATURE % (node.id, self.current_type.parent.name))
        except SemanticError:
            pass

        child_scope = scope.create_child()
        for param in node.params:
            typex: Type = self.context.get_type(param.typex)
            if typex.name == 'SELF_TYPE':
                self.errors.append(FORBIDDEN_SELF_TYPE % self.current_type.name)
            child_scope.define_variable(param.id, typex)

        expr_type: Type = self.context.get_type('Void')
        return_type = self.current_method.return_type

        if node.body is not None:
            expr_type = self.visit(node.body, child_scope)
        if self.current_method.return_type != self.context.get_type('Void') \
                and not expr_type.conforms_to(return_type):
            self.errors.append(INCOMPATIBLE_TYPES % (expr_type.name, self.current_method.return_type.name))

    @visitor.when(cool_ast.VarDeclarationNode)
    def visit(self, node: cool_ast.VarDeclarationNode, scope: Scope):
        var_type: Type = self.context.get_type(node.typex)

        if scope.is_defined(node.id):
            self.errors.append(LOCAL_ALREADY_DEFINED % (node.id, self.current_method.name))
        else:
            scope.define_variable(node.id, var_type)

        expr_type: Type = self.visit(node.expr, scope)
        if not expr_type.conforms_to(var_type):
            self.errors.append(INCOMPATIBLE_TYPES % (expr_type.name, var_type.name))

    @visitor.when(cool_ast.AssignNode)
    def visit(self, node: cool_ast.AssignNode, scope: Scope):
        expr_type: Type = self.visit(node.expr, scope)
        if scope.is_defined(node.id):
            var_type: Type = scope.find_variable(node.id).type
            var_type = self.current_type  # if var_type.name == 'SELF_TYPE' else var_type
        else:
            try:
                self.current_type: Type
                att = self.current_type.get_attribute(node.id)
                var_type = att.type
            except SemanticError:
                self.errors.append(VARIABLE_NOT_DEFINED % (node.id, self.current_method.name))
                var_type = ErrorType()
        if not expr_type.conforms_to(var_type):
            self.errors.append(INCOMPATIBLE_TYPES % (expr_type.name, var_type.name))
        return var_type

    @visitor.when(cool_ast.MethodCallNode)
    def visit(self, node: cool_ast.MethodCallNode, scope: Scope):
        object_type = self.current_type
        if node.expr is not None:
            object_type = self.visit(node.expr, scope)
            if node.type is not None:
                node_type = self.context.get_type(node.type)
                if node_type.name == 'SELF_TYPE':
                    node_type = object_type
                if object_type.conforms_to(node_type):
                    object_type = node_type
                else:
                    self.errors.append(f'Invalid method call')
        elif node.type is not None:
            self.errors.append('Invalid method call')
        try:
            method: Method = object_type.get_method(node.id)
            return_type: Type = method.return_type if method.return_type.name != 'SELF_TYPE' else object_type
            if node.expr is None and method.return_type.name == 'SELF_TYPE':
                # the method called belongs to the current class
                return_type: Type = SelfType(method.return_type)

            if len(method.param_types) != len(node.args):
                self.errors.append(UNEXPECTED_NUMBER_OF_ARGUMENT % (self.current_type.name, node.id))

            arg_types: List[Type] = []
            for arg in node.args:
                arg_types.append(self.visit(arg, scope.create_child()))
            for arg_type, typex in zip(arg_types, method.param_types):
                if not arg_type.conforms_to(typex):
                    self.errors.append(f'Incorrect argument type in method {self.current_type.name}.{node.id}:'
                                       + INCOMPATIBLE_TYPES % (arg_type.name, typex.name))
        except SemanticError:
            return_type = ErrorType()
            self.errors.append(METHOD_NOT_DEFINED % (node.id, self.current_type.name))
        return return_type

    @visitor.when(cool_ast.ConditionalNode)
    def visit(self, node: cool_ast.ConditionalNode, scope: Scope):
        condition_type: Type = self.visit(node.condition, scope.create_child())
        bool_type: Type = self.context.get_type('Bool')
        if condition_type != bool_type:
            self.errors.append(INCOMPATIBLE_TYPES % (condition_type.name, bool_type.name))

        then_type: Type = self.visit(node.then_body, scope.create_child())
        else_type: Type = self.visit(node.else_body, scope.create_child())

        return Type.join_types(then_type, else_type)

    @visitor.when(cool_ast.LoopNode)
    def visit(self, node: cool_ast.LoopNode, scope: Scope):
        condition_type: Type = self.visit(node.condition, scope.create_child())
        bool_type: Type = self.context.get_type('Bool')
        if condition_type != bool_type:
            self.errors.append(INCOMPATIBLE_TYPES % (condition_type.name, bool_type.name))

        child_scope = scope.create_child()
        self.visit(node.body, child_scope)

        return self.context.get_type('Object')

    @visitor.when(cool_ast.LetNode)
    def visit(self, node: cool_ast.LetNode, scope: Scope):
        child_scope: Scope = scope.create_child()
        for var in node.var_decl_list:
            var: cool_ast.VarDeclarationNode
            var_type: Type = self.context.get_type(var.typex)
            child_scope.define_variable(var.id, var_type)
            if var.expr is not None:
                var_expr_type: Type = self.visit(var.expr, child_scope)
                if not var_expr_type.conforms_to(var_type):
                    self.errors.append(INCOMPATIBLE_TYPES % (var_expr_type.name, var_type.name))

        return_type: Type = self.context.get_type('Void')
        if node.in_expr is not None:
            return_type = self.visit(node.in_expr, child_scope)

        return return_type

    @visitor.when(cool_ast.CaseNode)
    def visit(self, node: cool_ast.CaseNode, scope: Scope):
        self.visit(node.case_expr, scope.create_child())
        case_types: List[Type] = []
        for option in node.options:
            option: cool_ast.CaseOptionNode
            child_scope: Scope = scope.create_child()
            option_type: Type = self.context.get_type(option.type)
            if option_type.name == 'SELF_TYPE':
                option_type = self.current_type
                self.errors.append(FORBIDDEN_SELF_TYPE % self.current_type.name)
            child_scope.define_variable(option.id, option_type)
            typex: Type = self.visit(option.expr, child_scope)
            case_types.append(typex)

        return Type.join_types(*case_types)

    @visitor.when(cool_ast.BlocksNode)
    def visit(self, node: cool_ast.BlocksNode, scope: Scope):
        child_scope: Scope = scope.create_child()
        return_type: Type = self.context.get_type('Void')
        for expr in node.expr_list:
            return_type = self.visit(expr, child_scope)
        return return_type

    @visitor.when(cool_ast.ArithmeticNode)
    def visit(self, node: cool_ast.ArithmeticNode, scope: Scope):
        left_expr_type: Type = self.visit(node.left, scope)
        right_expr_type: Type = self.visit(node.right, scope)
        int_type = self.context.get_type('Int')

        if left_expr_type != int_type or right_expr_type != int_type:
            self.errors.append(INVALID_OPERATION % (left_expr_type.name, right_expr_type.name))
        return int_type

    @visitor.when(cool_ast.ComparerNode)
    def visit(self, node: cool_ast.ComparerNode, scope: Scope):
        left_expr_type: Type = self.visit(node.left, scope)
        right_expr_type: Type = self.visit(node.right, scope)
        bool_type = self.context.get_type('Bool')

        if left_expr_type != right_expr_type:
            self.errors.append(INVALID_OPERATION % (left_expr_type.name, right_expr_type.name))
        return bool_type

    @visitor.when(cool_ast.VariableNode)
    def visit(self, node: cool_ast.VariableNode, scope: Scope):
        if scope.is_defined(node.lex):
            var: VariableInfo = scope.find_variable(node.lex)
            return var.type if var.type.name != 'SELF_TYPE' else SelfType(self.current_type)
        try:
            att: Attribute = self.current_type.get_attribute(node.lex)
            return att.type if att.type.name != 'SELF_TYPE' else SelfType(self.current_type)
        except SemanticError:
            self.errors.append(VARIABLE_NOT_DEFINED % (node.lex, self.current_type.name))
            return ErrorType()

    @visitor.when(cool_ast.InstantiateNode)
    def visit(self, node: cool_ast.InstantiateNode, scope: Scope):
        try:
            new_type: Type = self.context.get_type(node.lex)
            return new_type if new_type.name != 'SELF_TYPE' else SelfType(self.current_type)
        except SemanticError:
            self.errors.append(TYPE_NOT_DEFINED % node.lex)
            return ErrorType()

    @visitor.when(cool_ast.IsVoidNode)
    def visit(self, node: cool_ast.IsVoidNode, scope: Scope):
        self.visit(node.expr, scope)
        return self.context.get_type('Bool')

    @visitor.when(cool_ast.NotNode)
    def visit(self, node: cool_ast.NotNode, scope: Scope):
        expr_type = self.visit(node.expr, scope)
        if expr_type != self.context.get_type('Bool'):
            self.errors.append(INVALID_OPERATION % (expr_type.name, 'Bool'))
        return self.context.get_type('Bool')

    @visitor.when(cool_ast.ComplementNode)
    def visit(self, node: cool_ast.ComplementNode, scope: Scope):
        expr_type = self.visit(node.expr, scope)
        if expr_type != self.context.get_type('Int'):
            self.errors.append(INVALID_OPERATION % (expr_type.name, 'Bool'))
        return self.context.get_type('Int')

    @visitor.when(cool_ast.ConstantNumNode)
    def visit(self, node: cool_ast.ConstantNumNode, scope: Scope):
        return self.context.get_type('Int')

    @visitor.when(cool_ast.BooleanNode)
    def visit(self, node: cool_ast.BooleanNode, scope: Scope):
        return self.context.get_type('Bool')

    @visitor.when(cool_ast.StringNode)
    def visit(self, node: cool_ast.StringNode, scope: Scope):
        return self.context.get_type('String')
