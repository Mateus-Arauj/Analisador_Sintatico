import rules
from token_1 import Token


class Lex:
    def __init__(self, content: str, rules: list[rules.RuleInterface]):
        self.rules = rules
        self.content = content


    def next(self) -> Token:
        if not self.content:
            return None

        for rule in self.rules:
            match = rule.check_match(self.content)
            #print(f'matching rule {rule.__class__.__name__}: {match}')
            
            if not match:
                continue
            
            endpos = match.span()[1]
            self.content = self.content[endpos:].lstrip()
            return rule.extract_token(match.group(0))

        raise Exception(f'Lexical Error: symbol {self.content[0]} not recognized')
