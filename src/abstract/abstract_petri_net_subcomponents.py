from __future__ import annotations
from abc import ABC,abstractmethod
from collections.abc import Collection

class AbstractPetriNetNode(ABC):
    
    @abstractmethod
    def add_arc_from_this_node(self,arc:AbstractPetriNetArc) -> None:
        raise NotImplementedError
    
    @abstractmethod
    def add_arc_to_this_node(self,arc:AbstractPetriNetArc) ->None:
        raise NotImplementedError
    
    @property
    @abstractmethod
    def arcs_from_this_node(self) -> Collection[AbstractPetriNetArc]:
        raise NotImplementedError

    @property
    @abstractmethod
    def arcs_to_this_node(self) -> Collection[AbstractPetriNetArc]:
        raise NotImplementedError
    
class AbstractPetriNetArc(ABC):

    @property
    @abstractmethod
    def source_node(self) -> AbstractPetriNetNode:
        raise NotImplementedError
    
    @property
    @abstractmethod
    def target_node(self) -> AbstractPetriNetNode:
        raise NotImplementedError
    
    @property
    @abstractmethod
    def weight(self) -> int:
        raise NotImplementedError
    
    @property
    @abstractmethod
    def is_inhibitor(self) -> int:
        raise NotImplementedError
    
class AbstractPetriNetPlace(AbstractPetriNetNode):
    @property
    @abstractmethod
    def capacity(self) ->int:
        raise NotImplementedError
    
    @property
    @abstractmethod
    def marking(self) ->int:
        raise NotImplementedError
    
class AbstractPetriNetTransition(AbstractPetriNetNode):
    @property
    @abstractmethod
    def rate(self) ->int|float:
        raise NotImplementedError
    
    @property
    @abstractmethod
    def priority(self) ->int:
        raise NotImplementedError
    
    @abstractmethod
    def is_petri_enabled(self) -> bool:
        raise NotImplementedError
    
    @abstractmethod
    def is_signal_enabled(self) -> bool:
        raise NotImplementedError
        
    @abstractmethod
    def fire(self) -> None:
        raise NotImplementedError

class AbstractPetriNetTimedTransition(AbstractPetriNetTransition):
    @abstractmethod
    def is_time_enabled(self)->bool:
        raise NotImplementedError
    
    @abstractmethod
    def reset_timer(self)->None:
        raise NotImplementedError
    
class AbstractPetriNetTransitionsCollection(ABC):
    @abstractmethod
    def get_transition_chosen_to_fire(self) -> AbstractPetriNetTransition | None:
        raise NotImplementedError
    
    @abstractmethod
    def reset_timers(self) -> None:
        raise NotImplementedError
    
    @abstractmethod
    def __iter__(self):
        raise NotImplementedError
