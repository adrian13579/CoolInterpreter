from cmp.evaluation import evaluate_reverse_parse
from interpreter import Interpreter
from tools.serializers import TokenizerHandler, ParserHandler
import os
from semantics import TypeBuilder, TypeCollector, Context, Scope

path = os.getcwd().replace('tests', '') + 'tools'
tokenizer = TokenizerHandler.load(path + '/lexer')
parser = ParserHandler.load(path + '/parser')

for i, file in enumerate(os.listdir('runtime_tests')):
    txt = open('runtime_tests/' + file)
    code = txt.read()

    if i == 7:
        print('Test {} started:'.format(i))
        tokens = list(tokenizer(text5))
        print('Tokens:')
        for token in tokens: print(token)
        parse, operations = parser(tokens, get_shift_reduce=True)
        print('Parsing:')
        for j in parse: print(j)
        ast = evaluate_reverse_parse(parse, operations, tokens)
        print(ast)

        if ast is not None:
            errors = []
            context = Context()
            scope = Scope()

            TypeCollector(context, errors).visit(ast)
            TypeBuilder(context, errors).visit(ast)
            print(context)
            Interpreter(context).visit(ast, Scope())
