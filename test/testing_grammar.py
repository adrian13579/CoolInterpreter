from cmp.evaluation import evaluate_reverse_parse
from tools.utils import TokenizerHandler, ParserHandler

# code = ('\n'
#         '\n'
#         'class Foo inherits Bazz {\n'
#         '     a : Razz <- case self of\n'
#         '		      n : Razz => (new Bar);\n'
#         '		      n : Foo => (new Razz);\n'
#         '		      n : Bar => n;\n'
#         '   	         esac;\n'
#         '\n'
#         '     b : Int <- a.doh() + g.doh() + doh() + printh();\n'
#         '\n'
#         '     doh() : Int { (let i : Int <- h in { h <- h + 2; i; } ) };\n'
#         '\n'
#         '};\n'
#         '\n'
#         'class Bar inherits Razz {\n'
#         '\n'
#         '     c : Int <- doh();\n'
#         '\n'
#         '     d : Object <- printh();\n'
#         '};\n'
#         '\n'
#         '\n'
#         'class Razz inherits Foo {\n'
#         '\n'
#         '     e : Bar <- case self of\n'
#         '		  n : Razz => (new Bar);\n'
#         '		  n : Bar => n;\n'
#         '		esac;\n'
#         '\n'
#         '     f : Int <- aBazz.doh() + g.doh() + e.doh() + doh() + printh();\n'
#         '\n'
#         '};\n'
#         '\n'
#         'class Bazz inherits IO {\n'
#         '\n'
#         '     h : Int <- 1;\n'
#         '\n'
#         '     g : Foo  <- case self of\n'
#         '		     	n : Bazz => (new Foo);\n'
#         '		     	n : Razz => (new Bar);\n'
#         '			n : Foo  => (new Razz);\n'
#         '			n : Bar => n;\n'
#         '		  esac;\n'
#         '\n'
#         '     i : Object <- printh();\n'
#         '\n'
#         '     printh() : Int { { out_int(h); 0; } };\n'
#         '\n'
#         '     doh() : Int { (let i: Int <- h in { h <- h + 1; i; } ) };\n'
#         '};\n'
#         '\n'
#         'class Main {\n'
#         '  a : Bazz <- new Bazz;\n'
#         '  b : Foo <- new Foo;\n'
#         '  c : Razz <- new Razz;\n'
#         '  d : Bar <- new Bar;\n'
#         '\n'
#         '  main(): String { "do nothing" };\n'
#         '\n'
#         '};\n'
#         '\n')
code = '''

class A {

        main(): void {
                let x : T in x + let y : T in y 

        };
};
'''

tokenizer = TokenizerHandler.load()
tokens = list(tokenizer(code))
print(tokens)
parser = ParserHandler.load()

parse, operations = parser(tokens, get_shift_reduce=True)
for i in parse:
    print(i)
ast = evaluate_reverse_parse(parse, operations, tokens)
print(ast)
