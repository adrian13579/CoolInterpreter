import itertools as itt
from collections import OrderedDict
from typing import List, Dict, Optional, Union, Any


class SemanticError(Exception):
    @property
    def text(self) -> str:
        return self.args[0]


class CoolRuntimeError(Exception):
    @property
    def text(self) -> str:
        return self.args[0]


class Type:
    def __init__(self, name: str):
        self.name = name
        self.attributes: List[Attribute] = []
        self.methods: List[Method] = []
        self.parent = None

    @staticmethod
    def types_distance(a: 'Type', b: 'Type') -> int:
        distance = 0
        if a.conforms_to(b):
            down, up = a, b
        elif b.conforms_to(a):
            down, up = b, a
        else:
            return -1
        while down != up:
            down = down.parent
            distance += 1
        return distance

    @staticmethod
    def least_type(*types) -> 'Type':
        types = list(types)
        typex: Type = types[0]
        for i in range(1, len(types)):
            typex = Type.least_type_aux(typex, types[i])
        return typex

    @staticmethod
    def least_type_aux(a: 'Type', b: 'Type') -> 'Type':
        if a is None or b is None:
            return ErrorType()
        while a != b:
            if a.conforms_to(b):
                a = a.parent
            else:
                b = b.parent
        return a

    @staticmethod
    def ancestors(a: 'Type') -> List['Type']:
        elders = [a]
        while a.parent is not None:
            a = a.parent
            elders.append(a)
        return elders

    def set_parent(self, parent):
        if self.parent is not None:
            raise SemanticError(f'Parent type is already set for {self.name}.')
        self.parent = parent

    def get_attribute(self, name: str):
        try:
            return next(attr for attr in self.attributes if attr.name == name)
        except StopIteration:
            if self.parent is None:
                raise SemanticError(f'Attribute "{name}" is not defined in {self.name}.')
            try:
                return self.parent.get_attribute(name)
            except SemanticError:
                raise SemanticError(f'Attribute "{name}" is not defined in {self.name}.')

    def define_attribute(self, name: str, typex):
        try:
            self.get_attribute(name)
        except SemanticError:
            attribute = Attribute(name, typex)
            self.attributes.append(attribute)
            return attribute
        else:
            raise SemanticError(f'Attribute "{name}" is already defined in {self.name}.')

    def get_method(self, name: str):
        try:
            return next(method for method in self.methods if method.name == name)
        except StopIteration:
            if self.parent is None:
                raise SemanticError(f'Method "{name}" is not defined in {self.name}.')
            try:
                return self.parent.get_method(name)
            except SemanticError:
                raise SemanticError(f'Method "{name}" is not defined in {self.name}.')

    def define_method(self, name: str, param_names: list, param_types: list, return_type):
        if name in (method.name for method in self.methods):
            raise SemanticError(f'Method "{name}" already defined in {self.name}')

        method = Method(name, param_names, param_types, return_type)
        self.methods.append(method)
        return method

    def all_attributes(self, clean=True):
        plain = OrderedDict() if self.parent is None else self.parent.all_attributes(False)
        for attr in self.attributes:
            plain[attr.name] = (attr, self)
        return plain.values() if clean else plain

    def all_methods(self, clean=True):
        plain = OrderedDict() if self.parent is None else self.parent.all_methods(False)
        for method in self.methods:
            plain[method.name] = (method, self)
        return plain.values() if clean else plain

    def conforms_to(self, other):
        return other.bypass() or self == other or self.parent is not None and self.parent.conforms_to(
            other)

    def bypass(self):
        return False

    def __str__(self):
        output = f'type {self.name}'
        parent = '' if self.parent is None else f' : {self.parent.name}'
        output += parent
        output += ' {'
        output += '\n\t' if self.attributes or self.methods else ''
        output += '\n\t'.join(str(x) for x in self.attributes)
        output += '\n\t' if self.attributes else ''
        output += '\n\t'.join(str(x) for x in self.methods)
        output += '\n' if self.methods else ''
        output += '}\n'
        return output

    def __repr__(self):
        return str(self)


class VoidType(Type):
    def __init__(self):
        Type.__init__(self, 'void')


class ErrorType(Type):
    def __init__(self):
        Type.__init__(self, '<error>')

    def conforms_to(self, other: Type) -> bool:
        return True

    def bypass(self) -> bool:
        return True

    def __eq__(self, other: Type):
        return isinstance(other, Type)


class TypeVariable(Type):
    next_var_type_id = 0

    def __init__(self):
        super().__init__('T{id}'.format(id=TypeVariable.next_var_type_id))
        TypeVariable.next_var_type_id += 1


class FunctionType(Type):
    def __init__(self, params_types: List[Type], return_type: Type):
        super().__init__('Function')
        self.params_types = params_types
        self.return_type = return_type

    def __eq__(self, other):
        if not isinstance(other, FunctionType):
            return False
        if len(self.params_types) != len(other.params_types):
            return False
        for i, j in zip(self.params_types, other.params_types):
            if i != j:
                return False
        return True


class Method:
    def __init__(self, name: str, param_names: List[str], params_types: List[Type], return_type: Type):
        self.name = name
        self.param_names = param_names
        self.param_types = params_types
        self.return_type = return_type

    def __str__(self):
        params = ', '.join(f'{n}:{t.name}' for n, t in zip(self.param_names, self.param_types))
        return f'[method] {self.name}({params}): {self.return_type.name};'

    def __eq__(self, other):
        return other.name == self.name and \
               other.return_type == self.return_type and \
               other.param_types == self.param_types


class Attribute:
    def __init__(self, name: str, typex: Type):
        self.name = name
        self.type = typex

    def __str__(self):
        return f'[attrib] {self.name} : {self.type.name};'

    def __repr__(self):
        return str(self)


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

    def set_attibute(self, name: str, value: 'CoolObject') -> None:
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


class Context:
    def __init__(self):
        self.types: Dict[str, Type] = {}

    def create_type(self, name: str) -> Type:
        if name in self.types:
            raise SemanticError(f'Type with the same name ({name}) already in context.')
        typex = self.types[name] = Type(name)
        return typex

    def get_type(self, name: str) -> Type:
        try:
            return self.types[name]
        except KeyError:
            raise SemanticError(f'Type "{name}" is not defined.')

    def __str__(self):
        return '{\n\t' + '\n\t'.join(y for x in self.types.values() for y in str(x).split('\n')) + '\n}'

    def __repr__(self):
        return str(self)


class VariableInfo:
    def __init__(self, name: str, vtype: Type, value=None):
        self.name = name
        self.type = vtype
        self.value = value


class Scope:
    def __init__(self, parent=None):
        self.locals: List[VariableInfo] = []
        self.parent: Scope = parent
        self.children: List[Scope] = []
        self.index: int = 0 if parent is None else len(parent)

    def __len__(self):
        return len(self.locals)

    def create_child(self) -> 'Scope':
        child = Scope(self)
        self.children.append(child)
        return child

    def define_variable(self, vname: str, vtype: Type, value: CoolObject = None) -> VariableInfo:
        info = VariableInfo(vname, vtype, value)
        self.locals.append(info)
        return info

    def find_variable(self, vname, index=None) -> Optional[VariableInfo]:
        _locals = self.locals if index is None else itt.islice(self.locals, index)
        try:
            return next(x for x in _locals if x.name == vname)
        except StopIteration:
            return self.parent.find_variable(vname, self.index) if self.parent is not None else None

    def is_defined(self, vname) -> bool:
        return self.find_variable(vname) is not None

    def is_local(self, vname) -> bool:
        return any(True for x in self.locals if x.name == vname)
