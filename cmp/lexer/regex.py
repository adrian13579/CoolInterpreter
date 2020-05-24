from cmp.automata import NFA, DFA, nfa_to_dfa
from cmp.automata import automata_union, automata_concatenation, automata_minimization, automata_closure
from cmp.evaluation import evaluate_parse
from cmp.pycompiler import Grammar, EOF
from cmp.utils import Token
from cmp.first_follow import compute_firsts, compute_follows
from cmp.parsers.ll1_parser import metodo_predictivo_no_recursivo, build_parsing_table


class Node:
    def evaluate(self):
        raise NotImplementedError()


class AtomicNode(Node):
    def __init__(self, lex):
        self.lex = lex


class UnaryNode(Node):
    def __init__(self, node):
        self.node = node

    def evaluate(self):
        value = self.node.evaluate()
        return self.operate(value)

    @staticmethod
    def operate(value):
        raise NotImplementedError()


class BinaryNode(Node):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def evaluate(self):
        lvalue = self.left.evaluate()
        rvalue = self.right.evaluate()
        return self.operate(lvalue, rvalue)

    @staticmethod
    def operate(lvalue, rvalue):
        raise NotImplementedError()


class EpsilonNode(AtomicNode):
    def evaluate(self):
        return NFA(states=1, finals=[0], transitions={})


class SymbolNode(AtomicNode):
    def evaluate(self):
        s = self.lex
        return NFA(states=2, finals=[1], transitions={(0, s): [1]})


class ClosureNode(UnaryNode):
    @staticmethod
    def operate(value):
        return automata_closure(value)


class UnionNode(BinaryNode):
    @staticmethod
    def operate(lvalue, rvalue):
        return automata_union(lvalue, rvalue)


class ConcatNode(BinaryNode):
    @staticmethod
    def operate(lvalue, rvalue):
        return automata_concatenation(lvalue, rvalue)


G = Grammar()
E = G.NonTerminal('E', True)
T, F, A, X, Y, Z = G.NonTerminals('T F A X Y Z')
pipe, star, opar, cpar, symbol, epsilon = G.Terminals('§ ∀ « » symbol ε')

E %= T + X, lambda h, s: s[2], None, lambda h, s: s[1]
X %= pipe + T + X, lambda h, s: s[3], None, None, lambda h, s: UnionNode(h[0], s[2])
X %= G.Epsilon, lambda h, s: h[0]
T %= F + Y, lambda h, s: s[2], None, lambda h, s: s[1]
Y %= F + Y, lambda h, s: s[2], None, lambda h, s: ConcatNode(h[0], s[1])
Y %= G.Epsilon, lambda h, s: h[0]
F %= A + Z, lambda h, s: s[2], None, lambda h, s: s[1]
Z %= star + Z, lambda h, s: s[2], None, lambda h, s: ClosureNode(h[0])
Z %= G.Epsilon, lambda h, s: h[0]
A %= symbol, lambda h, s: SymbolNode(s[1])
A %= opar + E + cpar, lambda h, s: s[2], None, None, None
A %= epsilon, lambda h, s: EpsilonNode(s[1])


def regex_tokenizer(text, G, skip_whitespaces=True):
    tokens = []
    fixed_tokens = {
        '§': Token('§', pipe),
        '∀': Token('∀', star),
        '«': Token('«', opar),
        '»': Token('»', cpar),
        'ε': Token('ε', epsilon)
    }
    for char in text:
        if skip_whitespaces and char.isspace():
            continue
        char_token = ' '
        try:
            char_token = fixed_tokens[char]
        except KeyError:
            char_token = Token(char, symbol)
        tokens.append(char_token)

    tokens.append(Token('$', G.EOF))
    return tokens


class Regex:
    def __init__(self, regex: str):
        self.regex: str = regex
        self.automaton: DFA = self.build_automaton(self.regex)

    def __call__(self, text):
        return self.automaton.recognize(text)

    @staticmethod
    def build_automaton(regex: str) -> DFA:
        first = compute_firsts(G)
        follows = compute_follows(G, first)
        tokens = regex_tokenizer(regex, G, skip_whitespaces=False)
        parsing_table, _ = build_parsing_table(G, first, follows)
        parser = metodo_predictivo_no_recursivo(G, parsing_table)
        left_parse = parser(tokens)
        ast = evaluate_parse(left_parse, tokens)
        nfa = ast.evaluate()
        dfa = nfa_to_dfa(nfa)
        mini = automata_minimization(dfa)
        return mini
