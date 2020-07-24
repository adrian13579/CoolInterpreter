from cmp.evaluation import evaluate_reverse_parse
from serializers import TokenizerHandler, ParserHandler
from semantics.types_builder import TypeBuilder
from semantics.types_collector import TypeCollector

code = '''
class Foo inherits Bazz {
     a : Razz <- case self of
		      n : Razz => (new Bar);
		      n : Foo => (new Razz);
		      n : Bar => n;
   	         esac;

     b : Int <- a.doh() + g.doh() + doh() + printh();

     doh() : Int { (let i : Int <- h in { h <- h + 2; i; } ) };

};

class Bar inherits Razz {

     c : Int <- doh();

     d : Object <- printh();
};


class Razz inherits Foo {

     e : Bar <- case self of
		  n : Razz => (new Bar);
		  n : Bar => n;
		esac;

     f : Int <- a@Bazz.doh() + g.doh() + e.doh() + doh() + printh();

};

class Bazz inherits IO {

     h : Int <- 1;

     g : Foo  <- case self of
		     	n : Bazz => (new Foo);
		     	n : Razz => (new Bar);
			n : Foo  => (new Razz);
			n : Bar => n;
		  esac;

     i : Object <- printh();

     printh() : Int { { out_int(h); 0; } };

     doh() : Int { (let i: Int <- h in { h <- h + 1; i; } ) };
};

class Main   {
 a : Bazz <- new Bazz;
  b : Foo <- new Foo;
  c : Razz <- new Razz;
  d : Bar <- new Bar;

  main(): String { "do nothing" };

};
'''

path = "/mnt/69F79531507E7A36/CS/This year's stuff/Compilacion/Proyectos/CoolInterpreter/tools"
tokenizer = TokenizerHandler.load(path + '/lexer')
tokens = list(tokenizer(code))
print(tokens)
parser = ParserHandler.load(path + '/parser')

parse, operations = parser(tokens, get_shift_reduce=True)
for i in parse:
    print(i)
ast = evaluate_reverse_parse(parse, operations, tokens)

errors = []
type_collector = TypeCollector(errors)
type_collector.visit(ast)
types_builder = TypeBuilder(type_collector.context, errors)
types_builder.visit(ast)

# types_checker = TypeChecker(types_builder.context, types_builder.errors)
# types_checker.visit(ast)
print(type_collector.context)
print(types_builder.context)
print(errors)
