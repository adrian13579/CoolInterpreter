import os
from typing import Any

import dill
from cmp.parsers.lr1_parser import LR1Parser
from re_lexer import CoolLexer
from tokenizer import CoolTokenizer
from grammar import G


class Serializer:
    @staticmethod
    def save(target: Any, path: str) -> bool:
        try:
            with open(path, 'wb') as p:
                dill.dump(target, p)
            return True
        except:
            return False

    @staticmethod
    def load(path: str) -> Any:
        try:
            with open(path, 'rb') as p:
                return dill.load(p)
        except:
            return None


if __name__ == '__main__':
    lexer = CoolLexer()
    Serializer.save(lexer, os.getcwd() + '/lexer')

    # parser = LR1Parser(G)
    # Serializer.save(parser, os.getcwd() + '/parser')
