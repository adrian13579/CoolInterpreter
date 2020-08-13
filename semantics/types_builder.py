from typing import List
from ast import ProgramNode, ClassDeclarationNode, MethodDeclarationNode, VarDeclarationNode, AttrDeclarationNode
from cmp import visitor
from utils import Type, SemanticError, ErrorType, Context, Method


class TypeBuilder:
    def __init__(self, context: Context, errors: List[str] = None):
        if errors is None:
            errors = []
        self.context = context
        self.current_type = None
        self.errors = errors
        self.non_inherit = (
            self.context.get_type('String'),
            self.context.get_type('Int'),
            self.context.get_type('Bool'),
            self.context.get_type('AUTO_TYPE'),
            self.context.get_type('SELF_TYPE'),
        )

    @visitor.on('node')
    def visit(self, node):
        pass

    @visitor.when(ProgramNode)
    def visit(self, node: ProgramNode):
        for declaration in node.declarations:
            self.visit(declaration)

        try:
            main: Type = self.context.get_type('Main')
            if main.parent not in (self.context.get_type('Object'), self.context.get_type('IO')):
                self.errors.append('Class Main cannot inherit from another class')
            try:
                method: Method = main.get_method('main')
                if len(method.param_names) != 0:
                    self.errors.append('the Main class must have a method main that takes no formal parameters')
            except:
                self.errors.append('The Main class must have a method main')
        except:
            self.errors.append('Every program must have a class Main.')

    @visitor.when(ClassDeclarationNode)
    def visit(self, node: ClassDeclarationNode):
        self.current_type: Type = self.context.get_type(node.id)
        if node.parent is not None:
            try:
                parent_type: Type = self.context.get_type(node.parent)
                self.current_type.parent = parent_type
                if parent_type in self.non_inherit:
                    self.errors.append(f'It is an error to inherit from type  {parent_type}')
            except SemanticError as error:
                self.errors.append(str(error))
                self.current_type.parent = ErrorType()
        else:
            self.current_type.parent = self.context.get_type('Object')

        for feature in node.features:
            self.visit(feature)

    @visitor.when(MethodDeclarationNode)
    def visit(self, node: MethodDeclarationNode):
        param_names = []
        param_types = []
        for param in node.params:
            param: VarDeclarationNode
            try:
                param_type: Type = self.context.get_type(param.typex)
                if param_type.name == 'SELF_TYPE':
                    param_type = self.current_type
            except SemanticError as error:
                self.errors.append(str(error))
                param_type = ErrorType()
            param_names.append(param.id)
            param_types.append(param_type)

        try:
            return_type = self.context.get_type(node.type)
            if return_type.name == 'SELF_TYPE':
                return_type = self.current_type
        except SemanticError as error:
            self.errors.append(str(error))
            return_type = ErrorType()

        try:
            self.current_type.define_method(node.id, param_names, param_types, return_type)
        except SemanticError as error:
            self.errors.append(str(error))

    @visitor.when(AttrDeclarationNode)
    def visit(self, node: AttrDeclarationNode):
        att_type: Type
        try:
            att_type = self.context.get_type(node.typex)
        except SemanticError as error:
            self.errors.append(str(error))
            att_type = ErrorType()

        try:
            self.current_type.define_attribute(node.id, att_type)
        except SemanticError as error:
            self.errors.append(str(error))
