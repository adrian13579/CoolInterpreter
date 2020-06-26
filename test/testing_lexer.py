# from tokenizer import CoolTokenizer
#
# tokenizer = CoolTokenizer()
# text = '''efre3132fdvfv_2fr2f'''
#
# for token in tokenizer(text):
#     print(token.lex, token.token_type, token.col, token.row)


a = [1, 2, 3]
b = [1, 2, 3,4]

for i, j in zip(a, b):
    print(i,j)
else:
    print(';(')

print(zip(a,b))
