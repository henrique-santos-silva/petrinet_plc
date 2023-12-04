class InfiniteCanvas {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        // canvas = document.getElementById('petriNetCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.scale = 1;
        this.originX = 0;
        this.originY = 0;
        this.dragStartX = 0;
        this.dragStartY = 0;
        this.dragging = false;

        this.redrawTimeout = null;

        this.addEventListeners();
        this.redraw();
    }

    addEventListeners() {
        this.canvas.addEventListener('wheel', this.handleZoom.bind(this));
        this.canvas.addEventListener('mousedown', this.startDrag.bind(this));
        this.canvas.addEventListener('mousemove', this.drag.bind(this));
        this.canvas.addEventListener('mouseup', this.endDrag.bind(this));
        let this_ = this;
        window.onload = function() {
            this_.canvas.width = window.innerWidth;
            this_.canvas.height = window.innerHeight;
            let scale_x = this_.canvas.width / (extreme_coord.max_x - extreme_coord.min_x)
            let scale_y = this_.canvas.height / (extreme_coord.max_y - extreme_coord.min_y)
            if (scale_x == 0 && scale_y == 0){
                this_.scale = 1    
            }else{
                this_.scale = 0.4 * Math.min(scale_x,scale_y)
            }
            this_.redraw();

        };
        window.onresize = function() {
            this_.canvas.width = window.innerWidth;
            this_.canvas.height = window.innerHeight;
            let scale_x = this_.canvas.width / (extreme_coord.max_x-extreme_coord.min_x)
            let scale_y = this_.canvas.height / (extreme_coord.max_y-extreme_coord.min_y)
            if (scale_x == 0 && scale_y == 0){
                this_.scale = 1    
            }else{
                this_.scale = 0.4 * Math.min(scale_x,scale_y)
            }
            this_.redraw();
            
        };
    }

    getMouseCoordsOnCanvas(event) {
        const mouseX = (event.clientX -this.originX - this.canvas.offsetLeft)/ this.scale;
        const mouseY = (event.clientY -this.originY - this.canvas.offsetTop)/ this.scale;
        return { x: mouseX, y: mouseY };
    }
    
    handleZoom(event) {
       
        const zoomIntensity = 0.1;
        const{x: mousePosX, y:mousePosY} = this.getMouseCoordsOnCanvas(event)
        const wheel = event.deltaY < 0 ? 1 : -1;
        const zoom = Math.exp(wheel * zoomIntensity);
    
        this.scale *= zoom;
    
        this.originX = event.clientX  -  this.canvas.offsetLeft - mousePosX*this.scale;
        this.originY = event.clientY  -  this.canvas.offsetTop - mousePosY*this.scale;
    
        event.preventDefault();
        this.redraw();
    }

    startDrag(event) {
        const{x: dragStartX, y:dragStartY} = this.getMouseCoordsOnCanvas(event)
        this.dragStartX = dragStartX
        this.dragStartY = dragStartY
        this.dragging = true;
    }

    drag(event) {
        if (this.dragging) {
            this.originX = event.clientX  -  this.canvas.offsetLeft - this.dragStartX*this.scale;
            this.originY = event.clientY  -  this.canvas.offsetTop - this.dragStartY*this.scale;
            this.redraw();
        }
    }

    endDrag(event) {
        this.dragging = false;
    }

    redraw() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        this.ctx.save();
        this.ctx.translate(this.originX, this.originY);
        this.ctx.scale(this.scale, this.scale);


        for (let arc_index in arcs_global) {
            const arc = arcs_global[arc_index];
            arc.draw(this.ctx);
        }
        for (let place_id in places_global) {
            const place = places_global[place_id];
            place.draw(this.ctx);
        }
        for (let transition_id in transitions_global) {
            const transition = transitions_global[transition_id];
            transition.draw(this.ctx);
        }

        this.ctx.restore();

    }
}

