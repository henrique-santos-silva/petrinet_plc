from __future__ import annotations
import random
from src.abstract.abstract_petri_net_subcomponents import *
from src.abstract.abstract_petri_net_subcomponents import AbstractPetriNetArc, AbstractPetriNetTransition
from src.abstract.abstract_io_handler import AbstractIOHandler
from src.abstract.abstract_bool_parser import AbstractBoolParser
import time
from typing import Callable
from enum import Enum,auto

class PetriNetNode(AbstractPetriNetNode):
    def __init__(self,id:str) -> None:
        super().__init__()
        self.id: str = id
        self._arcs_from_this_node: list[AbstractPetriNetArc] = []  # arcs that have this ArcReceiver as Source 
        self._arcs_to_this_node:   list[AbstractPetriNetArc] = []

    def add_arc_from_this_node(self, arc: AbstractPetriNetArc) -> None:
        self._arcs_from_this_node.append(arc)
   
    def add_arc_to_this_node(self, arc: AbstractPetriNetArc) -> None:
        self._arcs_to_this_node.append(arc)
    
    @property
    def arcs_from_this_node(self) -> list[AbstractPetriNetArc]:
        return self._arcs_from_this_node
 
    @property
    def arcs_to_this_node(self) -> list[AbstractPetriNetArc]:
        return self._arcs_to_this_node

class Arc(AbstractPetriNetArc):
    def __init__(self,
                 id:str,
                 source_node:AbstractPetriNetNode,
                 target_node:AbstractPetriNetNode,
                 weight:int,
                 is_inhibitor:bool) -> None:
        super().__init__()
        if (
            (isinstance(source_node,BaseTransition) and isinstance(target_node,BaseTransition))
             or
            (isinstance(source_node,Place) and isinstance(target_node,Place))
            ):
            raise TypeError(f"arc can't connect a {type(source_node)} to another {type(target_node)}")
        
        self.id = id
        self._source_node = source_node
        self._target_node = target_node
        self._weight = weight
        self._is_inhibitor = is_inhibitor

        source_node.add_arc_from_this_node(self)
        target_node.add_arc_to_this_node(self)
    
    @property
    def source_node(self) -> AbstractPetriNetNode:
        return self._source_node
    @property
    def target_node(self) -> AbstractPetriNetNode:
        return self._target_node

    @property
    def weight(self) -> int:
        return self._weight
    
    @property
    def is_inhibitor(self) -> int:
        return self._is_inhibitor

class Place(PetriNetNode,AbstractPetriNetPlace):
    def __init__(self,
                 id:str,
                 capacity:int,
                 marking:int,
                 ) -> None:
        super().__init__(id)
        self.id = id
        self._capacity = capacity if capacity > 0 else float('inf')
        self._marking = marking
        self._initial_marking = marking
        if self._marking > self._capacity:
            raise ValueError("place marking can't be greater than it's capacity")

    # def update_signal_output(self) -> int:
    #     return super().update_signal_output()
    
    @property
    def capacity(self) -> int:
        return self._capacity
    
    @property
    def marking(self) -> int:
        return self._marking
    
    @marking.setter
    def marking(self,marking:int) -> None:
        if marking > self.capacity:
            raise ValueError("place marking can't be greater than it's capacity")
        self._marking = marking

    @property
    def initial_marking(self) -> int:
        return self._initial_marking
    
class BaseTransition(PetriNetNode,AbstractPetriNetTransition):
    def __init__(self,
                id: str,
                rate:int|float,
                priority:int,
                signal_enabling_expression:str =  "True",
                io_handler:AbstractIOHandler|None = None,
                BoolParserClass:type[AbstractBoolParser]|None = None
                ) -> None:
        super().__init__(id)
        self._priority = priority
        self._rate = rate
        self._is_signal_enabled_val:bool = False
        self._is_petri_enabled_val:bool = False
        self._io_handler = io_handler
        if signal_enabling_expression == "True":
            self._is_signal_enabled_function = lambda: True
        elif signal_enabling_expression != "True" and (io_handler is None or BoolParserClass is None):
            raise TypeError("in case signal_enabling_expression is provided, function also requires IO_handler and BoolParserClass")
        else:
            assert(io_handler is not None)
            assert(BoolParserClass is not None)
            self._is_signal_enabled_function = BoolParserClass(signal_enabling_expression).generate_function()
    
    def __repr__(self) -> str:
        return self.id

    @property
    def rate(self) ->float:
        return self._rate
    
    @property
    def priority(self) ->int:
        return self._priority
            
    def is_petri_enabled(self) -> bool:
        for arc in self.arcs_to_this_node:
            preplace = arc.source_node
            assert(isinstance(preplace,Place))

            if (((not arc.is_inhibitor) and (preplace.marking < arc.weight))
                or
                (arc.is_inhibitor and preplace.marking > 0) 
                ):
                self._is_petri_enabled_val = False
                return self._is_petri_enabled_val
            

        for arc in self.arcs_from_this_node:
            postplace = arc.target_node
            assert(isinstance(postplace,Place))
            if arc.weight > postplace.capacity - postplace.marking:
                self._is_petri_enabled_val = False
                return self._is_petri_enabled_val
        
        self._is_petri_enabled_val = True
        return self._is_petri_enabled_val
            
    def is_signal_enabled(self) -> bool:
        
        if self._io_handler is not None:
            kwargs = self._io_handler.get_all()["digital_inputs"]
        else:
            kwargs = dict()
        self._is_signal_enabled_val = self._is_signal_enabled_function(**kwargs)
        return self._is_signal_enabled_val
        
    def fire(self) -> None:
        if not (self._is_signal_enabled_val and self._is_petri_enabled_val):
            raise RuntimeError("transition cannot fire if it its not enabled")
        
        for arc in self.arcs_to_this_node:
            if not arc.is_inhibitor:
                preplace = arc.source_node
                assert(isinstance(preplace,Place))
                preplace.marking -= arc.weight
            
        for arc in self.arcs_from_this_node:
            postplace = arc.target_node
            assert(isinstance(postplace,Place))
            postplace.marking += arc.weight

class InstantaneousTransition(BaseTransition):
    def __init__(self, id: str, rate: int | float, priority: int, signal_enabling_expression: str = "True", io_handler: AbstractIOHandler | None = None, BoolParserClass: type[AbstractBoolParser] | None = None) -> None:
        super().__init__(id, rate, priority, signal_enabling_expression, io_handler, BoolParserClass)
    
class TimedTransition(AbstractPetriNetTimedTransition,BaseTransition):
    def __init__(
            self,
            id: str,
            rate: int | float, 
            priority: int, 
            signal_enabling_expression: str = "True", 
            io_handler: AbstractIOHandler | None = None, 
            BoolParserClass: type[AbstractBoolParser] | None = None,
            timer_sec: int|float = 0
            ) -> None:
        super().__init__(id, rate, priority, signal_enabling_expression, io_handler, BoolParserClass)
        self._timer_sec = timer_sec
        self._enabled_since:float|None = None
        self._is_time_enabled_val:bool = False
    
    def reset_timer(self):
        self._enabled_since = None
    
    def is_petri_enabled(self) -> bool:
        super().is_petri_enabled()
        if not self._is_petri_enabled_val:
            self._enabled_since = None

        return self._is_petri_enabled_val

    def is_signal_enabled(self) -> bool:
        super().is_signal_enabled()

        if not self._is_signal_enabled_val:
            self._enabled_since = None

        return self._is_signal_enabled_val
        
    def is_time_enabled(self)->bool:
        if (self._enabled_since is None
            and 
            self._is_petri_enabled_val
            and 
            self._is_signal_enabled_val):
            self._enabled_since = time.time()

        if self._enabled_since is not None:
            self._is_time_enabled_val = time.time() - self._enabled_since > self._timer_sec
            return self._is_time_enabled_val 
        
        self._is_time_enabled_val = False
        return self._is_time_enabled_val 
    
    def fire(self):
        super().fire()
        self._enabled_since = None

class PetriNetDeadlockError(Exception):
    """Exception raised for Petri net deadlock situations."""
    def __init__(self, message:str="Petri net deadlock detected"):
        self.message = message
        super().__init__(message)

class TransitionsCollection(AbstractPetriNetTransitionsCollection):
    
    def __init__(self,
                transitions:list[InstantaneousTransition|TimedTransition],
                io_handler:AbstractIOHandler) -> None:
        self._io_handler = io_handler
        self._inner_state_function_get_transition_chosen_to_fire = TransitionsCollection.InnerStateFunctionGetTransitionChosenToFire.CHECK_PETRI_ENABLING

        self._instantaneous_transitions = TransitionsCollection.TransitionsByPriority()
        self._timed_transitions =  TransitionsCollection.TransitionsByPriority()

        self._petri_enabled_instantaneous_transitions = TransitionsCollection.TransitionsByPriority()
        self._petri_enabled_timed_transitions = TransitionsCollection.TransitionsByPriority()
        self._signal_enabled_instantaneous_transitions = TransitionsCollection.TransitionsByPriority()
        self._signal_enabled_timed_transitions = TransitionsCollection.TransitionsByPriority()
        self._time_enabled_timed_transitions = TransitionsCollection.TransitionsByPriority()
        # self._transition_chosen_to_fire_generator = self._generate_transition_chosen_to_fire()
        
        
        for transition in transitions:

            if isinstance(transition,InstantaneousTransition):
                self._instantaneous_transitions.append(transition)                
            else:
                self._timed_transitions.append(transition)
    
    def __repr__(self) -> str:
        return f"""TransitionsCollection(
    instantaneous_transitions:               {self._instantaneous_transitions},
    timed_transitions:                       {self._timed_transitions},
    petri_enabled_instantaneous_transitions: {self._petri_enabled_instantaneous_transitions},
    petri_enabled_timed_transitions:         {self._petri_enabled_timed_transitions}
    signal_enabled_instantaneous_transitions:{self._signal_enabled_instantaneous_transitions},
    signal_enabled_timed_transitions:        {self._signal_enabled_timed_transitions},
    self._time_enabled_timed_transitions:    {self._time_enabled_timed_transitions}
)"""


    def reset_timers(self):
        for timed_transition in self._timed_transitions:
            timed_transition.reset_timer()


    def get_transition_chosen_to_fire(self) -> BaseTransition | None:
        # return next(self._transition_chosen_to_fire_generator)
        enum_inner_states = TransitionsCollection.InnerStateFunctionGetTransitionChosenToFire

        if self._inner_state_function_get_transition_chosen_to_fire == (
            enum_inner_states.CHECK_PETRI_ENABLING):
            self._update_petri_enabled_instantaneous_transitions()
            self._update_petri_enabled_timed_transitions()
            if (
                self._petri_enabled_instantaneous_transitions.is_empty and
                self._petri_enabled_timed_transitions.is_empty):
                raise PetriNetDeadlockError
            
            self._inner_state_function_get_transition_chosen_to_fire = enum_inner_states.WAITING_FULL_ENABLING
            
            self._update_signal_enabled_instantaneous_transitions()            
            self._update_signal_enabled_timed_transitions()
            self._update_time_enabled_timed_transitions()

        if self._inner_state_function_get_transition_chosen_to_fire == (
            enum_inner_states.WAITING_FULL_ENABLING):

            if self._io_handler.has_been_updated: #some io change has happened
                self._update_signal_enabled_instantaneous_transitions()            
                self._update_signal_enabled_timed_transitions()
                self._update_time_enabled_timed_transitions()

            if not self._signal_enabled_instantaneous_transitions.is_empty:
                self._inner_state_function_get_transition_chosen_to_fire =enum_inner_states.CHECK_PETRI_ENABLING
                return self._signal_enabled_instantaneous_transitions.choose_based_on_priority_and_rate() 

            if not self._signal_enabled_timed_transitions.is_empty:
                self._update_time_enabled_timed_transitions()
                if not self._time_enabled_timed_transitions.is_empty:
                    return self._time_enabled_timed_transitions.choose_based_on_priority_and_rate()
        
        return None

    def _update_petri_enabled_instantaneous_transitions(self):
        self._petri_enabled_instantaneous_transitions.update_from_superset(
            superset = self._instantaneous_transitions,
            method = BaseTransition.is_petri_enabled
        )
    def _update_petri_enabled_timed_transitions(self):
        self._petri_enabled_timed_transitions.update_from_superset(
            superset = self._timed_transitions,
            method = TimedTransition.is_petri_enabled
        )

    def _update_signal_enabled_instantaneous_transitions(self):
        self._signal_enabled_instantaneous_transitions.update_from_superset(
            superset = self._petri_enabled_instantaneous_transitions,
            method = BaseTransition.is_signal_enabled
        )
    
    def _update_signal_enabled_timed_transitions(self):
        self._signal_enabled_timed_transitions.update_from_superset(
            superset = self._petri_enabled_timed_transitions,
            method = TimedTransition.is_signal_enabled
        )
    
    def _update_time_enabled_timed_transitions(self):
        self._time_enabled_timed_transitions.update_from_superset(
            superset = self._signal_enabled_timed_transitions,
            method = TimedTransition.is_time_enabled
        )

    #Helper classes
    class InnerStateFunctionGetTransitionChosenToFire(Enum):
        CHECK_PETRI_ENABLING = 0
        WAITING_FULL_ENABLING = auto()



    class TransitionsListWithRateAccumulator:
        def __init__(self) -> None:
            self.transitions_list:list[InstantaneousTransition|TimedTransition] = []
            self.accumulator = 0
        
        def append(self,transition:InstantaneousTransition|TimedTransition):
            self.transitions_list.append(transition)
            self.accumulator += transition.rate
        
        def __iter__(self):
            return self.transitions_list.__iter__()
        
        def __repr__(self) -> str:
            return f"TransitionsListWithRateAccumulator({self.transitions_list.__repr__()},{self.accumulator})"
        
    class TransitionsByPriority:                
        def __init__(self):
            self._max_value_priority:int|None = None
            self._dict:dict[
                int, # priority
                TransitionsCollection.TransitionsListWithRateAccumulator
            ] = dict()
        
        def __repr__(self) -> str:
            return f"TransitionsByPriority({self._dict})"
        
        def append(self,transition:InstantaneousTransition|TimedTransition):
            self._max_value_priority = max(transition.priority,self._max_value_priority or transition.priority)
            if transition.priority in self._dict:
                self._dict[transition.priority].append(transition)
            else:
                new_list = TransitionsCollection.TransitionsListWithRateAccumulator()
                new_list.append(transition)
                self._dict[transition.priority] = new_list
            

        def clear(self):
            self._max_value_priority = None
            self._dict = dict()
        
        @property
        def is_empty(self) -> bool:
            return len(self._dict) == 0
        
        def update_from_superset(self,
                                 superset:TransitionsCollection.TransitionsByPriority,
                                 method:Callable[[InstantaneousTransition|TimedTransition],bool]
        ):
            self.clear()
            for transition in superset:
                if method(transition):
                    self.append(transition)
    
        def choose_based_on_priority_and_rate(self) -> InstantaneousTransition|TimedTransition:
            assert(isinstance(self._max_value_priority,int))
            eligible_transitions = self._dict[self._max_value_priority]
            random_value = random.random() * eligible_transitions.accumulator
            acummulator = 0
            for eligible_transition in  eligible_transitions:
                acummulator += eligible_transition.rate
                if random_value <= acummulator:
                    return eligible_transition

            raise NotImplementedError

        def __iter__(self):
            return self._generator()

        def _generator(self):
            for transitions in self._dict.values():
                for transition in transitions:
                    yield transition