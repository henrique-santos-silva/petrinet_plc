$(document).ready(function (){
    var socket = io.connect('http://' + document.domain + ':' + location.port);
    
    socket.on('connect', function() {
        socket.send('Connected!');
        $("#disconnected").hide()
    });

    socket.on('IO_update', function(new_IO_state) {
        console.group("IO_update")
        console.log(new_IO_state)
        console.groupEnd()
        
        for (const [key, value] of Object.entries(new_IO_state["digital_inputs"])) {
            $('#' + key).attr('class', value ? 'led green' : 'led red');
        }
        for (const [key, value] of Object.entries(new_IO_state["digital_outputs"])) {
            $('#' + key).attr('class', value ? 'led green' : 'led red');
        }
    });

    socket.on('stateMachine_state_update', function(new_state) {

        console.log(`new state ${new_state}`)      
        
        let _ =[
            "CheckingPetriNetFilesExistence",
            "WaitingPetriNetFilesUpload"
        ].includes(new_state) ? $("#user_command_buttons").hide() : $("#user_command_buttons").show()
        
        _ =[
            "CheckingPetriNetFilesExistence",
            "WaitingPetriNetFilesUpload"
        ].includes(new_state) ? $("#IO_monitor").hide() : $("#IO_monitor").show()

        _ = [
            "Running",
            "Paused",
            "WaitingEndOfCycle",
            "DeadLock"
        ].includes(new_state) ? $("#new_file").hide() : $("#new_file").show()

        let _is_io_module_disabled = new_state !== "PetriNetFilesUploaded";
        $('#io-module-selector').prop('disabled',_is_io_module_disabled)
        $('#io-module-selector').parent().toggleClass('disabled',_is_io_module_disabled)
        if (_is_io_module_disabled) {
            $('#io-module-selector').addClass('disabled');
        } else {
            $('#io-module-selector').removeClass('disabled');
        }
        
        $("#IOPT_config").hide() 

        _ = [
            "CheckingPetriNetFilesExistence",
            "WaitingPetriNetFilesUpload",
        ].includes(new_state) ? $("#btn-download_iopt_from_server").hide() : $("#btn-download_iopt_from_server").show()
        
        $('#btn-start').prop('disabled',new_state != "PetriNetFilesUploaded")
        $('#btn-pause').prop('disabled',new_state != "Running")
        $('#btn-resume').prop('disabled',new_state != "Paused")
        $('#btn-finish').prop('disabled',new_state != "Running")
        $('#btn-finish_now').prop('disabled',[
            "CheckingPetriNetFilesExistence",
            "WaitingPetriNetFilesUpload",
            "PetriNetFilesUploaded"
        ].includes(new_state))

        if (new_state == "DeadLock"){
            alert("A Rede de Petri está em Deadlock! Finalize a execução e revise a RdP")
        }
    });
    


    $('#io-module-selector').parent().on('change',function(){
        if ($(this).hasClass('off')){
            socket.emit("stateMachine_event_update",'io_handler_emulator')
        }else{
            socket.emit("stateMachine_event_update",'io_handler_physical')
        }
    })


    $('button').click(
        function(){
            const IOPT_dictionary = JSON.parse(localStorage.getItem("IOPT_dictionary"));
            if ($(this).attr('id') == "btn-try_to_send_iopt_config"){
                console.log("if ($(this).attr('id') == 'btn-try_to_send_iopt_config')")
                if(is_form_valid(IOPT_dictionary)){
                    console.log("if(is_form_valid(IOPT_dictionary))")
            
                    socket.emit('stateMachine_event_update','FileUploaded')
                    socket.emit("IOPT_update",JSON.stringify(IOPT_dictionary))
                    localStorage.setItem("IOPT_dictionary", JSON.stringify(IOPT_dictionary))
                    $("#petrinet_json_file").val('')
                    $("#petrinet_xml_file").val('')
                    console.log(IOPT_dictionary)
   
                    localStorage.removeItem('IOPT_dictionary');
                    $("#user_command_buttons").show()
                    $("#IO_monitor").show()
                    $("#IOPT_config").hide()
                }else{
                    alert("campos inválidos")
                }
            }else if($(this).attr('id') == "btn-cancel_iopt_config"){
                $("#petrinet_json_file").val('')
                $("#petrinet_xml_file").val('')
                localStorage.removeItem('IOPT_dictionary');
                $("#IOPT_config").hide()
                $("#user_command_buttons").show()
                $("#IO_monitor").show()

            }else{
                socket.emit('stateMachine_event_update',$(this).attr('id'))
            }
        }
    );
    
    $("#petrinet_xml_file").on("change",function(event){
        const fileInput = event.target;
        const file = fileInput.files[0];

        petrinet_xml2json(file)
        .then((IOPT_dictionary) => {
            localStorage.setItem("IOPT_dictionary", JSON.stringify(IOPT_dictionary))
            generate_IOPT_config_div(
                IOPT_dictionary,
                loaded_from_json = false,
                inputs_name_list = [...Array(8).keys()].map(i => `DI${i}`),
                outputs_name_list = [...Array(16).keys()].map(i => `DO${i}`),
            )
            
            apply_popover_to_inputs(
                inputs = [...Array(8).keys()].map(i => `DI${i}`),
                places = IOPT_dictionary.places.map(place => place.id)
            )

            console.log(IOPT_dictionary)
            $("#user_command_buttons").hide()
            $("#IO_monitor").hide()            
          })
          .catch((error) => {
            console.error("Erro ao processar o arquivo:", error);
           });

    })

    $("#petrinet_json_file").on("change",function(event){
        const fileInput = event.target;
        const file = fileInput.files[0];

        petrinet_load_json(file)
        .then((IOPT_dictionary) => {
            localStorage.setItem("IOPT_dictionary", JSON.stringify(IOPT_dictionary))
            generate_IOPT_config_div(
                IOPT_dictionary,
                loaded_from_json = true,
                inputs_name_list = [...Array(8).keys()].map(i => `DI${i}`),
                outputs_name_list = [...Array(16).keys()].map(i => `DO${i}`),
            )
            
            apply_popover_to_inputs(
                inputs = [...Array(8).keys()].map(i => `DI${i}`),
                places = IOPT_dictionary.places.map(place => place.id)
            )
            console.log(IOPT_dictionary)
            $("#user_command_buttons").hide()
            $("#IO_monitor").hide()
          })
          .catch((error) => {
            console.error("Erro ao processar o arquivo:", error);
           });
    })

    socket.on('message', function(data) {
        console.log(data);
    });
    socket.on('disconnect', function(data) {
        $("#user_command_buttons").hide()
        $("#IO_monitor").hide()
        $("#new_file").hide()
        $("#disconnected").show()        
    });  
})


