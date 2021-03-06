from cmp.lexer.lexer import Lexer
from cmp.utils import Token
from grammar import *


class CoolTokenizer:
    def __init__(self):
        self.lexer = Lexer([
            ('comment', f'{comment_dashes}§{comment_star}'),
            (idx, identifier),
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
            (intx, integer),
            (string, stringx),
            (true, 'true'),
            (false, 'false'),
            ('new_line', '\\n'),
            ('space', '« »∀'),
            ('tab', '\\t'),
        ], G.EOF)

    def __call__(self, input_text: str) -> List[Token]:
        text = ""
        for i in input_text:
            if i == '\n':
                text += '\\n'
            elif i == '\t':
                text += '\\t'
            elif i == '\'':
                pass
            else:
                text += i

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
                if token.token_type.Name == string.Name:
                    new_lex = token.lex.replace('"', '')
                    new_lex = new_lex.replace('\\n', '\n')
                    new_lex = new_lex.replace('\\t', '\t')
                    token.lex = new_lex
                token.col = col
                token.row = row
                col += len(token.lex)
                ret_token.append(token)
        return ret_token


'''
Regex operators:
« equals ( 
» equals )
∀ equals *
§ equals |
'''

alf = 'a§b§c§d§f§e§g§h§i§j§k§l§m§n§o§p§q§r§s§t§u§v§w§x§y§z§A§B§C§D§E§F§G§H§I§J§K§L§M§N§O§P§Q§R§S§T§U§V§W§X§Y§Z'
symbol = '`§~§!§@§#§$§%§^§&§*§(§)§-§_§|§=§+§{§}§[§]§;§:§<§>§,§.§?§/§\\'
num = '1§2§3§4§5§6§7§8§9§0'
integer = '««1§2§3§4§5§6§7§8§9»«0§1§2§3§4§5§6§7§8§9»∀»§«0»'

stringx = f'"«{alf}§ §{symbol}§{num}»∀"'
identifier = f'«_»∀«{alf}»«{alf}§_§{num}»∀'
comment_dashes = f'«--«{alf}§{symbol}§ §{num}»∀\\n»'
comment_star = f"«(*«{alf}§{symbol}§ §{num}»∀*)»"
