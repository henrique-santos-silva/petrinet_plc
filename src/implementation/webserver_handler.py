import json
import os
from src import BASE_DIR,thread_error_queue
from pathlib import Path
from copy import deepcopy
from threading import Thread
from flask import Flask,send_file
from flask_socketio import SocketIO, emit
from flask_cors import CORS

from src.abstract.abstract_webserver_handler import AbstractWebServerHandler
from src.abstract.abstract_state_machine import AbstractStateMachine
from src.abstract.abstract_petri_net_subcomponents import AbstractPetriNetPlace, AbstractPetriNetTransitionsCollection,AbstractPetriNetTransition

class LocalWebServer(AbstractWebServerHandler):
    def __init__(self):
        self._command_dictionary ={
            'btn-start'     : LocalWebServer.Events.startExecution,
            'btn-pause'     : LocalWebServer.Events.pauseExecution,
            'btn-resume'    : LocalWebServer.Events.resumeExecution,
            'btn-finish'    : LocalWebServer.Events.finishExecutionAfterCycle,
            'btn-finish_now': LocalWebServer.Events.finishExecutionImmediately,
            'FileUploaded'  : LocalWebServer.Events.petriNetFilesUploaded,
            'io_handler_physical':LocalWebServer.Events.physicalIOHandlerSelected,
            'io_handler_emulator':LocalWebServer.Events.emulatorIOHandlerSelected
        }
        self._server_started = False

        self._current_state = None
        self._current_io = None
        self._current_places_marking = None
        self._current_transitions_enabling_state = None
        self._event_callback = None
        
        self._is_physical_io_module = True
        self._is_physical_io_module_enabled = True

        webserver_ihm_uploaded_IOPT_path = os.path.join(BASE_DIR, "webserver_ihm_uploaded_IOPT") 
        if not os.path.exists(webserver_ihm_uploaded_IOPT_path):
            os.makedirs(webserver_ihm_uploaded_IOPT_path)

        self._IOPT_PATH = os.path.join(webserver_ihm_uploaded_IOPT_path, "IOPT.json")

        Thread(target=self._run_website,daemon=True).start()
        while not self._server_started:
            pass
        
    def set_event_callback(self,event_callback):
        self._event_callback = event_callback
    
    def check_petri_net_files_existence(self):
        IOPT   = Path(self._IOPT_PATH)
        return IOPT.is_file()

    def get_file(self):
        with open(self._IOPT_PATH) as f:
            PNML = json.load(f)
            return (PNML)
        
    def post_IOs(self,IOs:dict):
        if not(IOs == self._current_io):
            self._current_io = deepcopy(IOs)
            self._socketio.emit("IO_update",IOs)
    
    def post_current_io_module(self,is_physical:bool=None,is_physical_enabled:bool=None):
        if is_physical is not None:
            self._is_physical_io_module = is_physical
        if is_physical_enabled is not None:
            self._is_physical_io_module_enabled = is_physical_enabled

        self._socketio.emit(
            "io_module_selected",
            {
                "is_physical_io_module":self._is_physical_io_module,
                "is_physical_io_module_enabled":self._is_physical_io_module_enabled
            }
        )
    
    def post_current_petrinet_debugging_info(
        self,
        places:dict[str,AbstractPetriNetPlace],
        transition_collection:AbstractPetriNetTransitionsCollection,
        fired_transition:AbstractPetriNetTransition|None = None
    ):
        transitions_enabling_state = {
            transition.id:{
                "is_petri_enabled":transition._is_petri_enabled_val,
                "is_signal_enabled":transition._is_signal_enabled_val
            } for transition in transition_collection
        }

        if fired_transition is not None:
            self._current_places_marking = {place_id:place.marking for place_id,place in places.items()}
            self._current_transitions_enabling_state = transitions_enabling_state
            
            self._socketio.emit(
                "petrinet_debugging_info",
                {
                    "places_marking":self._current_places_marking,
                    "transitions_enabling_state":self._current_transitions_enabling_state,
                    "fired_transition":fired_transition.id
                }
            )
        else:
            if transitions_enabling_state != self._current_transitions_enabling_state:
                self._current_transitions_enabling_state = transitions_enabling_state
                self._socketio.emit(
                    "petrinet_debugging_info",
                    {
                        "transitions_enabling_state":self._current_transitions_enabling_state,
                    }
                )

        

    def post_state(self,state:AbstractStateMachine.States):
        if state != self._current_state:
            self._socketio.emit("stateMachine_state_update",state.name)
            self._current_state = state

    def _run_website(self):
        try:
            app = Flask(__name__,static_url_path="/static",static_folder=os.path.join(BASE_DIR, 'src/implementation/webserver_ihm_static'))
            socketio = SocketIO(app,async_mode='threading', cors_allowed_origins="*")
            cors = CORS(app, resources={r"/socket.io/*": {"origins": "*"}})
            self._socketio = socketio

            @app.route('/',methods=["GET"])
            def index():
                return app.send_static_file("index.html")
            
            @app.route('/debug',methods=["GET"])
            def petri_net_live_view():
                return app.send_static_file("petri_net_live_view.html")
            
            @app.route('/api/getFile/IOPT.json',methods=["GET"])
            def get_file():
                return send_file(path_or_file= Path(self._IOPT_PATH).absolute(),as_attachment=True)
            
            @socketio.on("connect")
            def handle_new_connection():            
                if self._current_state is not None:
                    emit("stateMachine_state_update",self._current_state.name)
                if self._current_io is not None:
                    emit("IO_update",self._current_io)
                self.post_current_io_module()

                with open(self._IOPT_PATH) as f:
                    iopt_dict = json.load(f)
                    emit('petrinet_json_update',iopt_dict)
                
                self._socketio.emit(
                    "petrinet_debugging_info",
                    {
                        "places_marking":self._current_places_marking,
                        "transitions_enabling_state":self._current_transitions_enabling_state,
                        "fired_transition":None
                    }
                )
                
            @socketio.on("IOPT_update")
            def IOPT_update(new_IOPT):
                with open(self._IOPT_PATH,'w') as f:
                    iopt_dict = json.loads(new_IOPT)
                    f.write(json.dumps(iopt_dict,indent=4))
                    emit('petrinet_json_update',iopt_dict,broadcast=True)

                    self._current_places_marking = None 
                    self._current_transitions_enabling_state = None 
                    
                
            @socketio.on("stateMachine_event_update")
            def relay_stateMachine_event_update(button_pressed_id:str):
                new_client_event = self._command_dictionary[button_pressed_id]
                self._event_callback(new_client_event)

            self._server_started = True
            socketio.run(app,debug=False,allow_unsafe_werkzeug=True,host = '::',port=50000)
        except Exception as e:
            thread_error_queue.put(e)
