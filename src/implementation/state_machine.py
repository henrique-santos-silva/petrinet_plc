from queue import SimpleQueue
from enum import Enum, auto
from src import thread_error_queue
from src.abstract.abstract_state_machine import AbstractStateMachine

from src.abstract.abstract_petri_net_handler import AbstractPetriNetHandler
from src.abstract.abstract_webserver_handler import AbstractWebServerHandler
from src.abstract.abstract_io_handler import AbstractIOHandler
from collections.abc import Callable
from time import sleep

class StateMachine(AbstractStateMachine):

    def __init__(self,
                 petrinet_handler:AbstractPetriNetHandler,
                 webserver_handler: AbstractWebServerHandler,
                 io_handler : AbstractIOHandler,
                ) -> None:
        S = StateMachine.States
        A = StateMachine.Actions
        IE = StateMachine.InternalEvents

        self._petrinet_handler = petrinet_handler
        self._webserver_handler = webserver_handler
        self._io_handler = io_handler
        
        PetriNetEvents = self._petrinet_handler.Events
        WebServerEvents = self._webserver_handler.Events
            
        self._webserver_event = None
        self._petrinet_handler_event = None

        self._state:S = StateMachine.States.INIT
        self._internal_event:IE = StateMachine.InternalEvents.INIT

        self._webserver_handler.set_event_callback(self._set_webserver_event)
        self._petrinet_handler.set_event_callback(self._set_petri_net_event)

        self._state_machine_dictionary:dict[S,dict[IE|PetriNetEvents|WebServerEvents,tuple[S,A]]] = {
            S.INIT : {
                IE.INIT :                       (S.CheckingPetriNetFilesExistence , A.CheckPetriNetFilesExistence)
            },
            S.CheckingPetriNetFilesExistence:{
                IE.filesNotUploadedYet:         (S.WaitingPetriNetFilesUpload     , A.DoNothing),
                IE.filesAlreadyUploaded:        (S.PetriNetFilesUploaded          , A.DoNothing)
            },
            S.WaitingPetriNetFilesUpload:{
                WebServerEvents.petriNetFilesUploaded:      (S.PetriNetFilesUploaded        , A.DoNothing),
            },
            S.PetriNetFilesUploaded:{
                WebServerEvents.startExecution:             (S.Running                      , A.StartExecution)
            },
            S.Running: {
                # IE.NONE:                                    (S.Running                      , A.PetriNetStep),
                PetriNetEvents.deadLock:                    (S.DeadLock                     , A.DoNothing),
                # PetriNetEvents.cycleFinished:               (S.Running                      , A.PetriNetStep),
                WebServerEvents.pauseExecution:             (S.Paused                       , A.PauseExecution),
                WebServerEvents.finishExecutionAfterCycle:  (S.WaitingEndOfCycle            , A.DoNothing),
                WebServerEvents.finishExecutionImmediately: (S.PetriNetFilesUploaded        , A.FinishExecution)
            },
            S.DeadLock:{
                WebServerEvents.finishExecutionImmediately: (S.PetriNetFilesUploaded        ,A.FinishExecution)
            },
            S.Paused:{
                WebServerEvents.resumeExecution:            (S.Running                      , A.ResumeExecution),
                WebServerEvents.finishExecutionImmediately: (S.PetriNetFilesUploaded        , A.FinishExecution)
            },
            S.WaitingEndOfCycle:{
                # IE.NONE:                                    (S.WaitingEndOfCycle            , A.PetriNetStep),
                PetriNetEvents.cycleFinished:               (S.PetriNetFilesUploaded        , A.FinishExecution),
                WebServerEvents.finishExecutionImmediately: (S.PetriNetFilesUploaded        , A.FinishExecution)
            }
        }
    
    def _set_petri_net_event(self,event:AbstractPetriNetHandler.Events):
        self._petrinet_handler_event = event
    
    def _set_webserver_event(self,event:AbstractWebServerHandler.Events):
        self._webserver_event = event

    def _get_event(self)->AbstractStateMachine.InternalEvents|AbstractPetriNetHandler.Events|AbstractWebServerHandler.Events:
        if self._internal_event is not StateMachine.InternalEvents.NONE:
            return self._internal_event
        
        if self._webserver_event is not None:
            event =  self._webserver_event
            self._webserver_event = None
            return event
        
        if self._petrinet_handler_event is not None:
            event = self._petrinet_handler_event
            self._petrinet_handler_event = None
            return event
        
        return StateMachine.InternalEvents.NONE


    def _exec_action(self,action:AbstractStateMachine.Actions) -> None:

        def exec_CheckPetriNetFilesExistence():
            if self._webserver_handler.check_petri_net_files_existence():
                return StateMachine.InternalEvents.filesAlreadyUploaded
            else:
                return StateMachine.InternalEvents.filesNotUploadedYet

        def exec_PetriNetStart():
            IOPT = self._webserver_handler.get_file()
            self._petrinet_handler.setup(IOPT)
            self._petrinet_handler.running_flag = True

        def exec_PetriNetPause():
            self._petrinet_handler.running_flag = False
            self._petrinet_handler.reset_timers()

        def exec_PetriNetResume():
            self._petrinet_handler.running_flag = True
        
        def exec_PetriNetFinishExecution():
            self._petrinet_handler.running_flag = False
            self._io_handler.clear()

            

        
        Actions = StateMachine.Actions
        switch_case_dict:dict[Actions,Callable[...,None|StateMachine.InternalEvents]] = {
            Actions.CheckPetriNetFilesExistence: exec_CheckPetriNetFilesExistence,
            Actions.DoNothing:       lambda:None,
            Actions.StartExecution:  exec_PetriNetStart,
            Actions.PauseExecution:  exec_PetriNetPause,
            Actions.ResumeExecution: exec_PetriNetResume,
            Actions.FinishExecution: exec_PetriNetFinishExecution
        }

        self._internal_event = switch_case_dict[action]() or StateMachine.InternalEvents.NONE
            
    def run(self):
        print("Máquina de estados inicializada")
        while True:
            sleep(0.05)

            event = self._get_event()

            self._state, action = self._state_machine_dictionary[self._state].get(
                event,
                (self._state,StateMachine.Actions.DoNothing)
            ) 
            # print(event.name,self._state.name,action.name)
            self._exec_action(action)
            # print(self._events_queue.qsize())
            self._webserver_handler.post_state(self._state)
            self._webserver_handler.post_IOs(self._io_handler.get_all())

            if not thread_error_queue.empty():
                error = thread_error_queue.get()
                print(error,'state machine')
                raise error