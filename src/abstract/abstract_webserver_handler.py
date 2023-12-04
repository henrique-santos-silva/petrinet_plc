from src.abstract.abstract_state_machine import AbstractStateMachine
from src.abstract.abstract_petri_net_subcomponents import AbstractPetriNetPlace, AbstractPetriNetTransitionsCollection,AbstractPetriNetTransition
from abc import ABC,abstractmethod
from enum import Enum, auto

class AbstractWebServerHandler(ABC):
    class Events(Enum):
        petriNetFilesUploaded = auto()
        startExecution = auto()
        pauseExecution = auto()
        resumeExecution = auto()
        finishExecutionAfterCycle = auto()
        finishExecutionImmediately = auto()
        physicalIOHandlerSelected = auto()
        emulatorIOHandlerSelected = auto()



    @abstractmethod
    def set_event_callback(self,event_callback):
        raise NotImplementedError
        
    @abstractmethod
    def check_petri_net_files_existence(self) -> bool:
        raise NotImplementedError
    
    @abstractmethod
    def get_file(self) -> dict:
        raise NotImplementedError
    
    @abstractmethod
    def post_IOs(self,IOs:dict):
        raise NotImplementedError
    
    @abstractmethod
    def post_state(self,state:AbstractStateMachine.States):
        raise NotImplementedError
    
    @abstractmethod
    def post_current_io_module(self,is_physical:bool=None,is_physical_enabled:bool=None):
        raise NotImplementedError
    
    @abstractmethod
    def post_current_petrinet_debugging_info(
        self,
        places:dict[str,AbstractPetriNetPlace],
        transition_collection:AbstractPetriNetTransitionsCollection,
        fired_transition:AbstractPetriNetTransition|None = None
    ):
        raise NotImplementedError
    