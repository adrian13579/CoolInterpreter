import re
from typing import Dict, Generator, Tuple, Pattern, Any
from grammar import *
from cmp.utils import Token


class ReLexer:
    def __init__(self, regex: List[Tuple[Any, str, str]], eof):
        self.patterns: Pattern = ReLexer._build_regex(regex)
        self.token_types: Dict[Any, str] = ReLexer._get_token_types(regex)
        self.position = 0
        self.EOF = eof
        self.row = 0
        self.column = 0

    @staticmethod
    def _build_regex(regex: List[Tuple[Any, str, str]]) -> Pattern:
        return re.compile(r'|'.join(['(?P<%s>%s)' % (name, regex) for _, name, regex in regex]))

    @staticmethod
    def _get_token_types(regex: List[Tuple[Any, str, str]]) -> Dict[Any, str]:
        token_type = {}
        for terminal, name, _ in regex:
            token_type[name] = terminal
        return token_type

    def __call__(self, text: str) -> Generator[Token, None, None]:
        while self.position < len(text):
            match = self.patterns.match(text, pos=self.position)
            if match is None:
                raise Exception(f'Unknown token in row:{self.row} col:{self.column}')

            lex = match.group()
            token_type = self.token_types[match.lastgroup]
            yield Token(lex, token_type)
            self.position = match.end()

        yield Token('$', self.EOF)


lexer = ReLexer(
    [  # ('comment', r'\(\*[^$]*\*\))|--.*'),
        (classx, 'class', r'class'),
        (inherits, 'inherits', r'inherits'),
        (let, 'let', r'let'),
        (assigment, 'assigment', r'<-'),
        (ifx, 'if', r'if'),
        # (thenx, r'then'),
        # (elsex, r'else'),
        # (fi, r'fi'),
        # (whilex, r'while'),
        # (loop, r'loop'),
        # (pool, r'pool'),
        # (case, r'case'),
        # (of, r'of'),
        # (esac, r'esac'),
        # (case_assigment, r'=>'),
        # (new, r'new'),
        # (isvoid, r'isvoid'),
        # (equal, r'='),
        # (less, r'<'),
        # (less_equal, r'<='),
        # (plus, r'+'),
        # (minus, r'-'),
        # (star, r'*'),
        # (div, r'/'),
        # (semi, r';'),
        # (colon, r':'),
        # (comma, r','),
        # (dot, r'.'),
        # (opar, r'('),
        # (cpar, r')'),
        # (ocur, r'{'),
        # (ccur, r'}'),
        # (inx, r'in'),
        # (notx, r'not'),
        # (at, r'@'),
        (intx, 'integer', r'/d'),
        (idx, 'identifier', r'[a-z][a-zA-Z0-9_]*'),
        (string, 'string', r'\"[^\"]*\"'),
        # (true, r'true'),
        # (false, r'false'),
        # ('whitespace', r' +'),
        # ('newline', r'\n'),
        # ('tabulation', r'\t')
    ], G.EOF
)

code = '''asasasa'''
for token in lexer(code):
    print(token.token_type, token.lex)
