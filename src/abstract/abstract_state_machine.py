from abc import ABC,abstractmethod
from enum import Enum,auto

class AbstractStateMachine(ABC):
    class InternalEvents(Enum):
        NONE = 0
        INIT = auto()
        filesAlreadyUploaded = auto()
        filesNotUploadedYet = auto()

    class States(Enum):
        INIT = 0
        CheckingPetriNetFilesExistence = auto()
        WaitingPetriNetFilesUpload = auto()
        PetriNetFilesUploaded = auto()
        Running = auto()
        DeadLock = auto()
        Paused = auto()
        WaitingEndOfCycle = auto()
    
    class Actions(Enum):
        DoNothing = 0
        CheckPetriNetFilesExistence =auto()
        
        AlertDeadLock = auto()
        StartExecution = auto()
        PauseExecution = auto()
        ResumeExecution = auto()
        FinishExecution = auto()

    @abstractmethod
    def run(self):
        raise NotImplementedError