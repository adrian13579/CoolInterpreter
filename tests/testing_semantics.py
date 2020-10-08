from cmp.evaluation import evaluate_reverse_parse
from semantics.types_updater import TypesUpdater
from tools.serializers import Serializer as sr
import os
from semantics import TypeBuilder, TypeCollector, TypeInferencer, Context, Scope, TypeChecker

path = os.getcwd().replace('tests', '') + 'tools'
tokenizer = sr.load(path + '/lexer')
parser = sr.load(path + '/parser')

for i, file in enumerate(os.listdir('semantics_tests')):
    txt = open('semantics_tests/' + file)
    code = txt.read()

    if i == 8:
        print('Test {} started:'.format(i))
        tokens = list(tokenizer(code))
        print('Tokens:')
        print(tokens, '\n')
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
            type_checker = TypeChecker(builder.context, errors)
            type_checker.visit(ast)
            print(errors)
            print('Done')
