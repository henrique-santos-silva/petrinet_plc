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
                
                const x_position = parseFloat(placeElement.querySelector("graphics").querySelector("position").getAttribute("x"));
                const y_position = parseFloat(placeElement.querySelector("graphics").querySelector("position").getAttribute("y"));
                const graphics = {x_position,y_position};
                
                IOPT_dictionary['places'].push({id,initial_marking,capacity,graphics});
                
                console.log(`Place ${index + 1}: id - ${id}, initial_marking - ${initial_marking}, capacity - ${capacity}`);
            });

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
                
                IOPT_dictionary[timed?'timed_transitions':'instantaneous_transitions'].push({id,rate,priority,graphics});
            });

            const arcElements = xmlDoc.querySelectorAll("arc");
            arcElements.forEach((arcElement, index) => {
                const id = arcElement.getAttribute("id");
                const source = arcElement.getAttribute("source");
                const target = arcElement.getAttribute("target");
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
