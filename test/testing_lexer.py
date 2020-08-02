from serializers import TokenizerHandler
from tokenizer import CoolTokenizer

path = "/mnt/69F79531507E7A36/CS/This year's stuff/Compilacion/Proyectos/CoolInterpreter/tools"
tokenizer = TokenizerHandler.load(path+'/lexer')
text = '''efre3132fdvfv_2fr2f'''

for token in tokenizer(text):
    print(token.lex, token.token_type, token.col, token.row)