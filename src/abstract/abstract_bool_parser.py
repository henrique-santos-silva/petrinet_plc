from abc import ABC,abstractmethod
from typing import Callable
class AbstractBoolParser(ABC):
    
    @abstractmethod
    def __init__(self,raw_cpp_style_boolean_expression:str):
        raise NotImplementedError

    @abstractmethod
    def generate_function(self) -> Callable[..., bool] :
        raise NotImplementedError