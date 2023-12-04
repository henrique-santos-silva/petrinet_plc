var places_global = {};
var transitions_global = {};
var arcs_global = [];
var extreme_coord = {min_x:Infinity,min_y:Infinity,max_x:-Infinity,max_y:-Infinity}
$(document).ready(function (){
    var infinite_canvas = new InfiniteCanvas('petriNetCanvas');
    var socket = io.connect('http://' + document.domain + ':' + location.port);

    socket.on('petrinet_json_update',function(IOPT_dictionary){
        console.log('petrinet_json_update')
        generatePetriNetFromJson(IOPT_dictionary);
        infinite_canvas.redraw()
    });
    
    socket.on('petrinet_debugging_info',function(petrinet_debugging_info){
        console.log('petrinet_debugging_info')
        for (let transition_id in petrinet_debugging_info.transitions_enabling_state) {
            transition = transitions_global[transition_id];
            transition.isPetriEnabled  = petrinet_debugging_info.transitions_enabling_state[transition_id].is_petri_enabled
            transition.isSignalEnabled = petrinet_debugging_info.transitions_enabling_state[transition_id].is_signal_enabled
        }

        if ('places_marking' in petrinet_debugging_info){
            
            for (let place_id in petrinet_debugging_info.places_marking) {
                place = places_global[place_id];
                place.marking = petrinet_debugging_info.places_marking[place_id];
            }
        }
        infinite_canvas.redraw()
    });
})
// Class to represent a position with x and y coordinates
class Position {
    constructor(x, y) {
        this.x = x;
        this.y = y;
    }
}

// Class for labels with text and a position
class Label {
    constructor(text, position) {
        this.text = text;
        this.position = position; // Position should be an instance of Position
    }
    
    // Method to draw the label on the canvas
    draw(ctx) {
        // Set the font to measure the text
        ctx.font = '9px Arial';

        // Measure the text to calculate the dimensions of the background rectangle
        const textMeasure = ctx.measureText(this.text);
        const padding = 0.2; // Extra space around the text
        const backgroundWidth = textMeasure.width + padding * 2;
        const backgroundHeight = parseInt(ctx.font, 10) + padding * 2;

        // Calculate the starting x position to center the text and background rectangle
        const startX = this.position.x - backgroundWidth / 2;
        const startY = this.position.y - backgroundHeight / 2 + padding;

        // Draw the background rectangle with 50% transparency
        ctx.fillStyle = 'rgba(255, 255, 255, 0.5)'; // White with 50% transparency
        ctx.fillRect(startX, startY, backgroundWidth, backgroundHeight);

        // Draw the text centered
        ctx.fillStyle = 'black'; // Text color
        ctx.fillText(this.text, startX + padding, this.position.y);
    }
}

// Class for transitions in a Petri net
class Transition {

    static WIDTH    = 11; //empirical value
    static HEIGHT   = 31; //empirical value
    static X_OFFSET = 6;  //empirical value
    static Y_OFFSET = -3; //empirical value
    
    constructor(x, y,isTimed, label,rotation) {

        this.position = new Position(x, y);
        this.rotation = rotation
        this.isPetriEnabled  = false; // Indicates if the transition is enabled
        this.isSignalEnabled = false;
        this.isTimed = isTimed;     // Boolean indicating if the transition is timed
        this.label = label;
    }

    // Method to draw the Transition on the canvas
    draw(ctx) {
        ctx.lineWidth = 2;
        if (this.isTimed) {
            // Draw an outlined rectangle for timed transitions
            ctx.strokeStyle = this.isPetriEnabled ? (this.isSignalEnabled ? 'yellow' : 'red') : 'black';
            if (this.rotation == 90){
                ctx.strokeRect(this.position.x + Transition.Y_OFFSET, this.position.y + Transition.X_OFFSET, Transition.HEIGHT, Transition.WIDTH);
            }else{
                ctx.strokeRect(this.position.x + Transition.X_OFFSET, this.position.y + Transition.Y_OFFSET, Transition.WIDTH, Transition.HEIGHT);
            }
        } else {
            // Draw a filled rectangle for non-timed transitions
            ctx.fillStyle = this.isPetriEnabled ? 'red' : 'black';
            if (this.rotation == 90){
                ctx.fillRect(this.position.x + Transition.Y_OFFSET, this.position.y + Transition.X_OFFSET, Transition.HEIGHT, Transition.WIDTH);
            }else{
                ctx.fillRect(this.position.x   + Transition.X_OFFSET, this.position.y + Transition.Y_OFFSET, Transition.WIDTH, Transition.HEIGHT);
            }
        }

        // Draw the label of the Transition
        this.label.draw(ctx);
    }
}

// Class for places in a Petri net
class Place {

    static R = 15; // place radius. empirical value
    static X_OFFSET = 12; //empirical value
    static Y_OFFSET = 12; //empirical value
    static TOKEN_RADIUS = 3;

    constructor(x, y, marking, label) {
        this.position = new Position(x, y);
        this.marking = marking; // A number indicating the number of tokens
        this.label = label;
    }

    // Method to draw the Place on the canvas
    draw(ctx) {
        ctx.fillStyle   = 'black';
        ctx.strokeStyle = 'black';

        // Erase previous tokens by filling the circle with white
        ctx.beginPath();
        ctx.arc(this.position.x + Place.X_OFFSET, this.position.y + Place.Y_OFFSET, Place.R, 0, 2 * Math.PI);
        ctx.fillStyle = 'white';
        ctx.fill();

        // Draw the outer circle for the Place
        ctx.beginPath();
        ctx.arc(this.position.x + Place.X_OFFSET, this.position.y + Place.Y_OFFSET, Place.R, 0, 2 * Math.PI);
        ctx.fillStyle = 'black';  // Set fill color back to black for tokens
        ctx.stroke();

        

        // If marking is 1, draw a single token centered in the Place
        if (this.marking === 1) {
            ctx.beginPath();
            ctx.arc(this.position.x + Place.X_OFFSET, this.position.y + Place.Y_OFFSET, Place.TOKEN_RADIUS, 0, 2 * Math.PI);
            ctx.fill();
        } else if (this.marking <= 5) {
            // Draw individual tokens for marking of 2 to 5
            for (let i = 0; i < this.marking; i++) {
                let angle = i * (2 * Math.PI / this.marking);
                let tokenX = this.position.x + Place.X_OFFSET + 0.5*Place.R * Math.cos(angle);
                let tokenY = this.position.y + Place.Y_OFFSET + 0.5*Place.R * Math.sin(angle);

                ctx.beginPath();
                ctx.arc(tokenX, tokenY, Place.TOKEN_RADIUS, 0, 2 * Math.PI);
                ctx.fill();
            }

          //Write the number of tokens  
        } else if (this.marking <= 10){
            ctx.fillText(this.marking.toString(), this.position.x + Place.X_OFFSET - 0.2* Place.r, this.position.y + Place.Y_OFFSET + 0.2*Place.R);
        }else if (this.marking <= 100){
            ctx.fillText(this.marking.toString(), this.position.x + Place.X_OFFSET - 0.4* Place.r, this.position.y + Place.Y_OFFSET + 0.2*Place.R);
        }else if (this.marking <= 1000){
            ctx.fillText(this.marking.toString(), this.position.x + Place.X_OFFSET - 0.6* Place.r, this.position.y + Place.Y_OFFSET + 0.2*Place.R);
        }
        else{
            ctx.fillText(this.marking.toString(), this.position.x + Place.X_OFFSET - 0.8* Place.r, this.position.y + Place.Y_OFFSET + 0.2*Place.R);
        }
        
        // Draw the label of the Place
        this.label.draw(ctx);
    }
}

// Class for arcs in a Petri net
class Arc {
    constructor(weight, isInhibitor, label, path) {
        this.weight = weight; // Weight of the arc
        this.isInhibitor = isInhibitor; // Boolean indicating if the arc is an inhibitor
        this.label = label;
        this.path = path; // Path should be a list of Position instances
    }
    draw(ctx) {

        ctx.fillStyle   = 'black';
        ctx.strokeStyle = 'black';
        if (this.path.length < 2) {
            console.error("Not enough points to draw an arc");
            return;
        }

        // Begin drawing the arc path
        ctx.beginPath();
        ctx.moveTo(this.path[0].x, this.path[0].y);

        // Draw lines connecting each point in the path
        for (let i = 1; i < this.path.length; i++) {
            ctx.lineTo(this.path[i].x, this.path[i].y);
        }

        // Stroke the path
        ctx.stroke();

        // Draw either an arrowhead or a circle at the last position based on the arc type
        const lastPoint = this.path[this.path.length - 1];
        const secondLastPoint = this.path[this.path.length - 2];
        if (this.isInhibitor) {
            // If the arc is an inhibitor, draw a circle at the end
            this.drawInhibitorArcEnd(ctx, secondLastPoint, lastPoint,);
        } else {
            // If it's a regular arc, draw an arrowhead
            this.drawArrowhead(ctx, secondLastPoint, lastPoint);
        }
    }

    // Method to draw an arrowhead at the end of the arc
    drawArrowhead(ctx, from, to) {
        const headLength = 10    ; // The size of the arrow head

        // Calculate the angle of the line
        const dx = to.x - from.x;
        const dy = to.y - from.y;
        const angle = Math.atan2(dy, dx);

        // Start drawing the arrowhead from the end point
        ctx.beginPath();
        
        // Move to the tip of the arrow
        ctx.moveTo(to.x, to.y);

        // Draw the first side of the arrowhead
        ctx.lineTo(to.x - headLength * Math.cos(angle - Math.PI / 6), to.y - headLength * Math.sin(angle - Math.PI / 6));

        // Draw the line back to the tip of the arrow to create the second side
        ctx.moveTo(to.x, to.y); // Move back to the tip of the arrow
        ctx.lineTo(to.x - headLength * Math.cos(angle + Math.PI / 6), to.y - headLength * Math.sin(angle + Math.PI / 6));



        // Set the style for the arrowhead
        ctx.strokeStyle = 'black';
        ctx.lineWidth = 2;

        // Apply the stroke to the arrowhead
        ctx.stroke();
    }

    // Method to draw the end of an inhibitor arc with a circle
    drawInhibitorArcEnd(ctx, from, to) {
        const radius = 3;
        // Calculate the angle of the last line segment
        const angle = Math.atan2(to.y - from.y, to.x - from.x);
        // Determine the center point of the circle so that it touches the last point of the arc path
        const circleCenterX = to.x - radius * Math.cos(angle);
        const circleCenterY = to.y - radius * Math.sin(angle);

        // Draw the outlined circle with a white fill
        ctx.beginPath();
        ctx.arc(circleCenterX, circleCenterY, radius, 0, 2 * Math.PI);
        ctx.fillStyle = 'white'; // Set the fill color to white
        ctx.fill(); // Apply the fill to the circle
        ctx.strokeStyle = 'black'; // Set the stroke color for the circle
        ctx.stroke(); // Apply the stroke to the circle
    }
}


function generatePetriNetFromJson(petriNetJson) {
    transitions_global = {};
    places_global = {};
    arcs_global = [];
    extreme_coord = {min_x:Infinity,min_y:Infinity,max_x:-Infinity,max_y:-Infinity}

    // initialize Arcs
    petriNetJson.arcs.forEach(arc => {
        const path = arc.graphic_path.map(point => new Position(point.x_position, point.y_position)); // Map the graphic path to Position instances
        const newArc = new Arc(
            arc.weight,
            arc.type === "inhibitor", // Determine if the arc is an inhibitor
            new Label(arc.weight, path[0]), // Assume the label position is the first point of the arc path
            path
        );
        arcs_global.push(newArc)


    });

    // initialize Places
    petriNetJson.places.forEach(place => {
        const newPlace = new Place(
            place.graphics.x_position,
            place.graphics.y_position,
            place.initial_marking,
            new Label(
                place.id,
                new Position(
                    place.graphics.x_position,
                    place.graphics.y_position -10
                )
            )

            );
        extreme_coord.min_x = Math.min(place.graphics.x_position, extreme_coord.min_x);
        extreme_coord.min_y = Math.min(place.graphics.y_position, extreme_coord.min_y);
        extreme_coord.max_x = Math.max(place.graphics.x_position, extreme_coord.max_x);
        extreme_coord.max_y = Math.max(place.graphics.y_position, extreme_coord.max_y);

        places_global[place.id] = newPlace;
    });

    // initialize Transitions (both instantaneous and timed)
    const transitions = [...petriNetJson.instantaneous_transitions, ...petriNetJson.timed_transitions];
    transitions.forEach(transition => {
        const isTimed = 'timer_sec' in transition;
        const newTransition = new Transition(
            transition.graphics.x_position,
            transition.graphics.y_position,
            isTimed,
            new Label(
                transition.id,
                new Position(
                    transition.graphics.x_position, 
                    transition.graphics.y_position -10
                )
            ),
            transition.graphics.rotation
        );
        transitions_global[transition.id] = newTransition;

        extreme_coord.min_x = Math.min(transition.graphics.x_position, extreme_coord.min_x);
        extreme_coord.min_y = Math.min(transition.graphics.y_position, extreme_coord.min_y);
        extreme_coord.max_x = Math.max(transition.graphics.x_position, extreme_coord.max_x);
        extreme_coord.max_y = Math.max(transition.graphics.y_position, extreme_coord.max_y);

    });

}