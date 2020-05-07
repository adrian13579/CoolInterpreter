from tokenizer import CoolTokenizer

tokenizer = CoolTokenizer()
text = '''
class Point
{
    * Hola esto es un comentario
    
            * z : int;
    x : AUTO_TYPE;
    y : AUTO_TYPE;
    init(n : Int, m : Int) : SELF_TYPE {
    {
    x <- n;
    y <- m;
    }
    };
};
'''

for token in tokenizer(text):
    print(token.lex, token.token_type, token.col, token.row)
