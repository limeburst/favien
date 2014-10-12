"use strict";

var Stroke = function(brush) {
    this.brush = brush;
    this.traces = [];
};

var Trace = function(x, y, p, t) {
    this.x = x;
    this.y = y;
    this.p = p;
    this.t = t;
};

var Brush = function(radius, globalAlpha, spacing, fillStyle, globalCompositeOperation) {
    var distance;
    var prevX;
    var prevY;
    var prevP;
    var lastX;
    var lastY;
    var direction;
    this.name = 'arc';
    this.radius = radius;
    this.globalAlpha = globalAlpha;
    this.spacing = spacing;
    this.fillStyle = fillStyle;
    this.globalCompositeOperation = globalCompositeOperation;
    this.draw = function(canvas, trace) {
        var ctx = canvas[0].getContext('2d');
        ctx.globalAlpha = this.globalAlpha;
        ctx.fillStyle = this.fillStyle;
        ctx.globalCompositeOperation = this.globalCompositeOperation;
        ctx.beginPath();
        ctx.arc(trace.x, trace.y, trace.p * this.radius, 0, Math.PI * 2);
        ctx.fill();
        ctx.closePath();
    };
    this.down = function(canvas, trace) {
        isDrawing = true;
        lastX = prevX = trace.x;
        lastY = prevY = trace.y;
        prevP = trace.p;
        distance = 0;
        stroke.traces.push(trace);
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
            var drawSpacing = this.radius * this.spacing * midScale;
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
                stroke.traces.push(trace);
                this.draw(canvas, new Trace(lastX, lastY, trace.p, new Date().getTime()));
            } else {
                while (distance >= drawSpacing) {
                    var tx = Math.cos(direction);
                    var ty = Math.sin(direction);
                    lastX += tx * drawSpacing;
                    lastY += ty * drawSpacing;
                    prevP += scaleSpacing;
                    distance -= drawSpacing;
                    stroke.traces.push(trace);
                    this.draw(canvas, new Trace(lastX, lastY, prevP, new Date().getTime()));
                }
            }
        }
    };
};

var brush;
var stroke;
var isLocked;
var isDrawing;

function getPressure(wacom) {
    if (wacom === undefined) {
        return 0.5
    } else {
        return wacom.pressure
    }
}

function getGlobalCompositeOperation(wacom) {
    var destinationOut = 'destination-out';
    var sourceOver = 'source-over';
    if (wacom === undefined) {
        if ($('#eraser').is(':checked')) {
            return destinationOut
        } else {
            return sourceOver
        }
    } else {
        if (wacom.isEraser) {
            return destinationOut
        } else {
            return sourceOver
        }
    }
}

$(document).ready(function() {
    var wacom = document.getElementById('wacom').penAPI;
    var strokes = [];
    var save = $('#save');
    var canvas = $('#canvas');
    canvas.on('mousedown', function(e) {
        if (!isLocked) {
            isLocked = true;
            $('#width').prop('disabled', true);
            $('#height').prop('disabled', true);
        }
        isDrawing = true;
        brush = new Brush(
            $('#radius').val(),
            $('#flow').val(),
            $('#spacing').val(),
            $('#color').val(),
            getGlobalCompositeOperation(wacom)
        );
        stroke = new Stroke(brush);
        brush.down(canvas, new Trace(e.offsetX, e.offsetY, getPressure(wacom), new Date().getTime()));
    });
    canvas.on('mousemove', function(e) {
        if (isDrawing) {
            brush.move(canvas, new Trace(e.offsetX, e.offsetY, getPressure(wacom), new Date().getTime()));
        }
    });
    canvas.on('mouseup mouseleave', function() {
        if (stroke) {
            strokes.push(stroke);
        }
        isDrawing = false;
        brush = undefined;
        stroke = undefined;
    });
    save.submit(function(e) {
        $('#submit').prop('disabled', true);
        $.ajax({
            url: save[0].action,
            type: save[0].method,
            dataType: 'json',
            data: {
                title: $('#title').val(),
                description: $('#description').val(),
                canvas: canvas[0].toDataURL(),
                strokes: JSON.stringify(strokes)
            },
            success: function(data) {
                window.location.replace(data.location);
            },
            error: function() {
                $('#submit').prop('disabled', false);
            }
        });
        e.preventDefault();
    });
    var width = $('#width');
    width.on('change', function() {
        canvas[0].width = width.val();
    });
    var height = $('#height');
    height.on('change', function() {
        canvas[0].height = height.val();
    })
});
