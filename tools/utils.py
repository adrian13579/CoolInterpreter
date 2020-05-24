# from cmp.parsers.lr1_parser import LR1Parser
from cmp.tools.parsing import LR1Parser
from tokenizer import CoolTokenizer, G
import dill


class TokenizerHandler:
    def __init__(self):
        self._tokenizer = None

    def create(self):
        self._tokenizer = CoolTokenizer()
        return self._tokenizer

    def save(self):
        if self._tokenizer is None:
            raise Exception('You must create an instance of tokenizer first')
        else:
            with open('/mnt/69F79531507E7A36/CS/MyStuff/Compilacion/Proyectos/CoolInterpreter/tools/lexer',
                      'wb') as lexer:
                dill.dump(self._tokenizer, lexer)

    @staticmethod
    def load():
        with open('/mnt/69F79531507E7A36/CS/MyStuff/Compilacion/Proyectos/CoolInterpreter/tools/lexer', 'rb') as lexer:
            return dill.load(lexer)


class ParserHandler:
    def __init__(self):
        self._parser = None

    def create(self):
        self._parser = LR1Parser(G)
        return self._parser

    def save(self):
        if self._parser is None:
            raise Exception('You must create an instance of tokenizer first')
        else:
            with open('/mnt/69F79531507E7A36/CS/MyStuff/Compilacion/Proyectos/CoolInterpreter/tools/parser',
                      'wb') as parser:
                dill.dump(self._parser, parser)

    @staticmethod
    def load():
        with open('/mnt/69F79531507E7A36/CS/MyStuff/Compilacion/Proyectos/CoolInterpreter/tools/parser',
                  'rb') as parser:
            return dill.load(parser)


if __name__ == '__main__':
    t = TokenizerHandler()
    t.create()
    t.save()

    p = ParserHandler()
    p.create()
    p.save()
