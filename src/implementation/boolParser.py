from typing import Callable
from src.abstract.abstract_bool_parser import AbstractBoolParser

class BoolParser(AbstractBoolParser):
    _valid_extra_tokens:list[str] = []

    @classmethod
    def set_valid_extra_tokens(cls, valid_input_tokens:list[str]|None=None,valid_place_tokens:list[str]|None = None):
        valid_input_tokens = [extra_input_token.lower() for extra_input_token in valid_input_tokens] if valid_input_tokens is not None else []
        valid_place_tokens = [extra_place_token.lower() for extra_place_token in valid_place_tokens] if valid_place_tokens is not None else []

        cls._valid_extra_tokens = [*valid_input_tokens,*valid_place_tokens]

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

        self.raw = raw_cpp_style_boolean_expression.replace(" ","").lower()
        self._get_tokens()
        self._to_pythonic_tokens()
        self._verify_bool_expression_does_not_raise_exception()

    def generate_function(self) -> Callable[... ,bool]:
        expression = ' '.join(self._tokens)
        def f(**kwargs):
            lower_kwargs = {k.lower(): v for k, v in kwargs.items()}
            return eval(expression, {}, lower_kwargs)
        return f
        
    def _get_tokens(self):
        p0 = p1 = 0
        tokens:list[str] = []
        token_tmp:str|None = None
        while p0 <= p1 < len(self.raw):
            substring = self.raw[p0:p1+1]
            if substring in [*"()!^|&","true","false"]:
                tokens.append(substring)
                p0 = p1 = p1+1
                continue
            elif substring[0] in ('i','p') and substring in self._valid_extra_tokens:
                token_tmp = substring
            elif substring[0] in ('i','p') and not (substring in self._valid_extra_tokens):
                if token_tmp is not None:
                    tokens.append(token_tmp)
                    token_tmp = None
                    p0 = p1 = p1
                    continue
            
            p1 += 1
        if token_tmp is not None:
            tokens.append(token_tmp)
            
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
            if self._tokens[i] in ["true","false"] or self._tokens[i][0] in ('i','p'):
                should_raise = False

            if self._tokens[i][0] in ('i','p'):
                self._inputs_set.add(self._tokens[i])
                self._tokens_test[i] = 'True'
                self._tokens[i] = f"bool({self._tokens[i]})"
            else:
                if self._tokens[i] in conversion_map:
                    self._tokens[i] = conversion_map[self._tokens[i]]
                self._tokens_test[i] = self._tokens[i]
        
        if should_raise:
            raise SyntaxError("invalid expression")
                

    def _verify_bool_expression_does_not_raise_exception(self):
        expression = ' '.join(self._tokens_test)
        _ = eval(expression) # raises SyntaxError if expression is not valid
    
