from cmp.evaluation import evaluate_reverse_parse
from tools.serializers import Serializer as sr
import os

path = os.getcwd().replace('tests', '') + 'tools'
tokenizer = sr.load(path + '/lexer')
parser = sr.load(path + '/parser')
code = '''
class Main inherits CellularAutomaton {
    cells : CellularAutomaton;

    main() : SELF_TYPE {
        {
	 (let continue : Bool  in
	  (let choice : String  in
	   {
	   out_string("Welcome to the Game of Life.\n");
	   out_string("There are many initial states to choose from. \n");
	   while prompt2() loop
	    {
	     continue <- true;
	     choice <- option();
	     cells <- (new CellularAutomaton).init(choice);
	     cells.print();
             while continue loop
		if prompt() then
                    {
                        cells.evolve();
                        cells.print();
                    }
		else
		    continue <- false
	      fi
                pool;
            }
            pool;
	    self;
      }  ) ); }
    };
};


'''
code2 = '''

class CellularAutomaton inherits Board {
 
 neighbors(position: Int): Int { 
 	{
 	    {
	    ( if north(position) = "X" then 1 else 0 fi)
	     + (if southwest(position) = "X" then 1 else 0 fi);
	     ~ 12312;
	     };
	 }
 };


};


'''
tokens = list(tokenizer(code2))
print('Tokens:')
for token in tokens:
    print(token)
parse, operations = parser(tokens, get_shift_reduce=True)
print('Parsing:')
for j in parse:
    print(j)
ast = evaluate_reverse_parse(parse, operations, tokens)
print(ast)
