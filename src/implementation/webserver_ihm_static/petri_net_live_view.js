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
    
}

// Class for transitions in a Petri net
class Transition {
    constructor(x, y,isTimed, label,rotation) {

        this.position = new Position(x, y);
        this.rotation = rotation
        this.isPetriEnabled  = false; // Indicates if the transition is enabled
        this.isSignalEnabled = false;
        this.isTimed = isTimed;     // Boolean indicating if the transition is timed
        this.label = label;
    }
}

// Class for places in a Petri net
class Place {
    constructor(x, y, marking, label) {
        this.position = new Position(x, y);
        this.marking = marking; // A number indicating the number of tokens
        this.label = label;
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

