from __future__ import annotations
from typing import Type
from abc import ABC,abstractmethod
from enum import Enum,auto
from collections.abc import Collection
from src.abstract.abstract_io_handler import AbstractIOHandler
from src.abstract.abstract_bool_parser import AbstractBoolParser

class AbstractPetriNetHandler(ABC):

    def __init__(self,
                 petri_net_json_structure:dict,
                 io_handler:AbstractIOHandler,
                 BoolParserClass:Type[AbstractBoolParser]
    ) -> None:
        raise NotImplementedError
    
    
    @abstractmethod
    def reset_timers(self) -> None:
        raise NotImplementedError
    
    @abstractmethod
    def set_event_callback(self,event_callback):
        raise NotImplementedError
    
    @abstractmethod
    def setup(self,petri_net_json_structure:dict) -> None:
        return NotImplementedError

    @property
    @abstractmethod
    def running_flag(self):
        raise NotImplementedError

    @running_flag.setter
    @abstractmethod
    def running_flag(self,flag:bool):
        raise NotImplementedError
    
    class Events(Enum):
        deadLock = 0
        cycleFinished = auto()

    
