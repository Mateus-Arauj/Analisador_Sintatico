import logging
from lex import Lex 
from token_1 import Token, TokenClass

class Parser:
    def __init__(self, list):
       self.current_token = None
       self.list = list
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
        
    def parse(self):
        print("Starting syntactic analysis...")
        print('-'*30)
        self.program()
        print('-'*30)
        print("Syntactic analysis successfully completed.")

    def program(self):
        """
        <program> --> <block> "."
        """
        self.block()
        self.match(TokenClass(3),'.')

    def block(self):
        """
        <block> --> <constants>? <variables>? <procedures>? <statement>?
        """
        if self.current_token.token_value=='CONST':
            self.constants()
        if self.current_token.token_value=='VAR':
            self.variables()
        if self.current_token.token_value=='PROCEDURE':
            self.procedures()
        if self.current_token.token_value in ['CALL', 'BEGIN', 'IF', 'WHILE', 'PRINT'] or self.current_token.token_class == TokenClass(7):
            self.statement()
        
    def constants(self):
        """
        <constants> --> "CONST" <constdecl> ";"
        """
        self.match(TokenClass(1),'CONST')
        self.constdecl()
        self.match(TokenClass(3),';')

    def constdecl(self):
        """
        <constdecl> --> <constdef> "," <constdecl> | <constdef>
        """
        self.constdef()
        while self.current_token.token_value == ',':
            self.match(TokenClass(3), ',')
            self.constdef()

    def constdef(self):
        """
        <constdef> --> <Ident> "=" <Number>
        """
        self.match(TokenClass(7)) #ID
        self.match(TokenClass(2), '=')
        self.match(TokenClass(4)) #INTEGER_CONSTANT

    def variables(self):
        """
        <variables> --> "VAR" <vardecl> ";"
        """
        self.match(TokenClass(1),'VAR')
        self.vardecl()
        self.match(TokenClass(3),';')

    def vardecl(self):
        """
        <vardecl> --> <Ident> "," <vardecl> | <Ident>
        """
        self.match(TokenClass(7)) #ID
        while self.current_token.token_value == ',':
            self.match(TokenClass(3), ',')
            self.match(TokenClass(7)) #ID

    def procedures(self):
        """
        <procedures>         --> <procdecl> <procedures>
        """
        self.procdecl()
        while self.current_token.token_value == 'PROCEDURE':
            self.procdecl()
        
    def procdecl(self):
        """
        <procdecl> --> "PROCEDURE" <Ident> ";" <block> ";"
        """
        self.match(TokenClass(1), 'PROCEDURE')
        self.match(TokenClass(7)) #ID
        self.match(TokenClass(3),';')
        self.block()
        self.match(TokenClass(3),';')
        
    def statement(self):
        """"
        <statement>          --> <Ident> "<-" <expression>
                       | "CALL" <Ident>
                       | "BEGIN" <compound statement> "END"
                       | "IF" "NOT"? <condition> "THEN" <statement>
                       | "WHILE" "NOT"? <condition> "DO" <statement>
                       | "PRINT" <expression>
        """
        
        if self.current_token.token_class == TokenClass(7):
            self.match(TokenClass(7)) #ID
            self.match(TokenClass(2), '<-')
            self.expression()
        elif self.current_token.token_value == 'CALL':
            self.match(TokenClass(1), 'CALL')
            self.match(TokenClass(7)) #ID
        elif self.current_token.token_value == 'BEGIN':
            self.match(TokenClass(1),'BEGIN')
            self.compound_statement()
            self.match(TokenClass(1),'END')
        elif self.current_token.token_value == 'IF':
            self.match(TokenClass(1),'IF')
            if self.current_token.token_value == 'NOT':
                self.match(TokenClass(1),'NOT')
            self.condition()
            self.match(TokenClass(1),'THEN')
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
            
            
    def compound_statement(self):
        """
         <compound statement> --> (<statement> ";")*
        """
        if self.current_token.token_value in ['CALL', 'BEGIN', 'IF', 'WHILE', 'PRINT'] or self.current_token.token_class == TokenClass(7):
            print('-------------------------',self.current_token.token_value, self.current_token.token_class,'------------------------------------------')
            self.statement()
            self.match(TokenClass(3),';')
            self.compound_statement()
        

    
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