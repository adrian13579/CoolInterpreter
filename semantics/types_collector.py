from typing import List

from cool_ast import ProgramNode, ClassDeclarationNode
from cmp import visitor
from semantics.utils import Context, ErrorType, Type, VoidType, SemanticError


class TypeCollector(object):
    def __init__(self, context: Context, errors: List[str]):
        self.context = context
        self.errors = errors

    @visitor.on('node')
    def visit(self, node):
        pass

    @visitor.when(ProgramNode)
    def visit(self, node: ProgramNode):
        self.context.types['<error>'] = ErrorType()
        self.context.types['Void'] = VoidType()
        self_type = self.context.types['SELF_TYPE'] = Type('SELF_TYPE')
        auto_type = self.context.types['AUTO_TYPE'] = Type('AUTO_TYPE')
        objectx = self.context.types['Object'] = Type('Object')
        intx = self.context.types['Int'] = Type('Int')
        string = self.context.types['String'] = Type('String')
        boolx = self.context.types['Bool'] = Type('Bool')
        IO = self.context.types['IO'] = Type('IO')

        # self_type.parent = objectx
        objectx.define_method(name='abort', param_names=[], param_types=[], return_type=objectx)
        objectx.define_method(name='type_name', param_names=[], param_types=[], return_type=string)
        objectx.define_method(name='copy', param_names=[], param_types=[], return_type=self_type)
        IO.parent = objectx
        IO.define_method(name='out_string', param_names=['x'], param_types=[string], return_type=self_type)
        IO.define_method(name='out_int', param_names=['x'], param_types=[intx], return_type=self_type)
        IO.define_method(name='in_string', param_names=[], param_types=[], return_type=string)
        IO.define_method(name='in_int', param_names=[], param_types=[], return_type=intx)
        intx.parent = objectx
        boolx.parent = objectx
        string.parent = objectx
        string.define_method(name='length', param_names=[], param_types=[], return_type=intx)
        string.define_method(name='concat', param_names=['s'], param_types=[string], return_type=string)
        string.define_method(name='substr', param_names=['i', 'l'], param_types=[intx, intx], return_type=string)

        for declaration in node.declarations:
            self.visit(declaration)

    @visitor.when(ClassDeclarationNode)
    def visit(self, node: ClassDeclarationNode):
        try:
            self.context.get_type(node.id)
        except SemanticError:
            self.context.create_type(node.id)
