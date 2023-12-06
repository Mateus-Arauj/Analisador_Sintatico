import logging
from lex import Lex 
from token_1 import Token, TokenClass

class Parser:
    def __init__(self, list):
       self.current_token = None
       self.list = list
       self.py_code = ""
       #print(list)
       self.next_token()


    def next_token(self):
       #print('next_token')
       if len(self.list) > 0:
           self.current_token = self.list.pop(0)
       else:
           self.current_token = None

    def match(self, expected_class, expected_value = None):
        #print(self.current_token.token_class, self.current_token.token_value)
        if expected_value == None and self.current_token.token_class == expected_class:
            print('matching', self.current_token.token_class, self.current_token.token_value)
            self.next_token()
        elif self.current_token and self.current_token.token_class == expected_class and self.current_token.token_value == expected_value:
            print('matching', self.current_token.token_value)
            self.next_token()
        elif self.current_token is None:
            raise SyntaxError(f"Expected {expected_class} with value {expected_value}, found end of file")
        else:
            raise SyntaxError(f"Expected {expected_class} with value {expected_value}, found {self.current_token.token_class} with value {self.current_token.token_value}")  
        
    def indent_code(self, code):
        """
        Adiciona a indentação necessária ao código do bloco da função.
        """
        indented_code = ""
        for line in code.split('\n'):
            if line.strip() != '':
                indented_code += "  " + line + "\n"
        return indented_code   
    
    def parse(self):
        print("Starting syntactic analysis...")
        print('-'*30)
        program = self.program()
        self.py_code += program
        print(self.py_code)
        print('-'*30)
        print("Syntactic analysis successfully completed.")

    def program(self):
        """
        <program> --> <block> "."
        """
        blocks = self.block()
        self.match(TokenClass(3),'.')
        return blocks

    def block(self):
        """
        <block> --> <constants>? <variables>? <procedures>? <statement>?
        """
        block = ''
        if self.current_token.token_value=='CONST':
            block += self.constants()
        if self.current_token.token_value=='VAR':
            block += self.variables()
        if self.current_token.token_value=='PROCEDURE':
            block += self.procedures()
        if self.current_token.token_value in ['CALL', 'BEGIN', 'IF', 'WHILE', 'PRINT'] or self.current_token.token_class == TokenClass(7):
            block += self.statement()

        return block
        
    def constants(self):
        """
        <constants> --> "CONST" <constdecl> ";"
        """
        self.match(TokenClass(1),'CONST')
        constdecl =  self.constdecl()
        self.match(TokenClass(3),';')
        return constdecl
    
    def constdecl(self):
        """
        <constdecl> --> <constdef> "," <constdecl> | <constdef>
        """
        constdecl = ''
        constdecl += self.constdef()
        while self.current_token.token_value == ',':
            self.match(TokenClass(3), ',')
            constdecl += ','
            constdecl += self.constdef()
        return constdecl

    def constdef(self):
        """
        <constdef> --> <Ident> "=" <Number>
        """
        ident = self.current_token.token_value
        self.match(TokenClass(7)) #ID
        self.match(TokenClass(2), '=')
        number = self.current_token.token_value
        self.match(TokenClass(4)) #INTEGER_CONSTANT

        return f"{ident.upper()} = {number}\n"

    def variables(self):
        """
        <variables> --> "VAR" <vardecl> ";"
        """
        self.match(TokenClass(1),'VAR')
        var_code = self.vardecl()
        self.match(TokenClass(3),';')
        return var_code
        

    def vardecl(self):
        """
        <vardecl> --> <Ident> "," <vardecl> | <Ident>
        """
        vars_list = []
        vars_list.append(self.current_token.token_value)
        self.match(TokenClass(7)) #ID
        while self.current_token.token_value == ',':
            self.match(TokenClass(3), ',')
            vars_list.append(self.current_token.token_value)
            self.match(TokenClass(7)) #ID
        vars_string = ', '.join(vars_list)
        return f"{vars_string} = None\n"
    
    def procedures(self):
        """
        <procedures>         --> <procdecl> <procedures>
        """
        procedures = ''
        procedures += self.procdecl()
        while self.current_token.token_value == 'PROCEDURE':
             procedures += self.procdecl()
        return procedures
        
    def procdecl(self):
        """
        <procdecl> --> "PROCEDURE" <Ident> ";" <block> ";"
        """
        procdecl = ''
        self.match(TokenClass(1), 'PROCEDURE')
        proc_name = self.current_token.token_value
        self.match(TokenClass(7)) #ID
        self.match(TokenClass(3),';')
        procdecl += f"def {proc_name}():\n"
        block_code = self.block()
        indented_block_code = self.indent_code(block_code)
        self.match(TokenClass(3),';')
        procdecl += indented_block_code
        return procdecl
        
    def statement(self):
        """"
        <statement>          --> <Ident> "<-" <expression>
                       | "CALL" <Ident>
                       | "BEGIN" <compound statement> "END"
                       | "IF" "NOT"? <condition> "THEN" <statement>
                       | "WHILE" "NOT"? <condition> "DO" <statement>
                       | "PRINT" <expression>
        """
        statement = ''
        if self.current_token.token_class == TokenClass(7):
            var_name = self.current_token.token_value
            self.match(TokenClass(7)) #ID
            self.match(TokenClass(2), '<-')
            expr_code = self.expression()
            statement = f"{var_name} = {expr_code}\n"
        elif self.current_token.token_value == 'CALL':
            self.match(TokenClass(1), 'CALL')
            proc_name = self.current_token.token_value
            self.match(TokenClass(7)) #ID
            statement = f"{proc_name}()\n"
        elif self.current_token.token_value == 'BEGIN':
            self.match(TokenClass(1),'BEGIN')
            block_code = self.compound_statement()
            indented_block_code = self.indent_code(block_code)
            self.match(TokenClass(1),'END')
            statement += indented_block_code
        elif self.current_token.token_value == 'IF':
            negation = ''
            self.match(TokenClass(1),'IF')
            if self.current_token.token_value == 'NOT':
                negation = "not "
                self.match(TokenClass(1),'NOT')
            cond_code = self.condition()
            self.match(TokenClass(1),'THEN')
            statement += f"if {negation}{cond_code}:\n"
            self.statement()
        elif self.current_token.token_value == 'WHILE':
            self.match(TokenClass(1),'WHILE')
            if self.current_token.token_value == 'NOT':
                self.match(TokenClass(1),'NOT')
            self.condition()
            self.match(TokenClass(1),'DO')
            self.statement()
        elif self.current_token.token_value == 'PRINT':
            self.match(TokenClass(1),'PRINT')
            self.expression()
        return statement
            
    def compound_statement(self):
        """
         <compound statement> --> (<statement> ";")*
        """
        compound_statement = '' 
        if self.current_token.token_value in ['CALL', 'BEGIN', 'IF', 'WHILE', 'PRINT'] or self.current_token.token_class == TokenClass(7):
            print('-------------------------',self.current_token.token_value, self.current_token.token_class,'------------------------------------------')
            compound_statement += self.statement()
            self.match(TokenClass(3),';')
            self.compound_statement()
        return compound_statement
        

    
    def condition(self):
        """<condition>          --> "ODD" <expression>
                       | "EVEN" <expression>
                       | <expression> <relation> <expression>
        """
        if self.current_token.token_value == 'ODD':
            self.match(TokenClass(1),'ODD')
            self.expression()
        elif self.current_token.token_value == 'EVEN':
            self.match(TokenClass(1),'EVEN')
            self.expression()
        else:
            self.expression()
            self.relation()
            self.expression()

    def relation(self):
        """
        <relation>           --> "="
                       | "#"
                       | "<"
                       | "<="
                       | ">"
                       | ">="
                       | "/?"
        """
        if self.current_token.token_value == '=':
            self.match(TokenClass(2), '=')
        elif self.current_token.token_value == '#':
            self.match(TokenClass(2), '#')
        elif self.current_token.token_value == '<':
            self.match(TokenClass(2), '<')
        elif self.current_token.token_value == '<=':
            self.match(TokenClass(2), '<=')
        elif self.current_token.token_value == '>':
            self.match(TokenClass(2), '>')
        elif self.current_token.token_value == '>=':
            self.match(TokenClass(2), '>=')
        elif self.current_token.token_value == '/?':
            self.match(TokenClass(2), '/?')
        else : 
             raise SyntaxError(f"Expected relation, found {self.current_token.token_class} with value {self.current_token.token_value}")


    def expression(self):
        """
        <expression>         --> <sign>? <term> <terms>?
        """
        self.sign()
        self.term()
        self.terms()

    def sign(self):
        """
        <sign>               --> "+"
                               | "-"
        """
        if self.current_token.token_value == '+':
            self.match(TokenClass(2),'+')
        elif self.current_token.token_value == '-':
            self.match(TokenClass(2), '-')

    def term(self):
        """
        <term>               --> <factor> <factors>?
        """
        self.factor()
        self.factors()


    def terms(self):
        """
        <terms>              --> "+" <term>
                               | "-" <term>
        """
        if self.current_token.token_value == '+':
            self.match(TokenClass(2),'+')
            self.term()
        elif self.current_token.token_value == '-':
            self.match(TokenClass(2), '-')
            self.term()

    def factor(self):
        """
        <factor>             --> <Ident>
                       | <Number>
                       | "(" <expression> ")"
        """
        if self.current_token.token_class == TokenClass(7):
            self.match(TokenClass(7)) #ID
        elif self.current_token.token_class == TokenClass(4):
            self.match(TokenClass(4)) #INTEGER_CONSTANT
        elif self.current_token.token_value == '(':
            self.match(TokenClass(3),'(')
            self.expression()
            self.match(TokenClass(3),')')
        else: 
            raise SyntaxError(f"Expected factor, found {self.current_token.token_class} with value {self.current_token.token_value}")

    
    def factors(self):
        """
        <factors>            --> "/" <factor>
                       | "*" <factor>

        """
        if self.current_token.token_value == '/':
            self.match(TokenClass(2), '/')
            self.factor()
        elif self.current_token.token_value == '*':
            self.match(TokenClass(2), '*')
            self.factor()