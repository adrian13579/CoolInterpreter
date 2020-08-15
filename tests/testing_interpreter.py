from cmp.evaluation import evaluate_reverse_parse
from interpreter import Interpreter
from serializers import TokenizerHandler, ParserHandler
import os
from semantics import TypeChecker, TypeBuilder, TypeCollector, TypeInferencer, Context, Scope

path = "/mnt/69F79531507E7A36/CS/This year's stuff/Compilacion/Proyectos/CoolInterpreter/tools"
tokenizer = TokenizerHandler.load(path + '/lexer')
parser = ParserHandler.load(path + '/parser')

for i, file in enumerate(os.listdir('runtime_tests')):
    txt = open('runtime_tests/' + file)
    code = txt.read()

    if i == 3:
        print('Test {} started:'.format(i))
        tokens = list(tokenizer(code))
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
            print(context.get_type('Main').get_method('main').expression)
