import logging
from lex import Lex 
from token_1 import Token, TokenClass

class Parser:
    def __init__(self, list):
       self.current_token = None
       self.list = list
       self.py_code = ""
       self.global_vars = []
       self.code_top_flag = True
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
            #print('matching', self.current_token.token_class, self.current_token.token_value)
            self.next_token()
        elif self.current_token and self.current_token.token_class == expected_class and self.current_token.token_value == expected_value:
            #print('matching', self.current_token.token_value)
            self.next_token()
        elif self.current_token is None:
            raise SyntaxError(f"Expected {expected_class} with value {expected_value}, found end of file")
        else:
            raise SyntaxError(f"Expected {expected_class} with value {expected_value}, found {self.current_token.token_class} with value {self.current_token.token_value}")  
        
    def indent_code(self, code):
        indented_code = ""
        for line in code.split('\n'):
            #print(line)
            if line.strip() != '':
                indented_code += "  " + line + "\n"
        return indented_code   
    
    def add_global_variable(self, value): 
        if self.code_top_flag:
            self.global_vars.append(value)
            
    def parse(self):
        #print("Starting syntactic analysis...")
        #print('-'*30)
        program = self.program()
        self.py_code += program
        print('-'*30,"Translated Code",'-'*30)
        print(self.py_code)
        return self.py_code
        #print('-'*30)
        #print("Syntactic analysis successfully completed.")

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
        return constdecl + '\n'
    
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

        return f"{ident} = {number}"

    def variables(self):
        """
        <variables> --> "VAR" <vardecl> ";"
        """
        self.match(TokenClass(1),'VAR')
        var_code = self.vardecl()
        self.match(TokenClass(3),';')
        #return var_code
        return ''
        

    def vardecl(self):
        """
        <vardecl> --> <Ident> "," <vardecl> | <Ident>
        """
        vars_list = []
        self.add_global_variable(self.current_token.token_value)
        self.match(TokenClass(7)) #ID
        while self.current_token.token_value == ',':
            self.match(TokenClass(3), ',')
            self.add_global_variable(self.current_token.token_value)
            self.match(TokenClass(7)) #ID
        vars_string = ', '.join(vars_list)
        #return f"{vars_string} = None\n"
        return ''
    
    def procedures(self):
        """
        <procedures>         --> <procdecl> <procedures>
        """
        procedures = ''
        self.code_top_flag = False #Stop adding global variables to the array
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
        global_vars_decl = 'global ' + ', '.join(self.global_vars) + '\n' if self.global_vars else ''
        block_code = global_vars_decl
        block_code += self.block()
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
            # indented_block_code = self.indent_code(block_code)
            self.match(TokenClass(1),'END')
            statement += block_code
        elif self.current_token.token_value == 'IF':
            negation = ''
            self.match(TokenClass(1),'IF')
            if self.current_token.token_value == 'NOT':
                negation = "not "
                self.match(TokenClass(1),'NOT')
            cond_code = self.condition()
            self.match(TokenClass(1),'THEN')
            statement += f"if {negation}{cond_code}:\n"
            block_code = self.statement()
            indented_block_code = self.indent_code(block_code)
            statement += indented_block_code
        elif self.current_token.token_value == 'WHILE':
            negation = ''
            self.match(TokenClass(1),'WHILE')
            if self.current_token.token_value == 'NOT':
                negation = "not "
                self.match(TokenClass(1),'NOT')
            cond_code = self.condition()
            statement += f"while {negation}{cond_code}:\n"
            self.match(TokenClass(1),'DO')
            block_code = self.statement()
            indented_block_code = self.indent_code(block_code)
            statement += indented_block_code
        elif self.current_token.token_value == 'PRINT':
            self.match(TokenClass(1),'PRINT')
            expression_code = self.expression()
            statement += f"print({expression_code})\n"

        return statement
            
    def compound_statement(self):
        """
         <compound statement> --> (<statement> ";")*
        """
        compound_statement = '' 
        if self.current_token.token_value in ['CALL', 'BEGIN', 'IF', 'WHILE', 'PRINT'] or self.current_token.token_class == TokenClass(7):
            #print('-------------------------',self.current_token.token_value, self.current_token.token_class,'------------------------------------------')
            compound_statement += self.statement()
            self.match(TokenClass(3),';')
            compound_statement += self.compound_statement()
        return compound_statement
        

    
    def condition(self):
        """<condition>          --> "ODD" <expression>
                       | "EVEN" <expression>
                       | <expression> <relation> <expression>
        """
        cond_code = ""
        if self.current_token.token_value == 'ODD':
            self.match(TokenClass(1),'ODD')
            expr_code = self.expression()
            cond_code = f"({expr_code} % 2 != 0)"
        elif self.current_token.token_value == 'EVEN':
            self.match(TokenClass(1),'EVEN')
            expr_code = self.expression()
            cond_code = f"({expr_code} % 2 == 0)"
        else:
            left_expr = self.expression()
            if self.current_token.token_value == '/?':
                self.match(TokenClass(2), '/?')
                right_expr = self.expression()
                cond_code = f"{left_expr} % {right_expr} == 0"
            else:
                relation_op = self.relation()
                right_expr = self.expression()
                cond_code = f"{left_expr} {relation_op} {right_expr}"
        return cond_code

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
            return '=='
        elif self.current_token.token_value == '#':
            self.match(TokenClass(2), '#')
            return '#'
        elif self.current_token.token_value == '<':
            self.match(TokenClass(2), '<')
            return '<'
        elif self.current_token.token_value == '<=':
            self.match(TokenClass(2), '<=')
            return '<='
        elif self.current_token.token_value == '>':
            self.match(TokenClass(2), '>')
            return '>'
        elif self.current_token.token_value == '>=':
            self.match(TokenClass(2), '>=')
            return '>='
        # elif self.current_token.token_value == '/?':
        #     self.match(TokenClass(2), '/?')
        #     return '%'
        else : 
             raise SyntaxError(f"Expected relation, found {self.current_token.token_class} with value {self.current_token.token_value}")


    def expression(self):
        """
        <expression>         --> <sign>? <term> <terms>?
        """
        expr_code = ''
        expr_code += self.sign()
        expr_code += self.term()
        expr_code += self.terms()

        return expr_code 

    def sign(self):
        """
        <sign>               --> "+"
                               | "-"
        """
        sign = ''
        if self.current_token.token_value == '+':
            sign = self.current_token.token_value
            self.match(TokenClass(2),'+')

        elif self.current_token.token_value == '-':
            sign = self.current_token.token_value
            self.match(TokenClass(2), '-')

        return sign

    def term(self):
        """
        <term>               --> <factor> <factors>?
        """
        term_code = ''
        term_code += self.factor()
        term_code += self.factors()

        return term_code

    def terms(self):
        """
        <terms>              --> "+" <term>
                               | "-" <term>
        """
        terms_code = ''
        if self.current_token.token_value == '+':
            sign = self.current_token.token_value
            self.match(TokenClass(2),'+')
            term_code = self.term()
            terms_code = f" {sign} {term_code}"
            
        elif self.current_token.token_value == '-':
            sign = self.current_token.token_value
            self.match(TokenClass(2), '-')
            term_code = self.term()
            terms_code = f" {sign} {term_code}"
        return terms_code
    
    def factor(self):
        """
        <factor>             --> <Ident>
                       | <Number>
                       | "(" <expression> ")"
        """
        factor_code = ''
        if self.current_token.token_class == TokenClass(7):
            factor_code = self.current_token.token_value
            self.match(TokenClass(7)) #ID
        elif self.current_token.token_class == TokenClass(4):
            factor_code = str(self.current_token.token_value)
            self.match(TokenClass(4)) #INTEGER_CONSTANT
        elif self.current_token.token_value == '(':
            self.match(TokenClass(3),'(')
            factor_code = '(' + self.expression() + ')'
            self.match(TokenClass(3),')')
        else: 
            raise SyntaxError(f"Expected factor, found {self.current_token.token_class} with value {self.current_token.token_value}")
        return factor_code
    
    def factors(self):
        """
        <factors>            --> "/" <factor>
                       | "*" <factor>

        """
        factors_code = ''
        if self.current_token.token_value == '/':
            operator = self.current_token.token_value
            self.match(TokenClass(2), '/')
            factor_code = self.factor()
            factors_code = f" {operator} {factor_code}"
        elif self.current_token.token_value == '*':
            operator = self.current_token.token_value
            self.match(TokenClass(2), '*')
            factor_code = self.factor()
            factors_code = f" {operator} {factor_code}"
        return factors_code