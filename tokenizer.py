from cmp.lexer.lexer import Lexer
from grammar import G

alf = 'a|b|c|d|f|e|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z|A|B|C|D|E|F|G|H|I|J|K|L|M|N|O|P|Q|R|S|T|U|V|X|Y|Z'
num = '1|2|3|4|5|6|7|8|9|0'
intx = '[[1|2|3|4|5|6|7|8|9][0|1|2|3|4|5|6|7|8|9]@]|[0]'
string = f'"[{alf}| |_|{num}|\n|\b|\t|\f]@"'
idx = f'[[[{alf}|_]@][{alf}|_|{num}]@]|[{alf}|_]@'
comment_dashes = f'--[{alf}|_| |{num}]@\n'
comment_star = f'*[{alf}|_| |\n|{num}]@*'


class CoolTokenizer:
    def __init__(self):
        self.lexer = Lexer([
            ('class', 'class'),
            ('inherits', 'inherits'),
            ('self', 'self'),
            ('let', 'let'),
            ('assigment', '<-'),
            ('if', 'if'),
            ('then', 'then'),
            ('else', 'else'),
            ('fi', 'fi'),
            ('while', 'while'),
            ('loop', 'loop'),
            ('pool', 'pool'),
            ('case', 'case'),
            ('of', 'of'),
            ('esac', 'esac'),
            ('case_assigment', '=>'),
            ('new', 'new'),
            ('isvoid', 'isvoid'),
            ('equal', '='),
            ('less', '<'),
            ('less_equal', '<='),
            ('plus', '+'),
            ('minus', '-'),
            ('star', '*'),
            ('div', '/'),
            ('semi', ';'),
            ('colon', ':'),
            ('comma', ','),
            ('dot', '.'),
            ('opar', '('),
            ('cpar', ')'),
            ('ocur', '{'),
            ('ccur', '}'),
            ('in', 'in'),
            ('not', 'not'),
            ('id', idx),
            ('int', intx),
            ('string', string),
            ('true', 'true'),
            ('false', 'false'),
            # f'[{intx}|{string}|{idx}]'),
            ('new_line', '\n'),
            ('space', '[ ]@'),
            ('comment', f'{comment_dashes}|{comment_star}')
        ], G.EOF)

    def __call__(self, text: str):
        tokens = self.lexer(text)
        col = 1
        row = 1
        for token in tokens:
            if token.token_type == 'space':
                col += len(token.lex)
            elif token.token_type == 'new_line':
                row += 1
                col = 1
            elif token.token_type == 'comment':
                new_lines = token.lex.count('\n')
                row += new_lines
                col = 1
                if new_lines == 0:
                    col += len(token.lex)
                else:
                    index = token.lex.rfind('\n')
                    col += token.lex[index:].count(' ')
            else:
                token.col = col
                token.row = row
                col += len(token.lex)
                yield token
