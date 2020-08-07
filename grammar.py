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

# Productions
program %= class_list, lambda h, s: ProgramNode(s[1])

class_list %= def_class + semi + class_list, lambda h, s: [s[1]] + s[3]
class_list %= def_class + semi, lambda h, s: [s[1]]

def_class %= classx + idx + ocur + feature_list + ccur, lambda h, s: ClassDeclarationNode(s[2], s[4])
def_class %= classx + idx + inherits + idx + ocur + feature_list + ccur, lambda h, s: ClassDeclarationNode(s[2], s[6],
                                                                                                           s[4])

feature_list %= def_attr + semi + feature_list, lambda h, s: [s[1]] + s[3]
feature_list %= def_func + semi + feature_list, lambda h, s: [s[1]] + s[3]
feature_list %= G.Epsilon, lambda h, s: []

def_attr %= idx + colon + idx, lambda h, s: AttrDeclarationNode(s[1], s[3])
def_attr %= idx + colon + idx + assigment + expr, lambda h, s: AttrDeclarationNode(s[1], s[3], s[5])

def_func %= idx + opar + params_list + cpar + colon + idx + ocur + expr + ccur, lambda h, s: MethodDeclarationNode(
    s[1], s[3], s[6], s[8])

params_list %= param + comma + params_list, lambda h, s: [s[1]] + s[3]
params_list %= param, lambda h, s: [s[1]]
params_list %= G.Epsilon, lambda h, s: []

param %= idx + colon + idx, lambda h, s: VarDeclarationNode(s[1], s[3])

expr_list %= expr + semi, lambda h, s: [s[1]]
expr_list %= expr + semi + expr_list, lambda h, s: [s[1]] + s[3]

expr %= idx + assigment + expr, lambda h, s: AssignNode(s[1], s[3])
expr %= ifx + expr + thenx + expr + elsex + expr + fi, lambda h, s: ConditionalNode(s[2], s[4], s[6])
expr %= whilex + expr + loop + expr + pool, lambda h, s: LoopNode(s[2], s[4])
expr %= ocur + expr_list + ccur, lambda h, s: BlocksNode(s[2])
expr %= let + let_list + inx + expr, lambda h, s: LetNode(s[2], s[4])
expr %= case + expr + of + case_list + esac, lambda h, s: CaseNode(s[2], s[4])
expr %= isvoid + expr, lambda h, s: IsVoidNode(s[2])
expr %= notx + expr, lambda h, s: NotNode(s[2])
expr %= cmp, lambda h, s: s[1]

cmp %= cmp + less + arith, lambda h, s: LessNode(s[1], s[3])
cmp %= cmp + less_equal + arith, lambda h, s: LessOrEqualNode(s[1], s[3])
cmp %= cmp + equal + arith, lambda h, s: EqualsNode(s[1], s[3])
cmp %= arith, lambda h, s: s[1]

arith %= arith + plus + term, lambda h, s: PlusNode(s[1], s[3])
arith %= arith + minus + term, lambda h, s: MinusNode(s[1], s[3])
arith %= term, lambda h, s: s[1]

term %= term + star + factor, lambda h, s: StarNode(s[1], s[3])
term %= term + div + factor, lambda h, s: DivNode(s[1], s[3])
term %= factor, lambda h, s: s[1]

factor %= atom, lambda h, s: s[1]
factor %= opar + expr + cpar, lambda h, s: s[2]
factor %= new + idx, lambda h, s: InstantiateNode(s[2])

atom %= intx, lambda h, s: ConstantNumNode(s[1])
atom %= idx, lambda h, s: VariableNode(s[1])
atom %= factor + at + idx + dot + idx + opar + arg_list + cpar, lambda h, s: MethodCallNode(expr=s[1], typex=s[3],
                                                                                            idx=s[5], args=s[7])
atom %= factor + dot + idx + opar + arg_list + cpar, lambda h, s: MethodCallNode(expr=s[1], idx=s[3], args=s[5])
atom %= idx + opar + arg_list + cpar, lambda h, s: MethodCallNode(idx=s[1], args=s[3])
atom %= string, lambda h, s: StringNode(s[1])

arg_list %= expr, lambda h, s: [s[1]]
arg_list %= expr + comma + arg_list, lambda h, s: [s[1]] + s[3]
arg_list %= G.Epsilon, lambda h, s: []

let_list %= let_single + comma + let_list, lambda h, s: [s[1]] + s[3]
let_list %= let_single, lambda h, s: [s[1]]

let_single %= idx + colon + idx, lambda h, s: VarDeclarationNode(s[1], s[3])
let_single %= idx + colon + idx + assigment + expr, lambda h, s: VarDeclarationNode(s[1], s[3], s[5])

case_list %= case_single + case_list, lambda h, s: [s[1]] + s[2]
case_list %= case_single, lambda h, s: [s[1]]

case_single %= idx + colon + idx + case_assigment + expr + semi, lambda h, s: CaseOptionNode(s[1], s[3], s[5])
