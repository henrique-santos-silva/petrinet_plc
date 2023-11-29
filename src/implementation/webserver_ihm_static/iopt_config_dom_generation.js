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

  




function generate_IOPT_config_div(
  IOPT_dictionary, //dict
  loaded_from_json, //bool
  inputs_name_list, //list[str]
  outputs_name_list, //list[str]
){
    generate_transition_signal_enabling_condition_container(IOPT_dictionary, loaded_from_json, inputs_name_list)
    generate_output_activation_condition_container(IOPT_dictionary, loaded_from_json, outputs_name_list )
    
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
      input.classList.add('timed_transition_timer_textfield');
      input.setAttribute('name', `timed_transition_timer-${transitionName}`);
      input.setAttribute('id', `timed_transition_timer-${transitionName}`);
      input.setAttribute('required', true);
      input.value = loaded_from_json ? transition["timer_sec"] : 0.01;
      input.addEventListener("change", function () {
        this.value = Math.max(0.01, parseFloat(this.value));
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


function generate_transition_signal_enabling_condition_container(
  IOPT_dictionary, //dict
  loaded_from_json, //bool
  inputs_name_list //list[str]
){
  // -------------- Input to Transitons-------------------------------------------------------------
  const transition_signal_enabling_condition_container = document.getElementById('transition_signal_enabling_condition_container');

  transition_signal_enabling_condition_container.textContent="";
  const transitions = [...IOPT_dictionary["instantaneous_transitions"],...IOPT_dictionary["timed_transitions"]];
  
  for (const transition of transitions){
    const transitionName = transition.id;

    const outerDiv = document.createElement('div');
    outerDiv.classList.add('row', 'my-1');

      const labelCol = document.createElement('div');
      labelCol.classList.add('col-md-3', 'd-flex', 'align-items-center');

        const label = document.createElement('label');
        label.classList.add('form-label');
        label.setAttribute('for', `transition_signal_enabling_condition-${transitionName}`);
        label.textContent = transitionName;
      
        labelCol.appendChild(label);
      outerDiv.appendChild(labelCol);
    

      const inputCol = document.createElement('div');
      inputCol.classList.add('col-md-9');
        
        const input = document.createElement('input');
        input.setAttribute('type', 'text');
        input.classList.add('form-control');
        input.classList.add('transition_signal_enabling_condition_textfield');

        input.setAttribute('name', `transition_signal_enabling_condition-${transitionName}`);
        input.setAttribute('id', `transition_signal_enabling_condition-${transitionName}`); 
        input.setAttribute('autocomplete', `off`); 


        if (loaded_from_json){
          input.value = transition["signal_enabling_expression"];
          const event = new Event('change');
          input.dispatchEvent(event);
        }else{
          input.value = "true";
        }

        inputCol.appendChild(input);
      outerDiv.appendChild(inputCol);
      transition_signal_enabling_condition_container.appendChild(outerDiv);
  }
}

function generate_output_activation_condition_container(
  IOPT_dictionary, //dict
  loaded_from_json, //bool
  outputs_name_list //list[str]
){
  const output_activation_condition_container = document.getElementById('output_activation_condition_container');
  output_activation_condition_container.textContent = "";

  for (const output_name of outputs_name_list){
    const outerDiv = document.createElement('div');
    outerDiv.classList.add('row', 'my-1');

      // Cria a coluna para o label
      const labelCol = document.createElement('div');
      labelCol.classList.add('col-md-3', 'd-flex', 'align-items-center'); // Definindo o tamanho da coluna e alinhamento

        // Cria a etiqueta <label>
        const label = document.createElement('label');
        label.classList.add('form-label');
        label.setAttribute('for', `output_activation_condition-${output_name}`);
        label.textContent = output_name;
        labelCol.appendChild(label); // Anexa o label à sua coluna
      outerDiv.appendChild(labelCol);

      // Cria a coluna para o input
      const inputCol = document.createElement('div');
      inputCol.classList.add('col-md-9'); // Definindo o tamanho da coluna

        // Cria o input
        const input = document.createElement('input');
        input.setAttribute('type', 'text');
        input.classList.add('form-control'); // Usando 'form-control' para estilização do Bootstrap
        input.classList.add('output_activation_condition_textfield'); // Usando 'form-control' para estilização do Bootstrap
        input.setAttribute('name', `output_activation_condition-${output_name}`);
        input.setAttribute('id', `output_activation_condition-${output_name}`);

        if (loaded_from_json){
          input.value=IOPT_dictionary["marking_to_output_expressions"][output_name]
          const event = new Event('change');
          input.dispatchEvent(event);
        }else{
          input.value = "false"
        }
        inputCol.appendChild(input);
      outerDiv.appendChild(inputCol);
      output_activation_condition_container.appendChild(outerDiv);
  }

}