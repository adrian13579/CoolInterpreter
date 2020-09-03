import os

import dill
from cmp.parsers.lr1_parser import LR1Parser
from tokenizer import CoolTokenizer, G


class TokenizerHandler:
    def __init__(self):
        self._tokenizer = None

    def create(self) -> CoolTokenizer:
        self._tokenizer = CoolTokenizer()
        return self._tokenizer

    def save(self, path):
        if self._tokenizer is None:
            raise Exception('You must create an instance of tokenizer first')
        else:
            with open(path, 'wb') as lexer:
                dill.dump(self._tokenizer, lexer)

    @staticmethod
    def load(path: str) -> CoolTokenizer:
        with open(path, 'rb') as lexer:
            return dill.load(lexer)


class ParserHandler:
    def __init__(self):
        self._parser = None

    def create(self) -> LR1Parser:
        self._parser = LR1Parser(G)
        return self._parser

    def save(self, path):
        if self._parser is None:
            raise Exception('You must create an instance of parser first')
        else:
            with open(path, 'wb') as parser:
                dill.dump(self._parser, parser)

    @staticmethod
    def load(path) -> LR1Parser:
        with open(path, 'rb') as parser:
            return dill.load(parser)


if __name__ == '__main__':
    a = os.getcwd()
    t = TokenizerHandler()
    t.create()
    t.save(os.getcwd() + '/lexer')

    # p = ParserHandler()
    # p.create()
    # p.save(os.getcwd() + '/parser')
