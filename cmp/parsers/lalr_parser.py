from cmp.automata import State, multiline_formatter
from cmp.parsers.lr1_parser import build_LR1_automaton
from cmp.pycompiler import Item
from cmp.parsers.shift_reduce_parser import ShiftReduceParser


def build_LALR1_automaton(G):
    automaton = build_LR1_automaton(G)

    stKernel = {}
    for node in automaton:
        kernel = frozenset([item.Center() for item in node.state])
        try:
            stKernel[kernel].append(node)
        except KeyError:
            stKernel[kernel] = [node]

    initial = frozenset([item.Center() for item in automaton.state])
    automaton = State(automaton.state, True)

    visited = {initial: automaton}
    pending = [initial]

    while pending:
        current = pending.pop()
        current_state = visited[current]
        lr1_state = stKernel[current][0]

        for symbol in G.terminals + G.nonTerminals:
            if symbol.Name in lr1_state.transitions:
                dest_core = frozenset([item.Center() for item in lr1_state.transitions[symbol.Name][0].state])

                try:
                    next_state = visited[dest_core]

                except KeyError:
                    union_core = {center: set() for center in dest_core}
                    for node in stKernel[dest_core]:
                        for item in node.state:
                            union_core[item.Center()].update(item.lookaheads)
                    union_core = frozenset(
                        [Item(center.production, center.pos, lookaheads=lookaheads) for center, lookaheads in
                         union_core.items()])
                    next_state = State(union_core, True)
                    visited[dest_core] = next_state
                    pending.append(dest_core)
                current_state.add_transition(symbol.Name, next_state)

    automaton.set_formatter(multiline_formatter)
    return automaton


class LALR1Parser(ShiftReduceParser):

    def _build_parsing_table(self):
        G = self.G.AugmentedGrammar(True)

        automaton = build_LALR1_automaton(G)
        for i, node in enumerate(automaton):
            if self.verbose: print(i, '\t', '\n\t '.join(str(x) for x in node.state), '\n')
            node.idx = i

        for node in automaton:
            idx = node.idx
            for item in node.state:
                # Your code here!!!
                # - Fill `self.Action` and `self.Goto` according to `item`)
                # - Feel free to use `self._register(...)`)

                nSymbol = item.NextSymbol
                pr = item.production
                if item.IsReduceItem:
                    if pr.Left == G.startSymbol:
                        self._register(self.action, (idx, G.EOF), (self.OK, None))
                    else:
                        for c in item.lookaheads:
                            # register(self.action, (state,c), (self.REDUCE,pr))
                            self._register(self.action, (idx, c), (self.REDUCE, pr))
                #                         continue

                elif nSymbol.IsTerminal:
                    try:
                        xNode = node[nSymbol.Name][0]
                        self._register(self.action, (idx, nSymbol), (self.SHIFT, xNode.idx))
                    except KeyError:
                        # el automata q construyo es correcto, asi q esto nunca deberia ocurrir, pero bueeeeno
                        pass
                elif nSymbol.IsNonTerminal:
                    try:
                        tNode = node[nSymbol.Name][0]
                        #                        self._register(self.action, (idx,nSymbol), (self.SHIFT,tNode.idx) )
                        self._register(self.goto, (idx, nSymbol), tNode.idx)
                    except KeyError:
                        # el automata q construyo es correcto, asi q esto nunca deberia ocurrir, pero bueeeeno
                        pass

                pass

    @staticmethod
    def _register(table, key, value):
        try:
            if value not in table[key]:
                table[key].append(value)
        except:
            table[key] = [value]


def conflict_string_lalr(action, goto, terminals):
    return _conflict_string_lalr([0], set(), action, goto, terminals, False)


def _conflict_string_lalr(stack, visited, action_table, goto_table, terminals, conflict_bool):
    state = stack[-1]

    for t in terminals:
        if (state, t) in visited:
            continue

        try:
            value = action_table[(state, t)]
        except KeyError:
            continue

        if len(value) > 1:
            conflict_bool = True

        action, tag = value[0]

        if action == 'OK':
            if conflict_bool:
                return []
            return None

        if action == 'SHIFT':
            visited.add((state, t))
            conflict = _conflict_string_lalr(stack + [tag], visited, action_table, goto_table, terminals, conflict_bool)
            if conflict is None:
                continue
            return [t] + conflict

        if action == 'REDUCE':
            temp_stack = stack[: len(stack) - len(tag.Right)]
            return _conflict_string_lalr(temp_stack + [goto_table[temp_stack[-1], tag.Left][0]], visited, action_table,
                                         goto_table, terminals, conflict_bool)

    return None
