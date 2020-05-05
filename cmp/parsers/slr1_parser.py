from cmp.automata import State
from cmp.pycompiler import Item
from cmp.first_follow import compute_firsts, compute_follows
from cmp.parsers.shift_reduce_parser import ShiftReduceParser


def build_LR0_automaton(G):
    assert len(G.startSymbol.productions) == 1, 'Grammar must be augmented'

    start_production = G.startSymbol.productions[0]
    start_item = Item(start_production, 0)

    automaton = State(start_item, True)

    pending = [start_item]
    visited = {start_item: automaton}

    while pending:
        current_item = pending.pop()
        if current_item.IsReduceItem:
            continue

        # Your code here!!! (Decide which transitions to add)
        new_item = current_item.NextItem()
        transition_symbol = current_item.NextSymbol.Name
        next_items = [(new_item, transition_symbol)]

        if current_item.NextSymbol in G.nonTerminals:
            for production in current_item.NextSymbol.productions:
                new_item = Item(production, 0)
                next_items.append((new_item, G.Epsilon))

        current_state = visited[current_item]
        # Your code here!!! (Add the decided transitions)
        for item, symbol in next_items:
            try:
                state = visited[item]
            except KeyError:
                state = State(item, True)
                visited[item] = state
                pending.append(item)

            if symbol == G.Epsilon:
                current_state.add_epsilon_transition(state)
            else:
                current_state.add_transition(symbol, state)

    return automaton


class SLR1Parser(ShiftReduceParser):

    def _build_parsing_table(self):
        G = self.G.AugmentedGrammar(True)
        firsts = compute_firsts(G)
        follows = compute_follows(G, firsts)

        automaton = build_LR0_automaton(G).to_deterministic()
        for i, node in enumerate(automaton):
            if self.verbose: print(i, node)
            node.idx = i

        for node in automaton:
            idx = node.idx
            for state in node.state:
                item = state.state
                # Your code here!!!
                # - Fill `self.Action` and `self.Goto` according to `item`)
                # - Feel free to use `self._register(...)`)
                if item.IsReduceItem:
                    prod = item.production
                    if prod.Left == G.startSymbol:
                        SLR1Parser._register(self.action, (idx, G.EOF), (ShiftReduceParser.OK, None))
                    else:
                        for symbol in follows[prod.Left]:
                            SLR1Parser._register(self.action, (idx, symbol), (ShiftReduceParser.REDUCE, prod))
                else:
                    next_symbol = item.NextSymbol
                    if next_symbol.IsTerminal:
                        SLR1Parser._register(self.action, (idx, next_symbol),
                                             (ShiftReduceParser.SHIFT, node[next_symbol.Name][0].idx))
                    else:
                        SLR1Parser._register(self.goto, (idx, next_symbol), node[next_symbol.Name][0].idx)

    @staticmethod
    def _register(table, key, value):
        try:
            if value not in table[key]:
                table[key].append(value)
        except:
            table[key] = [value]


def conflict_string_slr1(action, goto, terminals):
    return _conflict_string_slr1([0], set(), action, goto, terminals, False)


def _conflict_string_slr1(stack, visited, action_table, goto_table, terminals, conflict_bool):
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
            conflict = _conflict_string_slr1(stack + [tag], visited, action_table, goto_table, terminals, conflict_bool)
            if conflict is None:
                continue
            return [t] + conflict

        if action == 'REDUCE':
            temp_stack = stack[: len(stack)-len(tag.Right)]
            return _conflict_string_slr1(temp_stack + [goto_table[temp_stack[-1], tag.Left][0]], visited, action_table, goto_table, terminals, conflict_bool)
    return None
