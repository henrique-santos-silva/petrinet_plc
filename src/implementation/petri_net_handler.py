from typing import Type
import threading
from src import thread_error_queue
from time import sleep
from src.abstract.abstract_bool_parser import AbstractBoolParser
from src.abstract.abstract_io_handler import AbstractIOHandler
from src.abstract.abstract_petri_net_handler import AbstractPetriNetHandler
from src.implementation.petri_net_subcomponents import Arc,Place,TimedTransition,InstantaneousTransition,TransitionsCollection,PetriNetDeadlockError

class PetriNetHandler(AbstractPetriNetHandler):
    def __init__(self,
                io_handler: AbstractIOHandler,
                BoolParserClass:Type[AbstractBoolParser]
    ) -> None:
        self._io_handler = io_handler
        self._BoolParserClass = BoolParserClass
        self._event_callback = None

        self._run_thread = threading.Thread(target=self._run,daemon=True)
        self._running_thread_flag     = threading.Event()
        self._step_execution_finished = threading.Event()
        self._step_execution_finished.set()


        self._run_thread.start()


    def reset_timers(self):
        self._step_execution_finished.wait()
        self._transitions_collection.reset_timers()

    def set_event_callback(self,event_callback):
        self._event_callback = event_callback

    def setup(self,petri_net_json_structure):  
        self._running_thread_flag.clear()
        self._step_execution_finished.wait()


        self._places:dict[str,Place] = dict()
        transitions:dict[str,InstantaneousTransition|TimedTransition] = dict()

        self._io_handler.set_marking_to_output_expressions(petri_net_json_structure["marking_to_output_expressions"],self._BoolParserClass)  
        for place in petri_net_json_structure["places"]:
            self._places[place["id"]] = Place(id=place["id"],capacity=place["capacity"],marking=place["initial_marking"])
        for instantaneous_transition in petri_net_json_structure["instantaneous_transitions"]:
            transitions[instantaneous_transition["id"]] = InstantaneousTransition(
                id = instantaneous_transition["id"],
                rate = instantaneous_transition["rate"],
                priority=instantaneous_transition["priority"],
                signal_enabling_expression=instantaneous_transition["signal_enabling_expression"],
                io_handler= self._io_handler,
                BoolParserClass=self._BoolParserClass,
            )
        for timed_transition in petri_net_json_structure["timed_transitions"]:
            transitions[timed_transition["id"]] = TimedTransition(
                id = timed_transition["id"],
                rate = timed_transition["rate"],
                priority=timed_transition["priority"],
                signal_enabling_expression=timed_transition["signal_enabling_expression"],
                timer_sec=timed_transition["timer_sec"],
                io_handler= self._io_handler,
                BoolParserClass=self._BoolParserClass,
            )
        self._transitions_collection = TransitionsCollection(transitions=list(transitions.values()),io_handler=self._io_handler)
        
        for arc in petri_net_json_structure["arcs"]:
            source_node = self._places.get(arc["source"]) or transitions[(arc["source"])] 
            target_node = self._places.get(arc["target"]) or transitions[(arc["target"])] 
            Arc(id = arc["id"],
                source_node=source_node,
                target_node=target_node,
                weight=arc["weight"],
                is_inhibitor= arc["type"] == "inhibitor"
            )
        self._io_handler.update_outputs(self._places)

    @property
    def running_flag(self):
        return self._running_thread_flag.is_set()

    @running_flag.setter
    def running_flag(self,flag:bool):
        if flag:
            self._running_thread_flag.set()
        else:
            self._running_thread_flag.clear()

    def _run(self):
        try:
            while True:
                self._running_thread_flag.wait()
                self._step()
                sleep(0.001)
        except Exception as e:
            thread_error_queue.put(e)

    def _step(self):
        self._step_execution_finished.clear()
        try:
            transition_chosen_to_fire = self._transitions_collection.get_transition_chosen_to_fire()
            if transition_chosen_to_fire is not None:
                transition_chosen_to_fire.fire()
                self._io_handler.update_outputs(self._places)

                for place in self._places.values():
                    if place.marking != place.initial_marking:
                        return
                self._event_callback(self.__class__.Events.cycleFinished)

        except PetriNetDeadlockError:
            self._event_callback(self.__class__.Events.deadLock)
        finally:
            self._step_execution_finished.set()
