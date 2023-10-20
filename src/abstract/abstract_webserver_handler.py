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
    def post_state(self,state):
        raise NotImplementedError