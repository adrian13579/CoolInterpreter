import os

from cmp.evaluation import evaluate_reverse_parse
from interpreter import Interpreter
from semantics import TypeCollector, TypeBuilder, TypeInferencer
from semantics.types_updater import TypesUpdater
from serializers import TokenizerHandler, ParserHandler
from utils import Context, Scope

path = os.getcwd() + '/tools'
tokenizer = TokenizerHandler.load(path + '/lexer')
parser = ParserHandler.load(path + '/parser')


def run_pipeline(args):
    file = open(args.file)
    code = file.read()
    tokens = list(tokenizer(code))
    parse, operations = parser(tokens, get_shift_reduce=True)
    ast = evaluate_reverse_parse(parse, operations, tokens)

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
        updater.visit(ast, inferencer.scope, 0)

        collector.context = Context()
        collector.visit(ast)
        builder.context = collector.context
        builder.visit(ast)
        print(builder.context)
        if errors:
            print(errors)
        else:
            interpreter = Interpreter(builder.context)
            interpreter.visit(ast, Scope())


if __name__ == '__main__':
    import argparse

    args_parser = argparse.ArgumentParser(description='Basic Cool Interpreter with Type Inference')
    args_parser.add_argument('file', type=str, help='Cool program to be executed')
    arguments = args_parser.parse_args()

    run_pipeline(arguments)
