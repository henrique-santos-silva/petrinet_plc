import os
from typing import Type
from copy import deepcopy
from src import BASE_DIR,thread_error_queue
from threading import Thread
from flask_socketio import SocketIO
from flask import Flask,send_from_directory
from src.abstract.abstract_io_handler import AbstractIOHandler
from src.abstract.abstract_bool_parser import AbstractBoolParser
from src.abstract.abstract_petri_net_subcomponents import AbstractPetriNetPlace

class IOWebMocker(AbstractIOHandler):
    # _template_dir = 
    def __init__(self,
                 digital_inputs:dict[str,bool]|None = None,
                 digital_outputs:dict[str,bool]|None = None,
                 web_mock:bool = False
                 ) -> None:
        super().__init__()
        self._output_boolean_functions = None
        self._digital_inputs  = digital_inputs or dict()
        self._previous_digital_inputs  =  deepcopy(self._digital_inputs)
        self._digital_outputs = digital_outputs or dict()
        
        if web_mock:
            self._server_started = False
            Thread(target=self._run_website,daemon=True).start()
            while not self._server_started: 
                pass

    @property
    def has_been_updated(self) -> bool:
        has_been_updated:bool =  (self._digital_inputs != self._previous_digital_inputs)
        self._previous_digital_inputs = deepcopy(self._digital_inputs)
        return has_been_updated


    def set_marking_to_output_expressions(self,
                                        marking_to_output_expressions: dict[str, str],
                                        BoolParserClass:Type[AbstractBoolParser]
        ) -> None:
        self._output_boolean_functions = dict()
        for output,marking_to_output_expression in marking_to_output_expressions.items():
            self._output_boolean_functions[output] = BoolParserClass(marking_to_output_expression).generate_function()
        
    def update_outputs(self,places:dict[str,AbstractPetriNetPlace]) -> None:
        places_bool = {id:_places.marking>0 for id,_places in places.items()}
        assert(self._output_boolean_functions is not None)
        for output, output_bool_function in self._output_boolean_functions.items():
            self._digital_outputs[output] = output_bool_function(**places_bool)

    def clear(self):
        self._output_boolean_functions = None
        for key in self._digital_outputs.keys():
            self._digital_outputs[key] = False
        
        
    def get_all(self):
        return {"digital_inputs":self._digital_inputs,"digital_outputs":self._digital_outputs}

    def _run_website(self):
        try:
            
            app = Flask(__name__,static_folder=os.path.join(BASE_DIR, 'src/implementation/IOWebMocker_static'))
            socketio = SocketIO(app,async_mode="threading")
            self._socketio=socketio

            @app.route("/")
            def index():
                return app.send_static_file("index.html")
                return send_from_directory('IOWebMocker_static', 'index.html')
            

            @socketio.on("input_update")
            def handle_input_update(data):
                for input_id,val in data.items():
                    self._digital_inputs[input_id] = val

                socketio.emit("inputs_update",data)

            self._server_started=True    
            socketio.run(app,debug=False,allow_unsafe_werkzeug=True,host="::",port=50001)
        
        except Exception as e:
            print("erro:",e)
            thread_error_queue.put(e)
        