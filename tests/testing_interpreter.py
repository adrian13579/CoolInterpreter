import os

from cmp.evaluation import evaluate_reverse_parse
from interpreter import Interpreter
from semantics import TypeBuilder, TypeCollector, Context, Scope
from tools.serializers import Serializer as sr

path = os.getcwd().replace('tests', '') + 'tools'
tokenizer = sr.load(path + '/lexer')
parser = sr.load(path + '/parser')

for i, file in enumerate(os.listdir('runtime_tests')):
    txt = open('runtime_tests/' + file)
    code = txt.read()

    if i == 6:
        print('Test {} started:'.format(i))
        tokens = list(tokenizer(code))
        print('Tokens:')
        for token in tokens:
            print(token.lex)
        parse, operations = parser(tokens, get_shift_reduce=True)
        print('Parsing:')
        for j in parse:
            print(j)
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
