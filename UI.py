import os

import streamlit as st
from contextlib import redirect_stdout
from cmp.evaluation import evaluate_reverse_parse
from format_visitor import FormatVisitor
from interpreter import Interpreter
from semantics import TypeCollector, TypeBuilder, TypeInferencer, TypeChecker, TypesUpdater
from tools.serializers import Serializer
from semantics.utils import Context, Scope

path = os.getcwd() + '/tools'
tokenizer = Serializer.load(path + '/lexer')
parser = Serializer.load(path + '/parser')
example_code = '''class Main inherits IO {
    main(): SELF_TYPE {
        out_string("Hello World")
    };
};
'''

if __name__ == '__main__':
    st.title('COOL Semantics Checker')
    st.sidebar.title('Options')
    inference = st.sidebar.checkbox('Types inference (AUTO_TYPE)')
    st.sidebar.text('Output')
    show_tokens = st.sidebar.checkbox('Tokens')
    show_parsing = st.sidebar.checkbox('Parsing')
    show_ast = st.sidebar.checkbox('Abstract Syntax Tree')
    show_context = st.sidebar.checkbox('Context')

    input_program = st.text_area('COOL Program', value=example_code, height=400)
    start = st.button('Start')
    if start:
        tokens = list(tokenizer(input_program))

        if show_tokens:
            st.markdown('### Tokens')
            st.write([str(token) + '\n' for token in tokens])

        parse, operations = parser(tokens, get_shift_reduce=True)

        if show_parsing:
            st.markdown('### Parsing')
            st.write([str(prod) + '\n' for prod in reversed(parse)])

        ast = evaluate_reverse_parse(parse, operations, tokens)
        formatter = FormatVisitor()

        if ast is not None:
            errors = []
            context = Context()
            scope = Scope()
            collector = TypeCollector(context, errors)
            builder = TypeBuilder(context, errors)

            if inference:
                # This part is for type inference
                ###################################################
                collector.visit(ast)
                builder.visit(ast)
                inferencer = TypeInferencer(context, scope, errors)

                st.markdown('## Before Types Inference')
                if show_ast:
                    st.markdown('### Abstract Syntax Tree')
                    st.text(formatter.visit(ast, 1))
                if show_context:
                    st.markdown('### Context')
                    st.text(context)

                inferencer.visit(ast, scope)
                updater = TypesUpdater(inferencer.context,
                                       inferencer.scope,
                                       inferencer.functions,
                                       inferencer.attributes,
                                       inferencer.substitutions,
                                       inferencer.errors)
                updater.visit(ast, inferencer.scope, 0)
                ###################################################

            # Normal pipeline
            collector.context = Context()
            collector.visit(ast)
            builder.context = collector.context
            builder.visit(ast)

            if inference:
                st.markdown('## After Types Inference')

            if show_ast:
                st.markdown('### Abstract Syntax Tree')
                st.text(formatter.visit(ast, 1))
            if show_context:
                st.markdown('### Context')
                st.text(builder.context)

            type_checker = TypeChecker(builder.context, errors)
            type_checker.visit(ast)
            print(builder.context)
            if errors:
                st.markdown('# Errors')
                st.write(errors)
            # else:
            #     interpreter = Interpreter(builder.context)
            #     interpreter.visit(ast, Scope())
