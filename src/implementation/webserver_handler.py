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
from src.abstract.abstract_state_machine import AbstractStateMachine

class LocalWebServer(AbstractWebServerHandler):
    def __init__(self):
        self._command_dictionary ={
            'btn-start'     : LocalWebServer.Events.startExecution,
            'btn-pause'     : LocalWebServer.Events.pauseExecution,
            'btn-resume'    : LocalWebServer.Events.resumeExecution,
            'btn-finish'    : LocalWebServer.Events.finishExecutionAfterCycle,
            'btn-finish_now': LocalWebServer.Events.finishExecutionImmediately,
            'FileUploaded'  : LocalWebServer.Events.petriNetFilesUploaded
        }
        self._server_started = False

        self._current_state = None
        self._current_io = None
        self._event_callback = None

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
            
            @app.route('/api/getFile/IOPT.json',methods=["GET"])
            def get_file():
                return send_file(path_or_file= Path(self._IOPT_PATH).absolute(),as_attachment=True)
            
            @socketio.on("connect")
            def handle_new_connection():            
                if self._current_state is not None:
                    emit("stateMachine_state_update",self._current_state.name)
                if self._current_io is not None:
                    emit("IO_update",self._current_io) 
                
            @socketio.on("IOPT_update")
            def IOPT_update(new_IOPT):
                with open(self._IOPT_PATH,'w') as f:
                    f.write(json.dumps(json.loads(new_IOPT),indent=4))
                
            @socketio.on("stateMachine_event_update")
            def relay_stateMachine_event_update(button_pressed_id:str):
                new_client_event = self._command_dictionary[button_pressed_id]
                self._event_callback(new_client_event)

            self._server_started = True
            socketio.run(app,debug=False,allow_unsafe_werkzeug=True,host = '::',port=50000)
        except Exception as e:
            thread_error_queue.put(e)
