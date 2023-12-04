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
}

