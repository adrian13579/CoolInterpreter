class ShiftReduceParser:
    SHIFT = 'SHIFT'
    REDUCE = 'REDUCE'
    OK = 'OK'

    def __init__(self, G, verbose=False):
        self.G = G
        self.verbose = verbose
        self.action = {}
        self.goto = {}
        self._build_parsing_table()

    def _build_parsing_table(self):
        raise NotImplementedError()

    def __call__(self, w, get_shift_reduce=False):
        stack = [0]
        cursor = 0
        output = []
        operations = []

        while True:
            state = stack[-1]
            lookahead = w[cursor]
            if self.verbose: print(stack, w[cursor:])
            try:
                action, tag = self.action[state, lookahead.token_type.Name][0]
                if action == ShiftReduceParser.SHIFT:
                    operations.append(self.SHIFT)
                    stack.append(tag)
                    cursor += 1
                elif action == ShiftReduceParser.REDUCE:
                    operations.append(self.REDUCE)
                    for _ in range(len(tag.Right)): stack.pop()
                    stack.append(self.goto[stack[-1], tag.Left.Name][0])
                    output.append(tag)
                elif action == ShiftReduceParser.OK:
                    return output if not get_shift_reduce else (output, operations)
                else:
                    assert False, 'Must be something wrong!'
            except KeyError:
                raise Exception(f'Aborting parsing: syntax error near token {lookahead.lex} line:{lookahead.row} col:{lookahead.col}')
