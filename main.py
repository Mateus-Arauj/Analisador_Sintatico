from lex import Lex
import rules
from translate import Parser
from token_1 import TokenClass
diretorio = './files/'
with open(diretorio + 'ex2.pl0mod.txt', 'r') as arquivo:
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

python_builtin_functions = [
    "abs", "all", "any", "ascii", "bin", "bool", "breakpoint", "bytearray", "bytes",
    "callable", "chr", "classmethod", "compile", "complex", "delattr", "dict", "dir", "divmod",
    "enumerate", "eval", "exec", "filter", "float", "format", "frozenset", "getattr", "globals",
    "hasattr", "hash", "help", "hex", "id", "input", "int", "isinstance", "issubclass", "iter",
    "len", "list", "locals", "map", "max", "memoryview", "min", "next", "object", "oct", "open",
    "ord", "pow", "print", "property", "range", "repr", "reversed", "round", "set", "setattr",
    "slice", "sorted", "staticmethod", "str", "sum", "super", "tuple", "type", "vars", "zip", "__import__"
]
for token in tokens:
    if token.token_value in python_builtin_functions:
        print(f"Problematic token detected! This token can cause issues in the execution of Python code as it may be a reserved word or a built-in function.: {token}")


parser = Parser(tokens)
result = parser.parse()
#Saving the result as a Python file
file_name = './converted_files/result.py'
with open(file_name, "w") as file:
    file.write(result)
