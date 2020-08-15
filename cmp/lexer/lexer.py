from cmp.automata import State
from cmp.utils import Token
from cmp.lexer.regex import Regex
from grammar import idx


class Lexer:
    def __init__(self, table, eof):
        self.eof = eof
        self.regexs = self._build_regexs(table)
        self.automaton = self._build_automaton()

    @staticmethod
    def _build_regexs(table):
        regexs = []
        for n, (token_type, regex) in enumerate(table):
            NFA = Regex.build_automaton(regex)
            automaton, states = State.from_nfa(NFA, get_states=True)
            for state in automaton:
                if state.final:
                    state.tag = [(n, token_type)]
            regexs.append(automaton)

        return regexs

    def _build_automaton(self):
        start = State('start')
        for automaton in self.regexs:
            start.add_epsilon_transition(automaton)

        return start.to_deterministic()

    def _walk(self, string):
        state = self.automaton
        final = state if state.final else None
        final_lex = lex = ''
        token_type = None
        priority = 500000
        for symbol in string:
            try:
                state = state.get(symbol)
                lex += symbol
                if state.final:
                    if state.tag is not None:
                        for tag in state.tag:
                            if lex == str(tag[1]) and tag[1] != idx:
                                priority, token_type = tag
                                final_lex = lex
                                break
                            elif tag[0] <= priority:
                                priority, token_type = tag
                                final_lex = lex
            except KeyError:
                break

        return token_type, final_lex

    def _tokenize(self, input_text):
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

        while len(text) > 0:
            token_type, lex = self._walk(text)
            yield lex, token_type
            text = text[len(lex):]

        yield '$', self.eof

    def __call__(self, text):
        return [Token(lex, ttype) for lex, ttype in self._tokenize(text)]
