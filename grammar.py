from cmp.pycompiler import Grammar
from ast import *

G = Grammar()
# Terminals
classx, inherits, selfx, let, assigment, ifx, thenx, elsex, fi, = G.Terminals(
    'class inherits self let <- if then else fi')
whilex, loop, pool, case, of, esac, case_assigment, new, isvoid, equal, = G.Terminals(
    'while loop pool case of esac => new isvoid =')
less, less_equal, plus, minus, star, div, semi, colon, comma = G.Terminals('< <= + - * / ; : ,')
dot, opar, cpar, ocur, ccur, inx, notx, idx, intx, string, true, false, at = G.Terminals(
    '. ( ) { } in not id int string true false @')

# Nonterminals
program = G.NonTerminal('<program>', True)
class_list, def_class = G.NonTerminals('<class-list> <class>')
feature_list, def_func, def_attr = G.NonTerminals('<feature_list> <def-func> <def-attr>')
params_list, param = G.NonTerminals('<params-list> <param>')
expr_list, expr = G.NonTerminals('<expr-list> <expr>')
cmp, arith, term, factor, atom = G.NonTerminals('<cmp> <arith> <term> <factor> <atom>')
func_call, arg_list = G.NonTerminals('<func-call> <arg-list>')
let_list, let_single = G.NonTerminals('<let-list> <let-single>')
case_list, case_single = G.NonTerminals('<case-list> <case-single>')

program %= class_list, lambda h, s: ProgramNode(s[1])

class_list %= def_class + semi + class_list, lambda h, s: [s[1]] + s[2]
class_list %= def_class + semi, lambda h, s: [s[1]]

def_class %= classx + idx + ocur + feature_list + ccur, lambda h, s: ClassDeclarationNode(s[2], s[4])
def_class %= classx + idx + inherits + idx + ocur + feature_list + ccur, lambda h, s: ClassDeclarationNode(s[2], s[6],
                                                                                                           s[4])

feature_list %= def_attr + semi + feature_list, lambda h, s: [s[1]] + s[3]
feature_list %= def_func + semi + feature_list, lambda h, s: [s[1]] + s[3]
feature_list %= G.Epsilon, lambda h, s: []

def_attr %= idx + colon + idx, lambda h, s: AttrDeclarationNode(s[1], s[3])
def_attr %= idx + colon + idx + assigment + expr, lambda h, s: AttrDeclarationNode(s[1], s[3], s[5])

def_func %= idx + opar + params_list + cpar + colon + idx + ocur + expr_list + ccur, lambda h, s: MethodDeclarationNode(
    s[1], s[3], s[6], s[8])

params_list %= param + comma + params_list, lambda h, s: [s[1]] + s[3]
params_list %= param, lambda h, s: [s[1]]
params_list %= G.Epsilon, lambda h, s: []

param %= idx + colon + idx, lambda h, s: VarDeclarationNode(s[1], s[2])

expr_list %= expr + semi,
expr_list %= expr + semi + expr_list

expr %= idx + assigment + expr
expr %= ifx + expr + thenx + expr + elsex + expr + fi
expr %= whilex + expr + loop + expr + pool
expr %= ocur + expr_list + ccur
expr %= let_list + inx + expr
expr %= ocur + expr_list + ccur
expr %= case + expr + of + case_list + esac
expr %= new + idx
expr %= isvoid + expr
expr %= notx + expr
expr %= cmp

cmp %= cmp + less + arith
cmp %= cmp + less_equal + arith
cmp %= arith

arith %= arith + plus + term
arith %= arith + minus + term
arith %= term

term %= term + star + factor
term %= term + div + factor
term %= factor

factor %= atom
factor %= opar + expr + cpar

atom %= intx
atom %= idx
atom %= factor + at + idx + dot + idx + opar + arg_list + cpar
atom %= factor + dot + idx + opar + arg_list + cpar
# atom %= idx + opar + arg_list + cpar

arg_list %= expr
arg_list %= expr + comma + arg_list
arg_list %= G.Epsilon

let_list %= let_single + let_list
let_list %= let_single

let_single %= let + idx + colon + idx

case_list %= case_single + case_list
case_list %= case_single

case_single %= idx + colon + idx + case_assigment + expr + semi
