from cmp.pycompiler import Grammar

G = Grammar()
# Terminals
classx, inherits, selfx, let, assigment, ifx, thenx, elsex, fi, = G.Terminals(
    'class inherits self let <- if then else fi')
whilex, loop, pool, case, of, esac, case_assigment, new, isvoid, equal, = G.Terminals(
    'while loop pool case of esac => new isvoid =')
less, less_equal, plus, minus, star, div, semi, colon, comma = G.Terminals('< <= + - * / ; : ,')
dot, opar, cpar, ocur, ccur, inx, notx, idx, intx, string, true, false, at = G.Terminals(
    ', . ( ) { } in not id int string true false @')

# Nonterminals
program = G.NonTerminal('<program>', True)
class_list, def_class = G.NonTerminal('<class-list> <class>')
feature_list, def_func, def_attr = G.NonTerminal('<feature_list> <def-func> <def-attr>')
params_list, param = G.NonTerminal('<params-list> <param>')
expr_list, expr = G.NonTerminal('<expr-list> <expr>')
cmp, arith, term, factor, atom = G.NonTerminals('<cmp> <arith> <term> <factor> <atom>')
func_call, arg_list = G.NonTerminals('<func-call> <arg-list>')
let_list, let_single = G.NonTerminal('<let-list> <let-single>')
case_list, case_single = G.NonTerminal('<case-list> <case-single>')

program %= class_list,

class_list %= def_class + semi + class_list,
class_list %= def_class + semi,

def_class %= classx + idx + ocur + feature_list + ccur,
def_class %= classx + idx + inherits + idx + ocur + feature_list + ccur,

feature_list %= def_attr + semi + feature_list,
feature_list %= def_func + semi + feature_list,
feature_list %= G.Epsilon,

def_attr %= idx + colon + idx,
def_attr %= idx + colon + idx + assigment + expr,

def_func %= idx + opar + params_list + cpar + colon + idx + ocur + expr_list + ccur,

params_list %= param + comma + params_list,
params_list %= G.Epsilon,

param %= idx + colon + idx

expr_list %= expr + semi,
expr_list %= expr + semi + expr_list,

expr %= idx + assigment + expr,
expr %= expr + at + idx + dot + idx + opar + arg_list + cpar,
expr %= expr + dot + idx + opar + arg_list + cpar,
expr %= expr + opar + arg_list + cpar,
expr %= ifx + expr + thenx + expr + elsex + expr + fi,
expr %= whilex + expr + loop + expr + pool,
expr %= let_list + inx + expr,
expr %= ocur + expr_list + ccur,
expr %= case + expr + of + case_list + esac
expr %= new + idx,
expr %= intx,
expr %= idx,

arg_list %= expr,
arg_list %= expr + comma + arg_list,
arg_list %= G.Epsilon,

let_list %= let_single + let_list,
let_list %= let_single,

let_single %= let + idx + colon + idx,

case_list %= case_single + case_list,
case_list %= case_single,

case_single %= idx + colon + idx + case_assigment + expr + semi,
