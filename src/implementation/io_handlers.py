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


class PDR0004_IOHandler(AbstractIOHandler):
    
    PCF_ADDRESS_RELAYS                  = 0x25
    PCF_ADDRESS_OPTO_ISOLATED_OUTPUTS   = 0x26
    PCF_ADDRESS_OPTO_ISOLATED_INPUTS    = 0x27
    
    def __init__(self) -> None:
        self._output_boolean_functions = None
        self._digital_outputs = {f"DO{i}":False for i in range(16)}
        self._digital_inputs  = {f"DI{i}":False for i in range(8)}
        self._previous_digital_inputs  =  deepcopy(self._digital_inputs)
        self.enabled = True

        try:
            import smbus
            self.bus = smbus.SMBus(1)
            self.clear()
            self.get_all()
        except Exception as e:
            self.enabled = False


    def _generate_bytes_from_bits(self,bits):
        if len(bits) % 8 != 0:
            raise ValueError("The number of bits must be a multiple of 8")

        bytes_list = []
        byte_value = 0
        for i, bit in enumerate(bits):
            byte_value = (byte_value << 1) | bit
            if (i + 1) % 8 == 0:
                bytes_list.append(byte_value)
                byte_value = 0

        return bytes_list
    
    def _generate_bits_from_byte(self,byte):
        if byte < 0 or byte > 255:
            raise ValueError("Byte value must be in the range 0-255")

        bits_list = []
        for _ in range(8):
            bits_list.append(bool(byte & 1))
            byte >>= 1

        return bits_list
    
    # def _set_relay_output(self,id:int|str,val=bool):
    #     if isinstance(id,int):
    #         id = f"DO{id}"
        
    #     self._digital_outputs[id] = val

    #     relay_output_byte,opto_isolated_output_byte = self._generate_bytes_from_bits([not bit for bit in self._digital_outputs.values()])

    #     self.bus.write_byte(self.PCF_ADDRESS_RELAYS, relay_output_byte)

    @property
    def has_been_updated(self) -> bool:
        self._update_inputs()
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
        
        opto_isolated_output_byte, relay_output_byte = self._generate_bytes_from_bits([not bit for bit in self._digital_outputs.values()])
        self.bus.write_byte(self.PCF_ADDRESS_RELAYS,                 relay_output_byte)
        self.bus.write_byte(self.PCF_ADDRESS_OPTO_ISOLATED_OUTPUTS,  opto_isolated_output_byte)    

    def _update_inputs(self):
        read_byte = self.bus.read_byte(self.PCF_ADDRESS_OPTO_ISOLATED_INPUTS)
        bits:list[bool] = self._generate_bits_from_byte(read_byte)
        for i in range(8):
            self._digital_inputs[f"DI{i}"] = not bits[i] 
        

    def clear(self):
        if self.enabled:
            self._output_boolean_functions = None
            for key in self._digital_outputs.keys():
                self._digital_outputs[key] = False
            self.bus.write_byte(self.PCF_ADDRESS_RELAYS, 0xFF)
            self.bus.write_byte(self.PCF_ADDRESS_OPTO_ISOLATED_OUTPUTS,  0xFF) 
                   
    def __del__(self):
        self.bus.write_byte(self.PCF_ADDRESS_RELAYS, 0xFF)

        
        
    def get_all(self):
        self._update_inputs()
        return {"digital_inputs":self._digital_inputs,"digital_outputs":self._digital_outputs}


class IOHandlersWrapper(AbstractIOHandler):
    def __init__(self,io_handler_emulator:AbstractIOHandler,io_handler_physical:AbstractIOHandler) -> None:
        self._io_handler_emulator = io_handler_emulator
        self._io_handler_physical = io_handler_physical
        self.select_io_handler_physical()
    
    def select_io_handler_emulator(self):
        self._io_handler = self._io_handler_emulator

    def select_io_handler_physical(self):
        if self._io_handler_physical.enabled:
            self._io_handler = self._io_handler_physical
        else:
            self._io_handler = self._io_handler_emulator



    @property
    def has_been_updated(self) -> bool:
        return self._io_handler.has_been_updated
    
    def set_marking_to_output_expressions(self, marking_to_output_expressions: dict[str, str], BoolParserClass: type[AbstractBoolParser]) -> None:
        return self._io_handler.set_marking_to_output_expressions(marking_to_output_expressions, BoolParserClass)
    
    def update_outputs(self, places: dict[str, AbstractPetriNetPlace]) -> dict[str, dict[str, bool]]:
        return self._io_handler.update_outputs(places)
    
    def clear(self):
        self._io_handler_emulator.clear()
        self._io_handler_physical.clear()
    
    def get_all(self) -> dict[str, dict[str, bool]]:
        return self._io_handler.get_all()

class IOWebMocker(AbstractIOHandler):
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
        
