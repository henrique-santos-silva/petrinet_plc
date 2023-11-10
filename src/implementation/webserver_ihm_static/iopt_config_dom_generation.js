function petrinet_xml2json(file) {
    return new Promise((resolve, reject) => {
      if (file) {
        const IOPT_dictionary = {
          "places": [],
          "instantaneous_transitions": [],
          "timed_transitions": [],
          "arcs": []
        };
        const reader = new FileReader();
  
        reader.onload = function (e) {
            const fileContent = e.target.result;

            // Parse the XML content
            const parser = new DOMParser();
            const xmlDoc = parser.parseFromString(fileContent, "text/xml");

            // Access all the place elements
            const placeElements = xmlDoc.querySelectorAll("place");
            placeElements.forEach((placeElement, index) => {
                const id = placeElement.getAttribute("id");
                const initial_marking = parseInt(placeElement.querySelector("initialMarking").querySelector("value").textContent.split(',')[1]); 
                const capacity = parseInt(placeElement.querySelector("capacity").querySelector("value").textContent);
                IOPT_dictionary['places'].push({id,initial_marking,capacity})
                
                console.log(`Place ${index + 1}: id - ${id}, initial_marking - ${initial_marking}, capacity - ${capacity}`);
            });

            const transitionElements = xmlDoc.querySelectorAll("transition");
            transitionElements.forEach((transitionElement, index) => {
                const id = transitionElement.getAttribute("id");
                const rate = parseFloat(transitionElement.querySelector("rate").querySelector("value").textContent); 
                const priority = parseInt(transitionElement.querySelector("priority").querySelector("value").textContent);
                const timed = transitionElement.querySelector("timed").querySelector("value").textContent == 'true';
                
                IOPT_dictionary[timed?'timed_transitions':'instantaneous_transitions'].push({id,rate,priority})
            });

            const arcElements = xmlDoc.querySelectorAll("arc");
            arcElements.forEach((arcElement, index) => {
                const id = arcElement.getAttribute("id");
                const source = arcElement.getAttribute("source");
                const target = arcElement.getAttribute("target");
                const weight = parseInt(arcElement.querySelector("inscription").querySelector("value").textContent.split(',')[1]);
                const type = arcElement.querySelector("type").getAttribute("value");
                IOPT_dictionary['arcs'].push({id,source,target,weight,type})
            });
            resolve(IOPT_dictionary);
        };
  
        reader.onerror = function (error) {
          reject(error);
        };
  
        reader.readAsText(file);

      } else {
        reject(new Error("Nenhum arquivo fornecido."));
      }
    });
  }

  function petrinet_load_json(file) {
    return new Promise((resolve, reject) => {
      if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            const fileContent = e.target.result;
            let IOPT_dictionary
            try {
              // Parse the JSON data into a JavaScript object
              IOPT_dictionary = JSON.parse(e.target.result);
            } catch (error) {
                console.error("Error parsing JSON:", error);
            }
            resolve(IOPT_dictionary);
        };
  
        reader.onerror = function (error) {
          reject(error);
        };
  
        reader.readAsText(file);

      } else {
        reject(new Error("Nenhum arquivo fornecido."));
      }
    });
  }

  

function generate_IOPT_config_div(IOPT_dictionary,loaded_from_json){
    // -------------- Input to Transitons-------------------------------------------------------------
    const transition_signal_enabling_condition_Container = document.getElementById('transition_signal_enabling_condition_container');

    transition_signal_enabling_condition_Container.textContent=""
    let transitions = [...IOPT_dictionary["instantaneous_transitions"],...IOPT_dictionary["timed_transitions"]]
    transitions.forEach((transition,index)=>{

      const transitionName = transition["id"]
      const outerDiv = document.createElement('div');
      outerDiv.classList.add('row', 'my-1');
    
      // Cria a coluna para o label
      const labelCol = document.createElement('div');
      labelCol.classList.add('col-md-3', 'd-flex', 'align-items-center');
    
      // Cria a etiqueta <label>
      const label = document.createElement('label');
      label.classList.add('form-label');
      label.setAttribute('for', `transition_signal_enabling_condition-${transitionName}`);
      label.textContent = transitionName;
    
      // Anexa o label à sua coluna
      labelCol.appendChild(label);
    
      // Cria a coluna para o input
      const inputCol = document.createElement('div');
      inputCol.classList.add('col-md-9');
    
      // Cria o input
      const input = document.createElement('input');
      input.setAttribute('type', 'text');
      input.classList.add('form-control'); // Bootstrap class for inputs
      input.setAttribute('name', `transition_signal_enabling_condition-${transitionName}`);
      input.setAttribute('id', `transition_signal_enabling_condition-${transitionName}`); 
      input.setAttribute('autocomplete', `off`); 
      


      input.addEventListener("change", function(){
        extra_tokens = ["i0","i1","i2","i3","i4","i5","i6","i7",]
        let valid_expression_bool;
        let new_string; 
        [valid_expression_bool,new_string] = is_valid_expression($(this).val(),extra_tokens)
        if (valid_expression_bool && new_string != ""){
            $(this).attr('class','form-control transition_signal_enabling_condition_textfield')
            $(this).val(new_string)
        } else {
            $(this).attr('class','form-control transition_signal_enabling_condition_textfield border border-danger')
        }
      });


      if (loaded_from_json){
        input.value = transition["signal_enabling_expression"]
        const event = new Event('change');
        input.dispatchEvent(event);
      }else{
        input.value = "true"
      }
    
      // Anexa o input à sua coluna
      inputCol.appendChild(input);
    
      // Anexa as colunas à div externa
      outerDiv.appendChild(labelCol);
      outerDiv.appendChild(inputCol);
    
      // Anexa a div externa à div principal
      transition_signal_enabling_condition_Container.appendChild(outerDiv);
    });
    

    // output_activation_condition_container
    // Seleciona o container
    const output_activation_condition_Container = document.getElementById('output_activation_condition_container');
    output_activation_condition_Container.textContent = "";

    for (let i = 0; i < 8; i++) {
      const outputName = `o${i}`;
      const outerDiv = document.createElement('div');
      outerDiv.classList.add('row', 'my-1'); // Usando 'row' em vez de 'd-flex'

      // Cria a coluna para o label
      const labelCol = document.createElement('div');
      labelCol.classList.add('col-md-3', 'd-flex', 'align-items-center'); // Definindo o tamanho da coluna e alinhamento

      // Cria a etiqueta <label>
      const label = document.createElement('label');
      label.classList.add('form-label');
      label.setAttribute('for', `output_activation_condition-${outputName}`);
      label.textContent = outputName;
      labelCol.appendChild(label); // Anexa o label à sua coluna

      // Cria a coluna para o input
      const inputCol = document.createElement('div');
      inputCol.classList.add('col-md-9'); // Definindo o tamanho da coluna

      // Cria o input
      const input = document.createElement('input');
      input.setAttribute('type', 'text');
      input.classList.add('form-control'); // Usando 'form-control' para estilização do Bootstrap
      input.setAttribute('name', `output_activation_condition-${outputName}`);
      input.setAttribute('id', `output_activation_condition-${outputName}`);
      // ...restante do código do input...

      input.addEventListener("change", function(){
          
        let extra_tokens = IOPT_dictionary["places"].map(function(place){return place["id"]})
        let valid_expression_bool;
        let new_string; 
        [valid_expression_bool,new_string] = is_valid_expression($(this).val(),extra_tokens)
        if (valid_expression_bool && new_string != ""){
          $(this).attr('class','form-control output_activation_condition_textfield')
          $(this).val(new_string)
        } else {
          $(this).attr('class','form-control output_activation_condition_textfield border border-danger')
        }
      });
      
      if (loaded_from_json){
        input.value=IOPT_dictionary["marking_to_output_expressions"][outputName]
        const event = new Event('change');
        input.dispatchEvent(event);
      }else{
        input.value = "false"
      }      
      inputCol.appendChild(input);

      // Anexa as colunas à div externa
      outerDiv.appendChild(labelCol);
      outerDiv.appendChild(inputCol);

      // Anexa a div externa à div principal
      output_activation_condition_Container.appendChild(outerDiv);
    }

    //--------------------------------
    const timed_transition_timer_Element = document.getElementById('timed_transition_timer_container');
    timed_transition_timer_Element.textContent = "";
    // Controle de visibilidade do container de timers
    IOPT_dictionary["timed_transitions"].length > 0 ? $("#timer_div").show() : $("#timer_div").hide();

    IOPT_dictionary["timed_transitions"].forEach((transition, index) => {
      const transitionName = transition["id"];

      // Cria a linha 'row' para o grupo de label e input
      const outerDiv = document.createElement('div');
      outerDiv.classList.add('row', 'my-1');

      // Cria a coluna para o label
      const labelCol = document.createElement('div');
      labelCol.classList.add('col-md-3', 'd-flex', 'align-items-center');

      // Cria a etiqueta <label>
      const label = document.createElement('label');
      label.classList.add('form-label');
      label.setAttribute('for', `timed_transition_timer-${transitionName}`);
      label.textContent = transitionName;
      labelCol.appendChild(label);

      // Cria a coluna para o input
      const inputCol = document.createElement('div');
      inputCol.classList.add('col-md-9');

      // Cria o input
      const input = document.createElement('input');
      input.setAttribute('type', 'number');
      input.setAttribute('step', '0.01');
      input.classList.add('form-control'); // Classe do Bootstrap para estilização dos inputs
      input.setAttribute('name', `timed_transition_timer-${transitionName}`);
      input.setAttribute('id', `timed_transition_timer-${transitionName}`);
      input.setAttribute('required', true);
      input.value = loaded_from_json ? transition["timer_sec"] : 0.00;
      input.addEventListener("change", function () {
        this.value = Math.max(0.00, parseFloat(this.value));
      });
      inputCol.appendChild(input);

      // Anexa as colunas à div externa
      outerDiv.appendChild(labelCol);
      outerDiv.appendChild(inputCol);

      // Anexa a div externa à div principal
      timed_transition_timer_Element.appendChild(outerDiv);
    });


    $('#IOPT_config').show()
}