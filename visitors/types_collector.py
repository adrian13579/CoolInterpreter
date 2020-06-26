from ast import ProgramNode, ClassDeclarationNode
from cmp import visitor
from cmp.semantic import Context, IntType, VoidType, ErrorType, SemanticError, Type, ObjectType, StringType, BoolType


class TypeCollector(object):
    def __init__(self, errors=None):
        if errors is None:
            errors = []
        self.context = None
        self.errors = errors

    @visitor.on('node')
    def visit(self, node):
        pass

    @visitor.when(ProgramNode)
    def visit(self, node: ProgramNode):
        self.context = Context()
        self.context.types['<error>'] = ErrorType()
        self.context.types['Void'] = VoidType()
        self_type = self.context.types['SELF_TYPE'] = Type('SELF_TYPE')
        self.context.types['AUTO_TYPE'] = Type('AUTO_TYPE')

        objectx = self.context.types['Object'] = ObjectType()
        intx = self.context.types['Int'] = IntType()
        string = self.context.types['String'] = StringType()
        boolx = self.context.types['Bool'] = BoolType()
        IO = self.context.types['IO'] = Type('IO')

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
        except:
            self.context.create_type(node.id)
