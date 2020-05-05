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

    def __call__(self, w):
        stack = [0]
        cursor = 0
        output = []

        while True:
            state = stack[-1]
            lookahead = w[cursor]
            if self.verbose: print(stack, w[cursor:])

            # Your code here!!! (Detect error)
            try:
                action, tag = self.action[state, lookahead][0]
                # Your code here!!! (Shift case)
                if action == ShiftReduceParser.SHIFT:
                    stack.append(tag)
                    cursor += 1
                # Your code here!!! (Reduce case)
                elif action == ShiftReduceParser.REDUCE:
                    for _ in range(len(tag.Right)): stack.pop()
                    stack.append(self.goto[stack[-1], tag.Left][0])
                    output.append(tag)
                # Your code here!!! (OK case)
                elif action == ShiftReduceParser.OK:
                    return output
                # Your code here!!! (Invalid case)
                else:
                    assert False, 'Must be something wrong!'
            except KeyError:
                raise Exception('Aborting parsing, item is not viable.')

