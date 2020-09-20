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


class CoolLexer(ReLexer):
    def __init__(self):
        super().__init__(
            [
                (classx, 'class', r'class(?=\s)'),
                (inherits, 'inherits', r'inherits(?=\s)'),
                (let, 'let', r'let(?=\s)'),
                (assigment, 'assigment', r'<-'),
                (ifx, 'if', r'if(?=\s)'),
                (thenx, 'then', r'then(?=\s)'),
                (elsex, 'else', r'else(?=\s)'),
                (fi, 'fi', r'fi'),
                (whilex, 'while', r'while(?=\s)'),
                (loop, 'loop', r'loop(?=\s)'),
                (pool, 'pool', r'pool'),
                (case, 'case', r'case(?=\s)'),
                (of, 'of', r'of(?=\s)'),
                (esac, 'esac', r'esac(?=\s)'),
                (case_assigment, 'case_assigment', r'=>'),
                (new, 'new', r'new(?=\s)'),
                (isvoid, 'isvoid', r'isvoid(?=\s)'),
                (equal, 'equal', r'='),
                (less, 'less', r'<'),
                (less_equal, 'less_equal', r'<='),
                (plus, 'plus', r'\+'),
                (star, 'star', r'\*'),
                (div, 'div', r'/'),
                (semi, 'semi', r';'),
                (colon, 'colon', r':'),
                (comma, 'comma', r','),
                (dot, 'dot', r'\.'),
                (cpar, 'cpar', r'\)'),
                (ocur, 'ocur', r'{'),
                (ccur, 'ccur', r'}'),
                (inx, 'in', r'in(?=\s)'),
                (notx, 'not', r'not(?=\s)'),
                (at, 'at', r'@'),
                (true, 'true', r'true'),
                (false, 'false', r'false'),
                (intx, 'integer', r'[\d][\d]*'),
                (idx, 'identifier', r'[a-zA-Z][a-zA-Z0-9_]*'),
                (string, 'string', r'\"[^\"]*\"'),
                ('whitespace', 'whitespace', r' +'),
                ('newline', 'newline', r'\n'),
                ('tabulation', 'tabulation', r'\t'),
                ('comment', 'comment', r'(\(\*[\s\S]*?\*\))|(--[^\n]*\n)'),
                (opar, 'opar', r'\('),
                (minus, 'minus', r'-'),
            ], G.EOF
        )

    def __call__(self, text: str) -> Generator[Token, None, None]:
        tokens: Generator[Token, None, None] = super().__call__(text)
        for token in tokens:
            token.row, token.col = self.row, self.column
            if token.token_type not in ('tabulation', 'whitespace', 'newline', 'comment'):
                if token.token_type.Name == string.Name:
                    token.lex = CoolLexer.format_str(token.lex)
                yield token

            if token.token_type == 'tabulation':
                self.column += 4
            elif token.token_type == 'whitespace':
                self.column += len(token.lex)
            elif token.token_type == 'newline':
                self.column = 0
                self.row += 1
            elif str(token.token_type) == string.Name or token.token_type == 'comment':
                new_lines = max(token.lex.count('\n') - token.lex.count('\\n'), 0)
                self.row += new_lines
                print(token.lex)
                if new_lines == 0:
                    self.column += len(token.lex)
                else:
                    index = token.lex.rfind('\n')
                    self.column += len(token.lex[index:]) + 1
            else:
                new_lines = token.lex.count('\n')
                if new_lines != 0:
                    self.row += new_lines
                    self.column = 0
                else:
                    self.column += len(token.lex)

    @staticmethod
    def format_str(string_lex: str) -> str:
        new_lex = ''
        for i in range(1, len(string_lex) - 1):
            new_lex += string_lex[i]
        new_lex = new_lex.replace('\\n', '\n')
        new_lex = new_lex.replace('\\t', '\t')
        return new_lex
