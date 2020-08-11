from cmp.evaluation import evaluate_reverse_parse
from semantics.types_updater import TypesUpdater
from serializers import TokenizerHandler, ParserHandler
import os
from semantics import TypeChecker, TypeBuilder, TypeCollector, TypeInferencer, Context, Scope

path = "/mnt/69F79531507E7A36/CS/This year's stuff/Compilacion/Proyectos/CoolInterpreter/tools"
tokenizer = TokenizerHandler.load(path + '/lexer')
parser = ParserHandler.load(path + '/parser')

for i, file in enumerate(os.listdir('semantics_tests')):
    txt = open('semantics_tests/' + file)
    code = txt.read()

    if i == 4:
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

            collector = TypeCollector(context, errors)
            collector.visit(ast)
            builder = TypeBuilder(context, errors)
            builder.visit(ast)
            inferencer = TypeInferencer(context, scope, errors)
            inferencer.visit(ast, scope)
            updater = TypesUpdater(inferencer.context,
                                   inferencer.scope,
                                   inferencer.functions,
                                   inferencer.attributes,
                                   inferencer.substitutions,
                                   inferencer.errors)
            print(context)
            updater.visit(ast, inferencer.scope, 0)

            collector.context = Context()
            collector.visit(ast)
            builder.context = collector.context
            builder.visit(ast)
            print(builder.context)
            print('Done')
