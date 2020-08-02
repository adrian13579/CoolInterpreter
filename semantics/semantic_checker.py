from ast import *
from cmp import visitor
from utils import Scope, VariableInfo
from utils import Context, Type, Method, ErrorType, Attribute
from semantics import INCOMPATIBLE_TYPES, WRONG_SIGNATURE, LOCAL_ALREADY_DEFINED, VARIABLE_NOT_DEFINED, \
    INVALID_OPERATION


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

    @visitor.when(ProgramNode)
    def visit(self, node: ProgramNode, scope: Scope = None):
        if scope is None:
            scope = Scope()
        for declaration in node.declarations:
            self.visit(declaration, scope.create_child())
        return scope

    @visitor.when(ClassDeclarationNode)
    def visit(self, node: ClassDeclarationNode, scope: Scope):
        self.current_type: Type = self.context.get_type(node.id)

        for feature in node.features:
            self.visit(feature, scope)

    @visitor.when(AttrDeclarationNode)
    def visit(self, node: AttrDeclarationNode, scope: Scope):
        att_type: Type = self.context.get_type(node.typex)
        if node.expression is not None:
            expr_type: Type = self.visit(node.expression, scope)
            if not expr_type.conforms_to(att_type):
                self.errors.append(INCOMPATIBLE_TYPES % (expr_type.name, att_type.name))

    @visitor.when(MethodDeclarationNode)
    def visit(self, node: MethodDeclarationNode, scope: Scope):
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
                        if i != j: self.errors.append(WRONG_SIGNATURE % (node.id, self.current_type.parent.name))
        except:
            pass
        child_scope = scope.create_child()
        for param in node.params:
            typex: Type = self.context.get_type(param.typex)
            child_scope.define_variable(param.id, typex)

        expr_type: Type = self.context.get_type('Void')
        if node.body is not None:
            expr_type = self.visit(node.body, child_scope)
        if self.current_method.return_type != self.context.get_type('Void') \
                and not expr_type.conforms_to(self.current_method.return_type):
            self.errors.append(INCOMPATIBLE_TYPES % (expr_type.name, self.current_method.return_type.name))

    @visitor.when(VarDeclarationNode)
    def visit(self, node: VarDeclarationNode, scope: Scope):
        var_type: Type = self.context.get_type(node.typex)

        if scope.is_defined(node.id):
            self.errors.append(LOCAL_ALREADY_DEFINED % (node.id, self.current_method.name))
        else:
            scope.define_variable(node.id, var_type)

        expr_type: Type = self.visit(node.expr, scope)
        if not expr_type.conforms_to(var_type):
            self.errors.append(INCOMPATIBLE_TYPES % (expr_type.name, var_type.name))

    @visitor.when(AssignNode)
    def visit(self, node: AssignNode, scope: Scope):
        expr_type: Type = self.visit(node.expr, scope)
        if scope.is_defined(node.id):
            var_type: Type = scope.find_variable(node.id).type
        else:
            try:
                self.current_type: Type
                att = self.current_type.get_attribute(node.id)
                var_type = att.type
            except:
                self.errors.append(VARIABLE_NOT_DEFINED % (node.id, self.current_method.name))
                var_type = ErrorType()
        if not expr_type.conforms_to(var_type):
            self.errors.append(INCOMPATIBLE_TYPES % (expr_type.name, var_type.name))

    @visitor.when(MethodCallNode)
    def visit(self, node: MethodCallNode, scope: Scope):
        try:
            method: Method = self.current_type.get_method(node.id)
            return_type: Type = method.return_type
            if len(method.param_types) != len(node.args):
                self.errors.append(f'Unexpected number of arguments in method {self.current_type.name}.{node.id}')

            arg_types: List[Type] = []
            for arg in node.args:
                arg_types.append(self.visit(arg, scope.create_child()))
            for arg_type, typex in zip(arg_types, method.param_types):
                if not arg_type.conforms_to(typex):
                    self.errors.append(f'Incorrect argument type in method {self.current_type.name}.{node.id}:'
                                       + INCOMPATIBLE_TYPES % (arg_type.name, typex.name))
        except:
            return_type = ErrorType()
            self.errors.append(f'Method {node.id} not defined in class {self.current_type.name}')
        return return_type

    @visitor.when(ConditonalNode)
    def visit(self, node: ConditonalNode, scope: Scope):
        condition_type: Type = self.visit(node.condition, scope.create_child())
        bool_type: Type = self.context.get_type('Bool')
        if condition_type != bool_type:
            self.errors.append(INCOMPATIBLE_TYPES % (condition_type.name, bool_type.name))

        then_type: Type = self.visit(node.then_body, scope.create_child())
        else_type: Type = self.visit(node.else_body, scope.create_child())

        return Type.least_type(then_type, else_type)

    @visitor.when(LoopNode)
    def visit(self, node: LoopNode, scope: Scope):
        condition_type: Type = self.visit(node.condition, scope.create_child())
        bool_type: Type = self.context.get_type('Bool')
        if condition_type != bool_type:
            self.errors.append(INCOMPATIBLE_TYPES % (condition_type.name, bool_type.name))

        child_scope = scope.create_child()
        self.visit(node.body, child_scope)

        return self.context.get_type('Object')

    @visitor.when(LetNode)
    def visit(self, node: LetNode, scope: Scope):
        child_scope: Scope = scope.create_child()
        for var in node.var_decl_list:
            var: VarDeclarationNode
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

    @visitor.when(CaseNode)
    def visit(self, node: CaseNode, scope: Scope):
        self.visit(node.case_expr, scope.create_child())
        case_types: List[Type] = []
        for option in node.options:
            option: CaseOptionNode
            child_scope: Scope = scope.create_child()
            option_type: Type = self.context.get_type(option.type)
            child_scope.define_variable(option.id, option_type)
            typex: Type = self.visit(option.expr, child_scope)
            case_types.append(typex)

        return Type.least_type(*case_types)

    @visitor.when(BlocksNode)
    def visit(self, node: BlocksNode, scope: Scope):
        child_scope: Scope = scope.create_child()
        return_type: Type = self.context.get_type('Void')
        for expr in node.expr_list:
            return_type = self.visit(expr, child_scope)
        return return_type

    @visitor.when(ArithmeticNode)
    def visit(self, node: BinaryNode, scope: Scope):
        left_expr_type: Type = self.visit(node.left, scope)
        right_expr_type: Type = self.visit(node.right, scope)
        int_type = self.context.get_type('Int')

        if left_expr_type != int_type or right_expr_type != int_type:
            self.errors.append(INVALID_OPERATION % (left_expr_type.name, right_expr_type.name))
        return int_type

    @visitor.when(ComparerNode)
    def visit(self, node: ComparerNode, scope: Scope):
        left_expr_type: Type = self.visit(node.left, scope)
        right_expr_type: Type = self.visit(node.right, scope)
        bool_type = self.context.get_type('Bool')

        if left_expr_type != bool_type or right_expr_type != bool_type:
            self.errors.append(INVALID_OPERATION % (left_expr_type.name, right_expr_type.name))
        return bool_type

    @visitor.when(VariableNode)
    def visit(self, node: VariableNode, scope: Scope):
        if scope.is_defined(node.lex):
            var: VariableInfo = scope.find_variable(node.lex)
            return var.type
        try:
            att: Attribute = self.current_type.get_attribute(node.lex)
            return att.type
        except:
            self.errors.append(VARIABLE_NOT_DEFINED % (node.lex, self.current_type.name))
            return ErrorType()

    @visitor.when(InstantiateNode)
    def visit(self, node: InstantiateNode, scope: Scope):
        try:
            new_type: Type = self.context.get_type(node.lex)
            return new_type
        except:
            self.errors.append(f'Type {node.lex} not defined')
            return ErrorType()

    @visitor.when(ConstantNumNode)
    def visit(self, node: ConstantNumNode, scope: Scope):
        return self.context.get_type('Int')

    @visitor.when(BooleanNode)
    def visit(self, node: BooleanNode, scope: Scope):
        return self.context.get_type('Bool')

    @visitor.when(StringNode)
    def visit(self, node: StringNode, scope: Scope):
        return self.context.get_type('String')

    @visitor.when(IsVoidNode)
    def visit(self, node: IsVoidNode, scope: Scope):
        return self.context.get_type('Bool')

    @visitor.when(NotNode)
    def visit(self, node: NotNode, scope: Scope):
        return self.context.get_type('Bool')
