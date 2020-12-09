from typing import List, Optional, Union, Any, Dict
from cmp import visitor
import cool_ast
from semantics import Context, Scope, Attribute, Type, VoidType, Method


class CoolRuntimeError(Exception):
    @property
    def text(self) -> str:
        return self.args[0]


class CoolObject:
    def __init__(self, typex: Type, value: Any = None):
        self.type = typex
        if value is None:
            if typex.name == 'Int':
                value = 0
            elif typex.name == 'String':
                value = ''
            elif typex.name == 'Bool':
                value = False
        self._value = value
        self.atributes: Dict[str, CoolObject] = {}

    @property
    def value(self):
        if self._value is None:
            return self
        return self._value

    def set_attribute(self, name: str, value: 'CoolObject') -> None:
        try:
            self.type.get_attribute(name)
            self.atributes[name] = value
        except:
            raise CoolRuntimeError(f'Object {self.type.name} does not have an attribute named {name}')

    def get_attribute(self, name) -> Union[Attribute, 'CoolObject']:
        try:
            return self.atributes[name]
        except KeyError:
            return self.type.get_attribute(name)

    def get_method(self, name: str, typex: Type) -> Optional[Method]:
        tmp_type = self.type
        while tmp_type != typex:
            if tmp_type.parent is not None:
                tmp_type = tmp_type.parent
            else:
                return None
        return tmp_type.get_method(name)


class VoidObject(CoolObject):
    def __init__(self):
        CoolObject.__init__(self, VoidType())

    def __eq__(self, other):
        return isinstance(other, VoidObject)


def abort(obj: CoolObject, context: Context) -> None:
    print('Aborting...')
    exit()


def type_name(obj: CoolObject, x: CoolObject, context: Context) -> CoolObject:
    return CoolObject(context.get_type('String'), x.type.name)


def copy(obj: CoolObject) -> CoolObject:
    copy_obj = CoolObject(obj.type, obj.value if obj.type.name in ('Int', 'String', 'Bool') else None)
    copy_obj.atributes = obj.atributes
    return copy_obj


def out_string(obj: CoolObject, x: CoolObject, context: Context) -> CoolObject:
    print(x.value)
    return obj


def out_int(obj: CoolObject, x: CoolObject, context: Context) -> CoolObject:
    print(x.value)
    return obj


def length(obj: CoolObject, context: Context) -> CoolObject:
    return CoolObject(context.get_type('Int'), len(obj.value))


def concat(obj: CoolObject, s: CoolObject, context: Context) -> CoolObject:
    return CoolObject(context.get_type('String'), obj.value + s.value)


def substr(obj: CoolObject, i: CoolObject, l: CoolObject, context: Context) -> CoolObject:
    return CoolObject(context.get_type('String'), obj.value[i.value: i.value + l.value])


def in_string(obj: CoolObject, context: Context) -> CoolObject:
    return CoolObject(context.get_type('String'), input())


def in_int(obj: CoolObject, context: Context) -> CoolObject:
    return CoolObject(context.get_type('Int'), int(input()))


class Interpreter:
    def __init__(self, context: Context):
        self.context = context
        self.stack: List[CoolObject] = []
        self.current_object: CoolObject = None
        self.builtin_functions = {
            ('Object', 'abort'): abort,
            ('Object', 'type_name'): type_name,
            ('Object', 'copy'): copy,
            ('IO', 'out_string'): out_string,
            ('IO', 'out_int'): out_int,
            ('IO', 'in_string'): in_string,
            ('IO', 'in_int'): in_int,
            ('String', 'length'): length,
            ('String', 'concat'): concat,
            ('String', 'substr'): substr,
        }

    @visitor.on('node')
    def visit(self, node, scope: Scope):
        pass

    @visitor.when(cool_ast.ProgramNode)
    def visit(self, node: cool_ast.ProgramNode, scope: Scope) -> None:
        for class_decl in node.declarations:
            self.visit(class_decl, scope)

        self.current_object = CoolObject(self.context.get_type('Main'))
        scope.define_variable('self', self.current_object.type, self.current_object)
        self.visit(self.current_object.get_method('main', self.current_object.type).expression, scope)

    @visitor.when(cool_ast.ClassDeclarationNode)
    def visit(self, node: cool_ast.ClassDeclarationNode, scope: Scope) -> None:
        attributes = [feature for feature in node.features if isinstance(feature, cool_ast.AttrDeclarationNode)]
        methods = [feature for feature in node.features if isinstance(feature, cool_ast.MethodDeclarationNode)]

        current_type = self.context.get_type(node.id)
        for attr in attributes:
            type_attr = current_type.get_attribute(attr.id)
            type_attr.expression = attr.expression

        for method in methods:
            type_method = current_type.get_method(method.id)
            type_method.expression = method.body

    @visitor.when(cool_ast.BlocksNode)
    def visit(self, node: cool_ast.BlocksNode, scope: Scope) -> CoolObject:
        cool_object = VoidObject()
        for expr in node.expr_list:
            cool_object = self.visit(expr, scope)
        return cool_object

    @visitor.when(cool_ast.ConditionalNode)
    def visit(self, node: cool_ast.ConditionalNode, scope: Scope) -> CoolObject:
        condition = self.visit(node.condition, scope)
        if condition.value:
            return self.visit(node.then_body, scope.create_child())
        return self.visit(node.else_body, scope.create_child())

    @visitor.when(cool_ast.LoopNode)
    def visit(self, node: cool_ast.LoopNode, scope: Scope) -> VoidObject:
        child_scope = scope.create_child()
        while self.visit(node.condition, child_scope).value:
            self.visit(node.body, child_scope)
        return VoidObject()

    @visitor.when(cool_ast.LetNode)
    def visit(self, node: cool_ast.LetNode, scope: Scope) -> CoolObject:
        child_scope = scope.create_child()
        for var in node.var_decl_list:
            var_type = self.context.get_type(var.typex)
            var_object = CoolObject(var_type) if var.expr is None else self.visit(var.expr, child_scope)
            child_scope.define_variable(var.id, var_type, var_object)
        return self.visit(node.in_expr, child_scope)

    @visitor.when(cool_ast.CaseNode)
    def visit(self, node: cool_ast.CaseNode, scope: Scope) -> CoolObject:
        expr = self.visit(node.case_expr, scope)
        min = 1e10
        most_suitable_type = 0
        for index, option in enumerate(node.options):
            option_type = self.context.get_type(option.type)
            types_distance = Type.types_distance(expr.type, option_type)
            if types_distance != -1 and types_distance < min:
                most_suitable_type = index
                min = types_distance

        if most_suitable_type == -1:
            raise CoolRuntimeError('Execution error')

        child_scope = scope.create_child()
        new_var_type = self.context.get_type(node.options[most_suitable_type].type)
        new_var_name = node.options[most_suitable_type].id
        child_scope.define_variable(vname=new_var_name, vtype=new_var_type, value=CoolObject(new_var_type))
        case_object = self.visit(node.options[most_suitable_type].expr, child_scope)
        return case_object

    @visitor.when(cool_ast.MethodCallNode)
    def visit(self, node: cool_ast.MethodCallNode, scope: Scope) -> CoolObject:
        expr = self.visit(node.expr, scope) if node.expr is not None else self.current_object
        typex = self.context.get_type(node.type) if node.type is not None else expr.type
        method = expr.get_method(node.id, typex)

        if expr.type.conforms_to(self.context.get_type('Object')) and ('Object', node.id) in self.builtin_functions:
            args = [expr] + [self.visit(arg, scope) for arg in node.args] + [self.context]
            return self.builtin_functions['Object', node.id](*args)

        if expr.type.conforms_to(self.context.get_type('String')) and ('String', node.id) in self.builtin_functions:
            args = [expr] + [self.visit(arg, scope) for arg in node.args] + [self.context]
            return self.builtin_functions['String', node.id](*args)

        if expr.type.conforms_to(self.context.get_type('IO')) and ('IO', node.id) in self.builtin_functions:
            args = [expr] + [self.visit(arg, scope) for arg in node.args] + [self.context]
            return self.builtin_functions['IO', node.id](*args)

        new_scope = Scope()
        new_scope.define_variable('self', expr.type, expr)
        for param_name, param_type, arg in zip(method.param_names, method.param_types, node.args):
            new_scope.define_variable(vname=param_name, vtype=param_type, value=self.visit(arg, scope))

        self.stack.append(self.current_object)
        self.current_object = expr
        method_return = self.visit(method.expression, new_scope)
        self.current_object = self.stack.pop()
        return method_return

    @visitor.when(cool_ast.MethodDeclarationNode)
    def visit(self, node: cool_ast.MethodDeclarationNode, scope: Scope) -> CoolObject:
        return VoidObject() if node.body is None else self.visit(node.body, scope)

    @visitor.when(cool_ast.VariableNode)
    def visit(self, node: cool_ast.VariableNode, scope: Scope) -> CoolObject:
        var = scope.find_variable(node.lex)
        if var is None:
            objectx = self.current_object.get_attribute(node.lex)
            if isinstance(objectx, Attribute):
                new_scope = Scope()
                new_scope.define_variable('self', self.current_object.type, self.current_object)
                objectx = self.visit(objectx.expression, new_scope)
                self.current_object.set_attribute(node.lex, objectx)
            return objectx
        return var.value

    @visitor.when(cool_ast.AssignNode)
    def visit(self, node: cool_ast.AssignNode, scope: Scope) -> CoolObject:
        expr = self.visit(node.expr, scope)
        var = scope.find_variable(node.id)
        if var is not None:
            var.value = expr
        else:
            self.current_object.set_attribute(node.id, expr)
        return expr

    @visitor.when(cool_ast.NotNode)
    def visit(self, node: cool_ast.NotNode, scope: Scope) -> CoolObject:
        return CoolObject(self.context.get_type('Bool'), not self.visit(node.expr, scope))

    @visitor.when(cool_ast.IsVoidNode)
    def visit(self, node: cool_ast.IsVoidNode, scope: Scope) -> CoolObject:
        return CoolObject(self.context.get_type('Bool'), isinstance(self.visit(node.expr, scope), VoidObject))

    @visitor.when(cool_ast.ConstantNumNode)
    def visit(self, node: cool_ast.ConstantNumNode, scope: Scope) -> CoolObject:
        return CoolObject(self.context.get_type('Int'), int(node.lex))

    @visitor.when(cool_ast.InstantiateNode)
    def visit(self, node: cool_ast.InstantiateNode, scope: Scope) -> CoolObject:
        return CoolObject(self.context.get_type(node.lex))

    @visitor.when(cool_ast.BooleanNode)
    def visit(self, node: cool_ast.BooleanNode, scope: Scope) -> CoolObject:
        return CoolObject(self.context.get_type('Bool'), node.lex == 'true')

    @visitor.when(cool_ast.StringNode)
    def visit(self, node: cool_ast.StringNode, scope: Scope) -> CoolObject:
        return CoolObject(self.context.get_type('String'), node.lex)

    @visitor.when(cool_ast.BinaryNode)
    def visit(self, node: cool_ast.BinaryNode, scope: Scope) -> CoolObject:
        left = self.visit(node.left, scope)
        right = self.visit(node.right, scope)
        return self.operate(node, left.value, right.value)

    @visitor.on('node')
    def operate(self, node, left, right) -> CoolObject:
        pass

    @visitor.when(cool_ast.PlusNode)
    def operate(self, node, left, right):
        return CoolObject(self.context.get_type('Int'), left + right)

    @visitor.when(cool_ast.MinusNode)
    def operate(self, node, left, right):
        return CoolObject(self.context.get_type('Int'), left - right)

    @visitor.when(cool_ast.StarNode)
    def operate(self, node, left, right):
        return CoolObject(self.context.get_type('Int'), left * right)

    @visitor.when(cool_ast.DivNode)
    def operate(self, node, left, right):
        return CoolObject(self.context.get_type('Int'), left // right)

    @visitor.when(cool_ast.EqualsNode)
    def operate(self, node, left, right):
        return CoolObject(self.context.get_type('Bool'), left == right)

    @visitor.when(cool_ast.LessOrEqualNode)
    def operate(self, node, left, right):
        return CoolObject(self.context.get_type('Bool'), left <= right)

    @visitor.when(cool_ast.LessNode)
    def operate(self, node, left, right):
        return CoolObject(self.context.get_type('Bool'), left < right)
