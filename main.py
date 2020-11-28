import logging
import os
from rich.console import Console
from cmp.evaluation import evaluate_reverse_parse
from format_visitor import FormatVisitor
from interpreter import Interpreter
from semantics import TypeCollector, TypeBuilder, TypeInferencer, TypeChecker, TypesUpdater
from tools.serializers import Serializer
from semantics.utils import Context, Scope

console = Console()

path = os.getcwd() + '/tools'
tokenizer = Serializer.load(path + '/lexer')
parser = Serializer.load(path + '/parser')


def get_ast(args):
    file = open(args.file)
    code = file.read()
    if args.lexing:
        console.log('LEXING')
    tokens = list(tokenizer(code))
    if args.lexing:
        console.log('Tokens')
        console.print('\n'.join(str(token) for token in tokens), style='blue')
    if args.parsing:
        console.log('PARSING')
    parse, operations = parser(tokens, get_shift_reduce=True)
    if args.parsing:
        console.print('\n'.join(str(operation) for operation in parse), style='bold cyan')
    ast = evaluate_reverse_parse(parse, operations, tokens)
    if args.ast:
        console.print('Abstract Syntax Tree\n' + FormatVisitor().visit(ast, 1),style='bold green')
    return ast


def normal_pipeline(args):
    ast = get_ast(args)
    if ast is not None:
        errors = []
        context = Context()

        collector = TypeCollector(context, errors)
        collector.visit(ast)
        builder = TypeBuilder(context, errors)
        builder.context = collector.context
        builder.visit(ast)
        context.types.pop('AUTO_TYPE')
        type_checker = TypeChecker(builder.context, errors)
        type_checker.visit(ast)
        if errors:
            for error in errors:
                console.print(error, style='bold red')
        else:
            interpreter = Interpreter(builder.context)
            console.log('OUTPUT:')
            interpreter.visit(ast, Scope())


def full_pipeline(args):
    ast = get_ast(args)

    if ast is not None:
        errors = []
        context = Context()
        scope = Scope()

        # This part is for type inference
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
        if args.ast:
            console.print('Abstract Syntax Tree after types inference\n' + FormatVisitor().visit(ast, 1),
                          style='bold green')
        # Normal pipeline
        collector.context = Context()
        collector.visit(ast)
        builder.context = collector.context
        builder.visit(ast)
        type_checker = TypeChecker(builder.context, errors)
        type_checker.visit(ast)
        if errors:
            console.log('ERROR')
            for error in errors:
                console.print(error, style='bold red')
        else:
            interpreter = Interpreter(builder.context)
            console.log('OUTPUT:')
            interpreter.visit(ast, Scope())


if __name__ == '__main__':
    import argparse

    args_parser = argparse.ArgumentParser(description='Simple COOL Interpreter with Type Inference')
    args_parser.add_argument(
        '--file',
        type=str,
        help='COOL program to be executed')
    args_parser.add_argument(
        '--ast',
        type=bool,
        default=False
    )
    args_parser.add_argument(
        '--parsing',
        type=bool,
        default=False
    )
    args_parser.add_argument(
        '--lexing',
        type=bool,
        default=False
    )
    args_parser.add_argument(
        '--inference',
        type=bool,
        default=True,
        help='Support for type inference through keyword AUTO_TYPE'
    )
    arguments = args_parser.parse_args()

    if not arguments.inference:
        normal_pipeline(arguments)
    else:
        full_pipeline(arguments)
