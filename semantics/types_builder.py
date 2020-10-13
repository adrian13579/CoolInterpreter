from typing import List, Dict
from cmp import visitor
import cool_ast
from semantics.utils import Type, SemanticError, ErrorType, Context, Method


class TypeBuilder:
    def __init__(self, context: Context, errors: List[str] = None):
        if errors is None:
            errors = []
        self.context = context
        self.current_type = None
        self.errors = errors
        self.non_inherit = None

        self.__hierarchy_tree: Dict[str, List[str]] = {
            'Object': ['Int', 'String', 'Bool', 'IO'],
            'Int': [],
            'String': [],
            'Bool': [],
            'IO': []
        }

    def __add_node(self, node):
        if node not in self.__hierarchy_tree:
            self.__hierarchy_tree[node] = []

    def __add_edge(self, node, parent):
        try:
            if node not in self.__hierarchy_tree[parent]:
                self.__hierarchy_tree[parent].append(node)
        except KeyError:
            self.__hierarchy_tree[parent] = [node]

    @visitor.on('node')
    def visit(self, node):
        pass

    @visitor.when(cool_ast.ProgramNode)
    def visit(self, node: cool_ast.ProgramNode):
        self.non_inherit = (
            self.context.get_type('String'),
            self.context.get_type('Int'),
            self.context.get_type('Bool'),
            self.context.get_type('AUTO_TYPE'),
            self.context.get_type('SELF_TYPE'),
        )

        for declaration in node.declarations:
            self.visit(declaration)

        try:
            main: Type = self.context.get_type('Main')
            if main.parent not in (self.context.get_type('Object'), self.context.get_type('IO')):
                self.errors.append(f'Class Main cannot inherit from  class {main.parent.name}')
            try:
                method: Method = main.get_method('main')
                if len(method.param_names) != 0:
                    self.errors.append('The Main class must have a method main that takes no formal parameters')
            except SemanticError:
                self.errors.append('The Main class must have a method main')
        except SemanticError:
            self.errors.append('Every program must have a class Main.')

        try:
            check_tree(self.__hierarchy_tree)
        except SemanticError as error:
            self.errors.append(str(error))

    @visitor.when(cool_ast.ClassDeclarationNode)
    def visit(self, node: cool_ast.ClassDeclarationNode):
        self.current_type: Type = self.context.get_type(node.id)
        self.__add_node(node.id)
        if node.parent is not None:
            try:
                parent_type: Type = self.context.get_type(node.parent)
                self.current_type.parent = parent_type

                self.__add_edge(node.id, node.parent)

                if parent_type in self.non_inherit:
                    self.errors.append(f'It is an error to inherit from type {parent_type}')
            except SemanticError as error:
                self.errors.append(str(error))
                self.current_type.parent = ErrorType()
        else:
            self.current_type.parent = self.context.get_type('Object')
            self.__add_edge(node.id, 'Object')
        for feature in node.features:
            self.visit(feature)

    @visitor.when(cool_ast.MethodDeclarationNode)
    def visit(self, node: cool_ast.MethodDeclarationNode):
        param_names = []
        param_types = []
        for param in node.params:
            param: cool_ast.VarDeclarationNode
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

    @visitor.when(cool_ast.AttrDeclarationNode)
    def visit(self, node: cool_ast.AttrDeclarationNode):
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


def visit_node(node: str, graph: Dict[str, List[str]], visited: Dict[str, bool], path: List[str]) -> None:
    for adj_node in graph[node]:
        if adj_node in visited:
            path.pop()
            raise SemanticError('Cyclic reference: ' + '->'.join([class_name for class_name in path]))
        else:
            path.append(adj_node)
            visit_node(adj_node, graph, visited, path)
            path.pop()
            visited[adj_node] = True


def check_tree(graph: Dict[str, List[str]]) -> None:
    visited: Dict[str, bool] = {}
    path: List[str] = []
    for node in graph:
        if node not in visited:
            path.append(node)
            visit_node(node, graph, visited, path)
            path.pop()
            visited[node] = True
