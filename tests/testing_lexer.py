from tools.serializers import TokenizerHandler
import os

path = os.getcwd().replace('tests', '') + 'tools'
tokenizer = TokenizerHandler.load(path + '/lexer')
text = '''--efre3132fdvfv_2fr2f'''
text2 = '''"\n"'''
text3 = '''classx'''
text4 = '''
(* The Game of Life 
   Tendo Kayiira, Summer '95
   With code taken from /private/cool/class/examples/cells.cl

 This introduction was taken off the internet. It gives a brief 
 description of the Game Of Life. It also gives the rules by which 
 this particular game follows.

	Introduction

   John Conway's Game of Life is a mathematical amusement, but it 
   is also much more: an insight into how a system of simple 
   cellualar automata can create complex, odd, and often aesthetically 
   pleasing patterns. It is played on a cartesian grid of cells
   which are either 'on' or 'off' The game gets it's name from the 
   similarity between the behaviour of these cells and the behaviour 
   of living organisms.

 The Rules

  The playfield is a cartesian grid of arbitrary size. Each cell in 
  this grid can be in an 'on' state or an 'off' state. On each 'turn' 
  (called a generation,) the state of each cell changes simultaneously 
  depending on it's state and the state of all cells adjacent to it.

   For 'on' cells, 
      If the cell has 0 or 1 neighbours which are 'on', the cell turns 
        'off'. ('dies of loneliness') 
      If the cell has 2 or 3 neighbours which are 'on', the cell stays 
        'on'. (nothing happens to that cell) 
      If the cell has 4, 5, 6, 7, 8, or 9 neighbours which are 'on', 
        the cell turns 'off'. ('dies of overcrowding') 

   For 'off' cells, 
      If the cell has 0, 1, 2, 4, 5, 6, 7, 8, or 9 neighbours which 
        are 'on', the cell stays 'off'. (nothing happens to that cell) 
      If the cell has 3 neighbours which are 'on', the cell turns 
        'on'. (3 neighbouring 'alive' cells 'give birth' to a fourth.) 

   Repeat for as many generations as desired. 

 *)
 

class Board inherits IO { 
 
 rows : Int;
 columns : Int;
 board_size : Int;

 size_of_board(initial : String) : Int {
   initial.length()
 };

 board_init(start : String) : SELF_TYPE {
   (let size :Int  <- size_of_board(start) in
    {
	if size = 15 then
	 {
	  rows <- 3;
	  columns <- 5;
	  board_size <- size;
	 }
	else if size = 16 then
	  {
	  rows <- 4;
	  columns <- 4;
	  board_size <- size;
	 }
	else if size = 20 then
	 {
	  rows <- 4;
	  columns <- 5;
	  board_size <- size;
	 }
	else if size = 21 then
	 {
	  rows <- 3;
	  columns <- 7;
	  board_size <- size;
	 }
	else if size = 25 then
	 {
	  rows <- 5;
	  columns <- 5;
	  board_size <- size;
	 }
	else if size = 28 then
	 {
	  rows <- 7;
	  columns <- 4;
	  board_size <- size;
	 }
	else 	-- If none of the above fit, then just give 
	 {  -- the configuration of the most common board
	  rows <- 5;
	  columns <- 5;
	  board_size <- size;
	 }
	fi fi fi fi fi fi;
	self;
    }
   )
 };

};



class CellularAutomaton inherits Board {
    population_map : String;
   
    init(map : String) : SELF_TYPE {
        {
            population_map <- map;
	    board_init(map);
            self;
        }
    };



   
    print() : SELF_TYPE {
        
	(let i : Int <- 0 in
	(let num : Int <- board_size in
	{
 	out_string("\n");
	 while i < num loop
           {
	    out_string(population_map.substr(i,columns));
	    out_string("\n"); 
	    i <- i + columns;
	   }
	 pool;
 	out_string("\n");
	self;
	}
	) ) 
    };
   
    num_cells() : Int {
        population_map.length()
    };
   
    cell(position : Int) : String {
	if board_size - 1 < position then
		" "
	else 
        	population_map.substr(position, 1)
	fi
    };
   
 north(position : Int): String {
	if (position - columns) < 0 then
	      " "	                       
	else
	   cell(position - columns)
	fi
 };

 south(position : Int): String {
	if board_size < (position + columns) then
	      " "                     
	else
	   cell(position + columns)
	fi
 };

 east(position : Int): String {
	if (((position + 1) /columns ) * columns) = (position + 1) then
	      " "                
	else
	   cell(position + 1)
	fi 
 };

 west(position : Int): String {
	if position = 0 then
	      " "
	else 
	   if ((position / columns) * columns) = position then
	      " "
	   else
	      cell(position - 1)
	fi fi
 };

 northwest(position : Int): String {
	if (position - columns) < 0 then
	      " "	                       
	else  if ((position / columns) * columns) = position then
	      " "
	      else
		north(position - 1)
	fi fi
 };

 northeast(position : Int): String {
	if (position - columns) < 0 then
	      " "	
	else if (((position + 1) /columns ) * columns) = (position + 1) then
	      " "     
	     else
	       north(position + 1)
	fi fi
 };

 southeast(position : Int): String {
	if board_size < (position + columns) then
	      " "                     
	else if (((position + 1) /columns ) * columns) = (position + 1) then
	       " "                
	     else
	       south(position + 1)
	fi fi
 };

 southwest(position : Int): String {
	if board_size < (position + columns) then
	      " "                     
	else  if ((position / columns) * columns) = position then
	      " "
	      else
	       south(position - 1)
	fi fi
 };

 neighbors(position: Int): Int { 
 	{
	     if north(position) = "X" then 1 else 0 fi
	     + if south(position) = "X" then 1 else 0 fi
 	     + if east(position) = "X" then 1 else 0 fi
 	     + if west(position) = "X" then 1 else 0 fi
	     + if northeast(position) = "X" then 1 else 0 fi
	     + if northwest(position) = "X" then 1 else 0 fi
 	     + if southeast(position) = "X" then 1 else 0 fi
	     + if southwest(position) = "X" then 1 else 0 fi;
	 }
 };

 
(* A cell will live if 2 or 3 of it's neighbors are alive. It dies 
   otherwise. A cell is born if only 3 of it's neighbors are alive. *)
    
    cell_at_next_evolution(position : Int) : String {

	if neighbors(position) = 3 then
		"X"
	else
	   if neighbors(position) = 2 then
		if cell(position) = "X" then
			"X"
		else
			"-"
	        fi
	   else
		"-"
	fi fi
    };
  

    evolve() : SELF_TYPE {
        (let position : Int <- 0 in
        (let num : Int <- num_cells() in
        (let temp : String in
            {
                while position < num loop
                    {
                        temp <- temp.concat(cell_at_next_evolution(position));
                        position <- position + 1;
                    }
                pool;
                population_map <- temp;
                self;
            }
        ) ) )
    };

(* This is where the background pattern is detremined by the user. More 
   patterns can be added as long as whoever adds keeps the board either
   3x5, 4x5, 5x5, 3x7, 7x4, 4x4 with the row first then column. *) 
 option(): String {
 {
  (let num : Int in
   {
   out_string("\nPlease chose a number:\n");
   out_string("\t1: A cross\n"); 
   out_string("\t2: A slash from the upper left to lower right\n");
   out_string("\t3: A slash from the upper right to lower left\n"); 
   out_string("\t4: An X\n"); 
   out_string("\t5: A greater than sign \n"); 
   out_string("\t6: A less than sign\n"); 
   out_string("\t7: Two greater than signs\n"); 
   out_string("\t8: Two less than signs\n"); 
   out_string("\t9: A 'V'\n"); 
   out_string("\t10: An inverse 'V'\n"); 
   out_string("\t11: Numbers 9 and 10 combined\n"); 
   out_string("\t12: A full grid\n"); 
   out_string("\t13: A 'T'\n");
   out_string("\t14: A plus '+'\n");
   out_string("\t15: A 'W'\n");
   out_string("\t16: An 'M'\n");
   out_string("\t17: An 'E'\n");
   out_string("\t18: A '3'\n");
   out_string("\t19: An 'O'\n");
   out_string("\t20: An '8'\n");
   out_string("\t21: An 'S'\n");
   out_string("Your choice => ");
   num <- in_int();
   out_string("\n");
   if num = 1 then
    	" XX  XXXX XXXX  XX  "
   else if num = 2 then
    	"    X   X   X   X   X    "
   else if num = 3 then
    	"X     X     X     X     X"
   else if num = 4 then
	"X   X X X   X   X X X   X"
   else if num = 5 then
	"X     X     X   X   X    "
   else if num = 6 then
	"    X   X   X     X     X"
   else if num = 7 then
	"X  X  X  XX  X      "
   else if num = 8 then
	" X  XX  X  X  X     "
   else if num = 9 then
	"X   X X X   X  "
   else if num = 10 then
	"  X   X X X   X"
   else if num = 11 then
	"X X X X X X X X"
   else if num = 12 then
	"XXXXXXXXXXXXXXXXXXXXXXXXX"
   else if num = 13 then
    	"XXXXX  X    X    X    X  "
   else if num = 14 then
    	"  X    X  XXXXX  X    X  "
   else if num = 15 then
    	"X     X X X X   X X  "
   else if num = 16 then
    	"  X X   X X X X     X"
   else if num = 17 then
	"XXXXX   X   XXXXX   X   XXXX"
   else if num = 18 then
	"XXX    X   X  X    X   XXXX "
   else if num = 19 then
	" XX X  XX  X XX "
   else if num = 20 then
	" XX X  XX  X XX X  XX  X XX "
   else if num = 21 then
	" XXXX   X    XX    X   XXXX "
   else
	"                         "
  fi fi fi fi fi fi fi fi fi fi fi fi fi fi fi fi fi fi fi fi fi;
    }
   );
 }
 };




 prompt() : Bool { 
 {
  (let ans : String in
   {
   out_string("Would you like to continue with the next generation? \n");
   out_string("Please use lowercase y or n for your answer [y]: ");
   ans <- in_string();
   out_string("\n");
   if ans = "n" then 
	false
   else
	true
   fi;
   }
  );
 }
 };


 prompt2() : Bool { 
  (let ans : String in
   {
   out_string("\n\n");
   out_string("Would you like to choose a background pattern? \n");
   out_string("Please use lowercase y or n for your answer [n]: ");
   ans <- in_string();
   if ans = "y" then 
	true
   else
	false
   fi;
   }
  )
 };


};

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
text5 = '''
class VarList inherits IO {
  isNil() : Bool { true };
  head()  : Variable { { abort(); new Variable; } };
  tail()  : VarList { { abort(); new VarList; } };
  add(x : Variable) : VarList { (new VarListNE).init(x, self) };
  print() : SELF_TYPE { out_string("\n") };
};

class VarListNE inherits VarList {
  x : Variable;
  rest : VarList;
  isNil() : Bool { false };
  head()  : Variable { x };
  tail()  : VarList { rest };
  init(y : Variable, r : VarList) : VarListNE { { x <- y; rest <- r; self; } };
  print() : SELF_TYPE { { x.print_self(); out_string(" ");
	                  rest.print(); self; } };
};

class LambdaList {
  isNil() : Bool { true };
  headE() : VarList { { abort(); new VarList; } };
  headC() : Lambda { { abort(); new Lambda; } };
  headN() : Int { { abort(); 0; } };
  tail()  : LambdaList { { abort(); new LambdaList; } };
  add(e : VarList, x : Lambda, n : Int) : LambdaList {
    (new LambdaListNE).init(e, x, n, self)
  };
};

class LambdaListNE inherits LambdaList {
  lam : Lambda;
  num : Int;
  env : VarList;
  rest : LambdaList;
  isNil() : Bool { false };
  headE() : VarList { env };
  headC() : Lambda { lam };
  headN() : Int { num };
  tail()  : LambdaList { rest };
  init(e : VarList, l : Lambda, n : Int, r : LambdaList) : LambdaListNE {
    {
      env <- e;
      lam <- l;
      num <- n;
      rest <- r;
      self;
    }
  };
};

class LambdaListRef {
  nextNum : Int <- 0;
  l : LambdaList;
  isNil() : Bool { l.isNil() };
  headE() : VarList { l.headE() };
  headC() : Lambda { l.headC() };
  headN() : Int { l.headN() };
  reset() : SELF_TYPE {
    {
      nextNum <- 0;
      l <- new LambdaList;
      self;
    }
  };
  add(env : VarList, c : Lambda) : Int {
    {
      l <- l.add(env, c, nextNum);
      nextNum <- nextNum + 1;
      nextNum - 1;
    }
  };
  removeHead() : SELF_TYPE {
    {
      l <- l.tail();
      self;
    }
  };
};


class Expr inherits IO {

  print_self() : SELF_TYPE {
    {
      out_string("\nError: Expr is pure virtual; can't print self\n");
      abort();
      self;
    }
  };

  beta() : Expr {
    {
      out_string("\nError: Expr is pure virtual; can't beta-reduce\n");
      abort();
      self;
    }
  };

  substitute(x : Variable, e : Expr) : Expr {
    {
      out_string("\nError: Expr is pure virtual; can't substitute\n");
      abort();
      self;
    }
  };

  gen_code(env : VarList, closures : LambdaListRef) : SELF_TYPE {
    {
      out_string("\nError: Expr is pure virtual; can't gen_code\n");
      abort();
      self;
    }
  };
};

class Variable inherits Expr {
  name : String;

  init(n:String) : Variable {
    {
      name <- n;
      self;
    }
  };

  print_self() : SELF_TYPE {
    out_string(name)
  };

  beta() : Expr { self };

  substitute(x : Variable, e : Expr) : Expr {
    if x = self then e else self fi
  };

  gen_code(env : VarList, closures : LambdaListRef) : SELF_TYPE {
    let cur_env : VarList <- env in
      { while (if cur_env.isNil() then
	          false
	       else
	         not (cur_env.head() = self)
	       fi) loop
	  { out_string("get_parent().");
	    cur_env <- cur_env.tail();
          }
        pool;
        if cur_env.isNil() then
          { out_string("Error:  free occurrence of ");
            print_self();
            out_string("\n");
            abort();
            self;
          }
        else
          out_string("get_x()")
        fi;
      }
  };
};

class Lambda inherits Expr {
  arg : Variable;
  body : Expr;

  init(a:Variable, b:Expr) : Lambda {
    {
      arg <- a;
      body <- b;
      self;
    }
  };

  print_self() : SELF_TYPE {
    {
      out_string("\\");
      arg.print_self();
      out_string(".");
      body.print_self();
      self;
    }
  };

  beta() : Expr { self };

  apply(actual : Expr) : Expr {
    body.substitute(arg, actual)
  };

  substitute(x : Variable, e : Expr) : Expr {
    if x = arg then
      self
    else
      let new_body : Expr <- body.substitute(x, e),
	  new_lam : Lambda <- new Lambda in
	new_lam.init(arg, new_body)
    fi
  };

  gen_code(env : VarList, closures : LambdaListRef) : SELF_TYPE {
    {
      out_string("((new Closure");
      out_int(closures.add(env, self));
      out_string(").init(");
      if env.isNil() then
        out_string("new Closure))")
      else
	out_string("self))") fi;
      self;
    }
  };

  gen_closure_code(n : Int, env : VarList,
		   closures : LambdaListRef) : SELF_TYPE {
    {
      out_string("class Closure");
      out_int(n);
      out_string(" inherits Closure {\n");
      out_string("  apply(y : EvalObject) : EvalObject {\n");
      out_string("    { out_string(\"Applying closure ");
      out_int(n);
      out_string("\\n\");\n");
      out_string("      x <- y;\n");
      body.gen_code(env.add(arg), closures);
      out_string(";}};\n");
      out_string("};\n");
    }
  };
};


class App inherits Expr {
  fun : Expr;
  arg : Expr;

  init(f : Expr, a : Expr) : App {
    {
      fun <- f;
      arg <- a;
      self;
    }
  };

  print_self() : SELF_TYPE {
    {
      out_string("((");
      fun.print_self();
      out_string(")@(");
      arg.print_self();
      out_string("))");
      self;
    }
  };

  beta() : Expr {
    case fun of
      l : Lambda => l.apply(arg);     -- Lazy evaluation
      e : Expr =>
	let new_fun : Expr <- fun.beta(),
	    new_app : App <- new App in
	  new_app.init(new_fun, arg);
    esac
  };

  substitute(x : Variable, e : Expr) : Expr {
    let new_fun : Expr <- fun.substitute(x, e),
        new_arg : Expr <- arg.substitute(x, e),
        new_app : App <- new App in
      new_app.init(new_fun, new_arg)
  };

  gen_code(env : VarList, closures : LambdaListRef) : SELF_TYPE {
    {
      out_string("(let x : EvalObject <- ");
      fun.gen_code(env, closures);
      out_string(",\n");
      out_string("     y : EvalObject <- ");
      arg.gen_code(env, closures);
      out_string(" in\n");
      out_string("  case x of\n");
      out_string("    c : Closure => c.apply(y);\n");
      out_string("    o : Object => { abort(); new EvalObject; };\n");
      out_string("  esac)");
    }
  };
};



class Term inherits IO {

  var(x : String) : Variable {
    let v : Variable <- new Variable in
      v.init(x)
  };

  lam(x : Variable, e : Expr) : Lambda {
    let l : Lambda <- new Lambda in
      l.init(x, e)
  };

  app(e1 : Expr, e2 : Expr) : App {
    let a : App <- new App in
      a.init(e1, e2)
  };

  (*
   * Some useful terms
   *)
  i() : Expr {
    let x : Variable <- var("x") in
      lam(x,x)
  };

  k() : Expr {
    let x : Variable <- var("x"),
        y : Variable <- var("y") in
    lam(x,lam(y,x))
  };

  s() : Expr {
    let x : Variable <- var("x"),
        y : Variable <- var("y"),
        z : Variable <- var("z") in
      lam(x,lam(y,lam(z,app(app(x,z),app(y,z)))))
  };

};



class Main inherits Term {
  beta_reduce(e : Expr) : Expr {
    {
      out_string("beta-reduce: ");
      e.print_self();
      let done : Bool <- false,
          new_expr : Expr in
        {
	  while (not done) loop
	    {
	      new_expr <- e.beta();
	      if (new_expr = e) then
		done <- true
	      else
		{
		  e <- new_expr;
		  out_string(" =>\n");
		  e.print_self();
		}
	      fi;
	    }
          pool;
	  out_string("\n");
          e;
	};
    }
  };

  eval_class() : SELF_TYPE {
    {
      out_string("class EvalObject inherits IO {\n");
      out_string("  eval() : EvalObject { { abort(); self; } };\n");
      out_string("};\n");
    }
  };

  closure_class() : SELF_TYPE {
    {
      out_string("class Closure inherits EvalObject {\n");
      out_string("  parent : Closure;\n");
      out_string("  x : EvalObject;\n");
      out_string("  get_parent() : Closure { parent };\n");
      out_string("  get_x() : EvalObject { x };\n");
      out_string("  init(p : Closure) : Closure {{ parent <- p; self; }};\n");
      out_string("  apply(y : EvalObject) : EvalObject { { abort(); self; } };\n");
      out_string("};\n");
    }
  };

  gen_code(e : Expr) : SELF_TYPE {
    let cl : LambdaListRef <- (new LambdaListRef).reset() in
      {
	out_string("Generating code for ");
	e.print_self();
	out_string("\n------------------cut here------------------\n");
	out_string("(*Generated by lam.cl (Jeff Foster, March 2000)*)\n");
	eval_class();
	closure_class();
	out_string("class Main {\n");
	out_string("  main() : EvalObject {\n");
	e.gen_code(new VarList, cl);
	out_string("\n};\n};\n");
	while (not (cl.isNil())) loop
	  let e : VarList <- cl.headE(),
	      c : Lambda <- cl.headC(),
	      n : Int <- cl.headN() in
	    {
	      cl.removeHead();
	      c.gen_closure_code(n, e, cl);
	    }
	pool;
	out_string("\n------------------cut here------------------\n");
      }
  };

  main() : Int {
    {
      i().print_self();
      out_string("\n");
      k().print_self();
      out_string("\n");
      s().print_self();
      out_string("\n");
      beta_reduce(app(app(app(s(), k()), i()), i()));
      beta_reduce(app(app(k(),i()),i()));
      gen_code(app(i(), i()));
      gen_code(app(app(app(s(), k()), i()), i()));
      gen_code(app(app(app(app(app(app(app(app(i(), k()), s()), s()),
                                   k()), s()), i()), k()), i()));
      gen_code(app(app(i(), app(k(), s())), app(k(), app(s(), s()))));
      0;
    }
  };
};


 '''
for token in tokenizer(text5):
    print(token.lex, token.token_type, token.col, token.row)
