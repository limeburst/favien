"use strict";

var Trace = function(x, y, p) {
    this.x = x;
    this.y = y;
    this.p = p;
};

var Brush = function(size, flow, spacing, color) {
    var distance;
    var prevX;
    var prevY;
    var prevP;
    var lastX;
    var lastY;
    var direction;
    this.name = 'arc';
    this.color = color;
    this.size = size;
    this.flow = flow;
    this.spacing = spacing;
    this.draw = function(canvas, trace) {
        var ctx = canvas[0].getContext('2d');
        ctx.globalAlpha = this.flow;
        ctx.fillStyle = this.color;
        ctx.beginPath();
        ctx.arc(trace.x, trace.y, trace.p * this.size, 0, Math.PI * 2);
        ctx.fill();
        ctx.closePath();
    };
    this.down = function(canvas, trace) {
        isDrawing = true;
        lastX = prevX = trace.x;
        lastY = prevY = trace.y;
        prevP = trace.p;
        distance = 0;
        this.draw(canvas, trace);
    };
    this.move = function(canvas, trace) {
        if (isDrawing) {
            var dx = trace.x - prevX;
            var dy = trace.y - prevY;
            var dp = trace.p - prevP;
            distance += Math.sqrt(dx * dx + dy * dy);
            prevX = trace.x;
            prevY = trace.y;
            var ldx = trace.x - lastX;
            var ldy = trace.y - lastY;
            var ld = Math.sqrt(ldx * ldx + ldy * ldy);
            direction = Math.atan2(ldy, ldx);
            var midScale = (prevP + trace.p) / 2;
            var drawSpacing = this.size * this.spacing * midScale;
            if (drawSpacing === 0) {
                return
            }
            if (distance < drawSpacing) {
                prevP = trace.p;
                return
            }
            var scaleSpacing = dp * (drawSpacing / distance);
            if (ld < drawSpacing) {
                lastX = trace.x;
                lastY = trace.y;
                distance -= drawSpacing;
                this.draw(canvas, new Trace(lastX, lastY, trace.p));
            } else {
                while (distance >= drawSpacing) {
                    var tx = Math.cos(direction);
                    var ty = Math.sin(direction);
                    lastX += tx * drawSpacing;
                    lastY += ty * drawSpacing;
                    prevP += scaleSpacing;
                    distance -= drawSpacing;
                    this.draw(canvas, new Trace(lastX, lastY, prevP));
                }
            }
        }
    };
};

var brush;
var isDrawing;

function getPressure() {
    var wacom = document.getElementById('wacom').penAPI;
    if (wacom === undefined) {
        return 0.5
    } else {
        return wacom.pressure
    }
}

$(document).ready(function() {
    var save = $('#save');
    var canvas = $('#canvas');
    canvas.on('mousedown', function(e) {
        isDrawing = true;
        brush = new Brush(
            $('#size').val(),
            $('#flow').val(),
            $('#spacing').val(),
            $('#color').val()
        );
        brush.down(canvas, new Trace(e.offsetX, e.offsetY, getPressure()));
    });
    canvas.on('mousemove', function(e) {
        if (isDrawing) {
            brush.move(canvas, new Trace(e.offsetX, e.offsetY, getPressure()));
        }
    });
    canvas.on('mouseup mouseleave', function(e) {
        isDrawing = false;
        brush = undefined;
    });
    save.submit(function(e) {
        $.ajax({
            url: save[0].action,
            type: save[0].method,
            dataType: 'json',
            data: {
                title: $('#title').val(),
                description: $('#description').val(),
                canvas: canvas[0].toDataURL()
            },
            success: function(data) {
                window.location.replace(data.location);
            }
        });
        e.preventDefault();
    });
});
