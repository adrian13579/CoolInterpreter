from typing import Dict, List

from utils import Context, Scope, Type, FunctionType
from cmp import visitor
import ast


class TypesUpdater:
    def __init__(self,
                 context: Context,
                 scope: Scope,
                 functions: Dict[(str, str), FunctionType],
                 attributes: Dict[(str, str), Type],
                 subst: Dict[str, Type],
                 errors: List[str]):
        self.context = context
        self.scope = scope
        self.funcitons = functions
        self.attributes = attributes
        self.subst = subst
        self.errors = errors

    @visitor.on('node')
    def visit(self, node, scope):
        pass
