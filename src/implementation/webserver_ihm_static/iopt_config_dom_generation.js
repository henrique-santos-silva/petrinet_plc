/**
 * 
 *
 * @param {string} placeOrTransitionId
 * @return {{ name: string, remainingString: string? }}
 */
function sanitizePlaceOrTransitionName(placeOrTransitionId){
  function sanitize(s){
    return s.trim().replace(' ','_').toLowerCase();
  }
  
  const startOfExpressionIndex = placeOrTransitionId.indexOf('(');
  if (startOfExpressionIndex === -1) {
    return { name: sanitize(placeOrTransitionId), remainingString: null};
  }
  let remainingString = placeOrTransitionId.slice(startOfExpressionIndex).trim();
  remainingString = remainingString.slice(1, remainingString.length - 1);

  return {
    name: sanitize(placeOrTransitionId.slice(0, startOfExpressionIndex)),
    remainingString,
  };

}

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
          
            // dict used to create 'marking_to_output_expressions' obj in json
            const dict_output_to_listOfPlaces = {};
            for (let i = 0; i <= 15; i++) {
              dict_output_to_listOfPlaces[`DO${i}`] = [];
            }

            placeElements.forEach((placeElement, index) => {
                const id = placeElement.getAttribute("id");
                const initial_marking = parseInt(placeElement.querySelector("initialMarking").querySelector("value").textContent.split(',')[1]); 
                const capacity = parseInt(placeElement.querySelector("capacity").querySelector("value").textContent);
                
                const x_position = parseFloat(placeElement.querySelector("graphics").querySelector("position").getAttribute("x"));
                const y_position = parseFloat(placeElement.querySelector("graphics").querySelector("position").getAttribute("y"));
                const graphics = {x_position,y_position};
                
                const {placeName, outputSignals} = get_output_signals_from_place_id(id);
                IOPT_dictionary['places'].push({id:placeName,initial_marking,capacity,graphics});
                
                outputSignals.forEach(o => {
                  if (o in dict_output_to_listOfPlaces){
                    dict_output_to_listOfPlaces[o].push(placeName)
                  }else{
                    dict_output_to_listOfPlaces[o] = [placeName]
                  }
                });

                
                console.log(`Place ${index + 1}: id - ${id}, initial_marking - ${initial_marking}, capacity - ${capacity}`);
            });

            Object.entries(dict_output_to_listOfPlaces).forEach(([key, listOfPlaces]) => {
              if (listOfPlaces.length > 0){
                dict_output_to_listOfPlaces[key] = listOfPlaces.join(" || "); 
              }else{
                dict_output_to_listOfPlaces[key] = "true";
              }

            });
            IOPT_dictionary["marking_to_output_expressions"] = dict_output_to_listOfPlaces

            const transitionElements = xmlDoc.querySelectorAll("transition");
            transitionElements.forEach((transitionElement, index) => {
                const id = transitionElement.getAttribute("id");
                const rate = parseFloat(transitionElement.querySelector("rate").querySelector("value").textContent); 
                const priority = parseInt(transitionElement.querySelector("priority").querySelector("value").textContent);
                const timed = transitionElement.querySelector("timed").querySelector("value").textContent == 'true';
                
                const x_position = parseFloat(transitionElement.querySelector("graphics").querySelector("position").getAttribute("x"));
                const y_position = parseFloat(transitionElement.querySelector("graphics").querySelector("position").getAttribute("y"));
                const rotation   = parseInt(transitionElement.querySelector("orientation").querySelector("value").textContent);
                const graphics = {x_position,y_position,rotation}
                
                let {transitionName,enablingExpression} = get_transition_signal_enabling_expression_from_id(id);
                
                transitionObj = {
                  id:transitionName,
                  signal_enabling_expression: enablingExpression,
                  rate,priority,graphics
                }
                if (timed){
                  transitionObj["timer_sec"] = rate
                }

                IOPT_dictionary[timed?'timed_transitions':'instantaneous_transitions'].push(transitionObj);
            });

            const arcElements = xmlDoc.querySelectorAll("arc");
            arcElements.forEach((arcElement, index) => {
                const id = arcElement.getAttribute("id");
                const {name:source} = sanitizePlaceOrTransitionName(arcElement.getAttribute("source"));
                const {name:target} = sanitizePlaceOrTransitionName(arcElement.getAttribute("target"));
                const weight = parseInt(arcElement.querySelector("inscription").querySelector("value").textContent.split(',')[1]);
                const type = arcElement.querySelector("type").getAttribute("value");

                const arcPathElements = arcElement.querySelectorAll("arcpath");
                const graphic_path = [];

                arcPathElements.forEach((arcPathElement,index)=>{
                  const x_position = parseFloat(arcPathElement.getAttribute("x"));
                  const y_position = parseFloat(arcPathElement.getAttribute("y"));
                  graphic_path.push({x_position,y_position});
                });
                
                IOPT_dictionary['arcs'].push({id,source,target,weight,type,graphic_path})
            });
            console.log(IOPT_dictionary)
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



/**
 * Given a placeId, returns the place name and a list of output signals associated with that place.
 *
 * @param {string} placeId - The ID of the place to check.
 * @return {{ placeName: string, outputSignals: string[] }} - An object containing the place name and an array of output signals associated with the place.
 */
function get_output_signals_from_place_id(placeId) {
  const {name:placeName,remainingString:signalsString} = sanitizePlaceOrTransitionName(placeId  )
  let outputSignals = [];
  if (signalsString !== null){
    outputSignals = signalsString
      .split(';')
      .filter(s => s !== '')
      .map(s => s.trim());
  }
  return { placeName, outputSignals };
  }

/**
 * Extracts the transition name and enabling expression from a given transitionId.
 * If the transitionId contains an expression in parentheses, returns the name and the expression.
 * If the transitionId does not contain an expression, returns the name and 'true'.
 * 
 * @param {string} transitionId - The ID of the transition to parse.
 * @return {{ transitionName: string, enablingExpression: string }} - An object containing the transition name and the enabling expression.
 */
function get_transition_signal_enabling_expression_from_id(transitionId) {
  const {name:transitionName,remainingString} = sanitizePlaceOrTransitionName(transitionId)
    return {
    transitionName,
    enablingExpression: remainingString ?? "true"
    };
}
