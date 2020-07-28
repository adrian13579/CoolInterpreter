from cmp.evaluation import evaluate_reverse_parse
from serializers import TokenizerHandler, ParserHandler
import os
from semantics import TypeChecker, TypeBuilder, TypeCollector, TypeInferencer, Context, Scope

path = "/mnt/69F79531507E7A36/CS/This year's stuff/Compilacion/Proyectos/CoolInterpreter/tools"
tokenizer = TokenizerHandler.load(path + '/lexer')
parser = ParserHandler.load(path + '/parser')

for i, file in enumerate(os.listdir('semantics_tests')):
    txt = open('semantics_tests/' + file)
    code = txt.read()

    if i == 5:
        print('Test {} started:'.format(i))
        tokens = list(tokenizer(code))
        print('Tokens:')
        print(tokens, '\n')
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
            TypeInferencer(context, scope, errors).visit(ast, scope)
