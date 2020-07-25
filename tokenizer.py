from cmp.lexer.lexer import Lexer
from cmp.utils import Token
from grammar import *


class CoolTokenizer:
    def __init__(self):
        self.lexer = Lexer([
            (classx, 'class'),
            (inherits, 'inherits'),
            (let, 'let'),
            (assigment, '<-'),
            (ifx, 'if'),
            (thenx, 'then'),
            (elsex, 'else'),
            (fi, 'fi'),
            (whilex, 'while'),
            (loop, 'loop'),
            (pool, 'pool'),
            (case, 'case'),
            (of, 'of'),
            (esac, 'esac'),
            (case_assigment, '=>'),
            (new, 'new'),
            (isvoid, 'isvoid'),
            (equal, '='),
            (less, '<'),
            (less_equal, '<='),
            (plus, '+'),
            (minus, '-'),
            (star, '*'),
            (div, '/'),
            (semi, ';'),
            (colon, ':'),
            (comma, ','),
            (dot, '.'),
            (opar, '('),
            (cpar, ')'),
            (ocur, '{'),
            (ccur, '}'),
            (inx, 'in'),
            (notx, 'not'),
            (at, '@'),
            (idx, identifier),
            (intx, integer),
            (string, stringx),
            (true, 'true'),
            (false, 'false'),
            ('new_line', '\n'),
            ('space', '« »∀'),
            ('tab', '\t'),
            ('comment', f'{comment_dashes}§{comment_star}')
        ], G.EOF)

    def __call__(self, text: str) -> List[Token]:
        tokens: List[Token] = self.lexer(text)
        col = 1
        row = 1
        ret_token = []
        for token in tokens:
            if token.token_type == 'space':
                col += len(token.lex)
            elif token.token_type == 'new_line':
                row += 1
                col = 1
            elif token.token_type == 'tab':
                col += 4
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
                ret_token.append(token)
        return ret_token


'« » ∀ §'
alf = 'a§b§c§d§f§e§g§h§i§j§k§l§m§n§o§p§q§r§s§t§u§v§w§x§y§z§A§B§C§D§E§F§G§H§I§J§K§L§M§N§O§P§Q§R§S§T§U§V§W§X§Y§Z'
num = '1§2§3§4§5§6§7§8§9§0'
integer = '««1§2§3§4§5§6§7§8§9»«0§1§2§3§4§5§6§7§8§9»∀»§«0»'
stringx = f'"«{alf}§.§;§:§(§)§.§,§:§;§ §_§{num}§\§n§b§t§f»∀"'
identifier = f'«_»∀«{alf}»«{alf}§_§{num}»∀'
comment_dashes = f'--«{alf}§_§ §{num}»∀\n'
comment_star = f'(*«{alf}§_§ §\n§{num}»∀*)'

# TODO  Fix Problem: Tokenizer does not recognize comment of the form (*...*)
