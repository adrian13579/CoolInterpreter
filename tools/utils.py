from typing import List

from cmp.parsers.lr1_parser import LR1Parser
# from cmp.tools.parsing import LR1Parser
from cmp.semantic import Type, ErrorType
from tokenizer import CoolTokenizer, G
import dill
import os


class TokenizerHandler:
    def __init__(self):
        self._tokenizer = None

    def create(self):
        self._tokenizer = CoolTokenizer()
        return self._tokenizer

    def save(self, path):
        if self._tokenizer is None:
            raise Exception('You must create an instance of tokenizer first')
        else:
            with open(path, 'wb') as lexer:
                dill.dump(self._tokenizer, lexer)

    @staticmethod
    def load(path: str):
        with open(path, 'rb') as lexer:
            return dill.load(lexer)


class ParserHandler:
    def __init__(self):
        self._parser = None

    def create(self):
        self._parser = LR1Parser(G)
        return self._parser

    def save(self, path):
        if self._parser is None:
            raise Exception('You must create an instance of tokenizer first')
        else:
            with open(path, 'wb') as parser:
                dill.dump(self._parser, parser)

    @staticmethod
    def load(path):
        with open(path, 'rb') as parser:
            return dill.load(parser)


def least_type(*types) -> Type:
    types = list(types)
    typex: Type = types[0]
    for i in range(1, len(types)):
        typex = least_type_aux(typex, types[i])
    return typex


def least_type_aux(a: Type, b: Type) -> Type:
    if a or b is None:
        return ErrorType()
    while a != b:
        if a.conforms_to(b):
            a = a.parent
        else:
            b = b.parent
    return a


def ancestors(a: Type) -> List[Type]:
    elders = [a]
    while a.parent is not None:
        a = a.parent
        elders.append(a)
    return elders


WRONG_SIGNATURE = 'Method "%s" already defined in "%s" with a different signature.'
SELF_IS_READONLY = 'Variable "self" is read-only.'
LOCAL_ALREADY_DEFINED = 'Variable "%s" is already defined in method "%s".'
INCOMPATIBLE_TYPES = 'Cannot convert "%s" into "%s".'
VARIABLE_NOT_DEFINED = 'Variable "%s" is not defined in "%s".'
INVALID_OPERATION = 'Operation is not defined between "%s" and "%s".'

if __name__ == '__main__':
    t = TokenizerHandler()
    t.create()
    t.save("/mnt/69F79531507E7A36/CS/This year's stuff/Compilacion/Proyectos/CoolInterpreter/tools/lexer")

    p = ParserHandler()
    p.create()
    p.save("/mnt/69F79531507E7A36/CS/This year's stuff/Compilacion/Proyectos/CoolInterpreter/tools/parser")
