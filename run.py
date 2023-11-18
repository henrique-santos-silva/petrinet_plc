try:
    from src.implementation.webserver_handler import LocalWebServer
    from src.implementation.io_handlers import IOWebMocker
    from src.implementation.petri_net_handler import PetriNetHandler
    from src.implementation.boolParser import BoolParser
    from src.implementation.state_machine import StateMachine
    import logging


    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    # print("https://example.com/")
    webserver_handler = LocalWebServer()
    io_handler= IOWebMocker(
        digital_inputs= {f"DI{i}":False for i in range(8)},
        digital_outputs={f"DO{i}":False for i in range(16)},
        web_mock=True
    )
    petrinet_handler = PetriNetHandler(io_handler,BoolParser)

    state_machine = StateMachine(petrinet_handler,webserver_handler,io_handler)
    state_machine.run()
except KeyboardInterrupt:
    print("\nKeyboardInterrupt\nFinalizando a execução")
except Exception as e:
    with open("petrinetplcerror.log","a") as f:
        f.write(str(e))
        f.write("\n")
        raise e