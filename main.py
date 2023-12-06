from lex import Lex
import rules
from translate import Parser
from token_1 import TokenClass
diretorio = './arquivos/'
with open(diretorio + 'ex3.pl0mod.txt', 'r') as arquivo:
    content = arquivo.read()

lex = Lex(content, [ \
    rules.CommentRule(), \
    rules.ReservedWordRule(), \
    # rules.FloatingPointNumericConstanteRule(), \
    rules.IntegerNumericConstantRule(), \
    # rules.TextConstantRule(), \
    rules.DelimiterRule(), \
    rules.OperatorRule(), \
    rules.IdRule() ])
tokens = []
while True:
    token_atual = lex.next()
    if token_atual is None:
        break
    #print(f'\ntoken extraido: {token_atual}\n\n\n')
    if(token_atual.token_class != TokenClass(8)):
        tokens.append(token_atual)

parser = Parser(tokens)
parser.parse()