from typing import Callable
from src.abstract.abstract_bool_parser import AbstractBoolParser

class BoolParser(AbstractBoolParser):
    def __init__(self,raw_cpp_style_boolean_expression:str) -> None:
        r'''
        string containing white spaces, parenthesis,
        ! : NOT operator,
        ^ : XOR operator,
        | : OR operator,
        & : AND operator,
        regex 'i\d+': input ("ex:i1,i0,i100000"),
        regex 'P\d+': place ("ex:P0,P1,P100000"),
        true,
        false,
        '''
        self._tokens:list[str]      = []
        self._tokens_test:list[str] = []
        self._inputs_set:set[str]  = set() 

        self.raw = raw_cpp_style_boolean_expression.replace(" ","")
        self._get_tokens()
        self._to_pythonic_tokens()
        self._verify_bool_expression_does_not_raise_exception()

    def generate_function(self) -> Callable[... ,bool]:
        expression = ' '.join(self._tokens)
        f = eval(f"lambda **kwargs:{expression}")
        return f
        
    def _get_tokens(self):
        p0 = p1 = 0
        tokens:list[str] = []
        input_tmp:str|None = None
        while p0 <= p1 < len(self.raw):
            substring = self.raw[p0:p1+1]
            if substring in [*"()!^|&","true","false"]:
                tokens.append(substring)
                p0 = p1 = p1+1
                continue
            elif substring[0] in ('i','P') and substring[1:].isnumeric():
                input_tmp = substring
            elif substring[0] in ('i','P') and not substring[1:].isnumeric():
                if input_tmp is not None:
                    tokens.append(input_tmp)
                    input_tmp = None
                    p0 = p1 = p1
                    continue
            
            p1 += 1
        if input_tmp is not None:
            tokens.append(input_tmp)
            
        if ''.join(tokens) == self.raw:
            self._tokens = tokens
            return
        

        raise SyntaxError("Invalid expression")
    
    def _to_pythonic_tokens(self):
        self._tokens_test:list[str] = ['']*len(self._tokens)
        should_raise = True
        conversion_map = {
            'true':"True",
            'false':"False",
            "!":"not",
            "|":'or',
            "&":"and"
        }
        for i in range(len(self._tokens)):
            if self._tokens[i] in ["true","false"] or self._tokens[i][0] in ('i','P'):
                should_raise = False

            if self._tokens[i][0] in ('i','P'):
                self._inputs_set.add(self._tokens[i])
                self._tokens_test[i] = 'True'
                self._tokens[i] = f"bool(kwargs['{self._tokens[i]}'])"
            else:
                if self._tokens[i] in conversion_map:
                    self._tokens[i] = conversion_map[self._tokens[i]]
                self._tokens_test[i] = self._tokens[i]
        
        if should_raise:
            raise SyntaxError("invalid expression")
                

    def _verify_bool_expression_does_not_raise_exception(self):
        expression = ' '.join(self._tokens_test)
        _ = eval(expression) # raises SyntaxError if expression is not valid
    
