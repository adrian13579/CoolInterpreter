from cmp.automata import State
from cmp.utils import Token
from cmp.lexer.regex import Regex


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
            for state in states:
                if state.final:
                    state.tag = (n, token_type)
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

        for symbol in string:
            try:
                state = state.get(symbol)
                lex += symbol
                if state.final:
                    final = state
                    final_lex = lex
            except KeyError:
                break

        return final, final_lex

    def _tokenize(self, text):
        states = None
        lex = None

        while len(text) > 0:
            states, lex = self._walk(text)
            if None in (states, text):
                raise Exception('Parsing Error')
            priority = 30000
            token_type = None
            for state in states.state:
                if state.final and state.tag[0] <= priority:
                    priority, token_type = state.tag
            yield lex, token_type
            text = text[len(lex):]

        yield '$', self.eof

    def __call__(self, text):
        return [Token(lex, ttype) for lex, ttype in self._tokenize(text)]
