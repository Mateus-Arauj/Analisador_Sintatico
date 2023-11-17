import re
from token_1 import Token, TokenClass


class RuleInterface:
    def regex_rules(self) -> list[str]:
        pass
    def extract_token(self, match: str) -> Token:
        pass
    def check_match(self, content: str) -> re.Match:
        for rule in self.regex_rules():
            match = re.match('^' + rule, content)
            if match:
                return match
        return None

class IntegerNumericConstantRule(RuleInterface):
    def regex_rules(self) -> list[str]:
        return [r'\b\d+\b']
    def extract_token(self, match: str) -> Token:
        return Token(TokenClass.INTEGER_CONSTANT, int(match))
    
# class FloatingPointNumericConstanteRule(RuleInterface):
#     def regex_rules(self) -> list[str]:
#         return [r'\d*\.\d+']
#     def extract_token(self, match: str) -> Token:
#         return Token(TokenClass.FLOAT_CONSTANT, match)
    
class IdRule(RuleInterface):
    def regex_rules(self) -> list[str]:
        return [r'[a-zA-Z_][a-zA-Z0-9_]*']
    def extract_token(self, match: str) -> Token:
        return Token(TokenClass.ID, match)

class ReservedWordRule(RuleInterface):
    def regex_rules(self) -> list[str]:
         return [
            r'\bCONST\b', 
            r'\bVAR\b', 
            r'\bPROCEDURE\b', 
            r'\bCALL\b', 
            r'\bBEGIN\b', 
            r'\bEND\b', 
            r'\bIF\b', 
            r'\bTHEN\b',
            r'\bWHILE\b', 
            r'\bDO\b', 
            r'\bPRINT\b', 
            r'\bODD\b', 
            r'\bEVEN\b', 
            r'\bNOT\b'
        ]
    def extract_token(self, match: str) -> Token:
        return Token(TokenClass.RESERVED_WORD, match)

# class OperatorRule(RuleInterface):
#     def regex_rules(self) -> list[str]:
#         return [r'[=#<>\/\?\+\-\*]|<-|\/\?']
#     def extract_token(self, match: str) -> Token:
#         return Token(TokenClass.OPERATOR, match)

class OperatorRule(RuleInterface):
    def regex_rules(self) -> list[str]:
        return [r'<=|>=|/\?|<-|[=#+<>*-/]']
    def extract_token(self, match: str) -> Token:
        return Token(TokenClass.OPERATOR, match)

class DelimiterRule(RuleInterface):
    def regex_rules(self) -> list[str]:
        return [r'[,;().]']
    def extract_token(self, match: str) -> Token:
        return Token(TokenClass.DELIMITER, match)

# class TextConstantRule(RuleInterface):
#     def regex_rules(self) -> list[str]:
#         return [r'".*?"']
#     def extract_token(self, match: str) -> Token:
#         return Token(TokenClass.TEXT_CONSTANT, match)
    
class CommentRule(RuleInterface):
    def regex_rules(self) -> list[str]:
        return [r'\{[^}]*\}']
    def extract_token(self, match: str) -> Token:
        return Token(TokenClass.COMMENT, match) 