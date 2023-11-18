from abc import ABC,abstractmethod
from typing import Callable
class AbstractBoolParser(ABC):
    
    @classmethod
    def set_valid_extra_tokens(cls, valid_input_tokens:list[str]|None=None,valid_place_tokens:list[str]|None = None):
        raise NotImplementedError

    @abstractmethod
    def __init__(self,raw_cpp_style_boolean_expression:str):
        raise NotImplementedError

    @abstractmethod
    def generate_function(self) -> Callable[..., bool] :
        raise NotImplementedError