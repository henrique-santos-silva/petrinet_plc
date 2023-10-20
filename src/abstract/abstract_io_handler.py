from abc import ABC,abstractmethod
from src.abstract.abstract_bool_parser import AbstractBoolParser
from src.abstract.abstract_petri_net_subcomponents import AbstractPetriNetPlace
from typing import Type
class AbstractIOHandler(ABC):
     
     @abstractmethod
     def set_marking_to_output_expressions(self,marking_to_output_expressions:dict[str,str],BoolParserClass:Type[AbstractBoolParser])->None:
          raise NotImplementedError
     
     @abstractmethod
     def update_outputs(self,places:dict[str,AbstractPetriNetPlace]) -> dict[str,dict[str,bool]]:
          raise NotImplementedError
     
     @abstractmethod
     def clear(self):
          raise NotImplementedError
     
     @abstractmethod
     def get_all(self) -> dict[str,dict[str,bool]]:
          raise NotImplementedError
     
     @property
     @abstractmethod
     def has_been_updated(self) ->bool:
          raise NotImplementedError