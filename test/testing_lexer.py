from tokenizer import CoolTokenizer

tokenizer = CoolTokenizer()
text = '''efre3132fdvfv_2fr2f'''

for token in tokenizer(text):
    print(token.lex, token.token_type, token.col, token.row)