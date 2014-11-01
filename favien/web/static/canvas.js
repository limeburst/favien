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

var Brush = function(size, flow, spacing, fillStyle, globalCompositeOperation) {
    var distance;
    var prevX;
    var prevY;
    var prevP;
    var lastX;
    var lastY;
    var direction;
    this.name = 'arc';
    this.size = size;
    this.flow = flow;
    this.spacing = spacing;
    this.fillStyle = fillStyle;
    this.globalCompositeOperation = globalCompositeOperation;
    this.draw = function(canvas, trace) {
        var ctx = canvas[0].getContext('2d');
        ctx.globalAlpha = this.flow / 100;
        ctx.fillStyle = this.fillStyle;
        ctx.globalCompositeOperation = this.globalCompositeOperation;
        ctx.beginPath();
        ctx.arc(trace.x, trace.y, trace.p * this.size / 2, 0, Math.PI * 2);
        ctx.fill();
        ctx.closePath();
    };
    this.down = function(canvas, trace) {
        lastX = prevX = trace.x;
        lastY = prevY = trace.y;
        prevP = trace.p;
        distance = 0;
        this.draw(canvas, trace);
    };
    this.move = function(canvas, trace) {
        if (this.spacing === null) {
            this.draw(canvas, trace);
            return
        }
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
        var drawSpacing = this.size * this.spacing / 100 * midScale;
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
            this.draw(canvas, new Trace(lastX, lastY, trace.p, trace.t));
        } else {
            while (distance >= drawSpacing) {
                var tx = Math.cos(direction);
                var ty = Math.sin(direction);
                lastX += tx * drawSpacing;
                lastY += ty * drawSpacing;
                prevP += scaleSpacing;
                distance -= drawSpacing;
                this.draw(canvas, new Trace(lastX, lastY, prevP, trace.t));
            }
        }
    };
};

function getSpacing() {
    var sliderValue = spacingSlider.val();
    if (spacing.is(':checked')) {
        if (sliderValue <= 100) {
            return sliderValue
        } else if (sliderValue > 100) {
            return 100 + (sliderValue - 100) * 9
        }
    } else {
        return null
    }
}

function getPressure() {
    var defaultPressure = 0.5;
    if (tablet.is(':checked')) {
        if (wacom === undefined) {
            return defaultPressure
        } else {
            return wacom.pressure
        }
    } else {
        return defaultPressure
    }
}

function getGlobalCompositeOperation() {
    var destinationOut = 'destination-out';
    var sourceOver = 'source-over';
    var defaultOperation;
    if (eraser.is(':checked')) {
        defaultOperation = destinationOut
    } else {
        defaultOperation = sourceOver
    }
    if (tablet.is(':checked')) {
        if (wacom === undefined) {
            return defaultOperation
        } else {
            if (wacom.isEraser) {
                return destinationOut
            } else {
                return sourceOver
            }
        }
    } else {
        return defaultOperation
    }
}

function replayStroke() {
    if (strokes.length) {
        var replayCanvas = $('#replay-canvas');
        var stroke = strokes.shift();
        var brush = new Brush(
            stroke.brush.size,
            stroke.brush.flow,
            stroke.brush.spacing,
            stroke.brush.fillStyle,
            stroke.brush.globalCompositeOperation
        );
        brush.down(replayCanvas, stroke.traces.shift());
        while (stroke.traces.length) {
            brush.move(replayCanvas, stroke.traces.shift());
        }
    }
}

var brush;
var stroke;
var isLocked;
var isDrawing;
var strokes = [];

var canvas = $('#canvas');
var color = $('#color');
var description = $('#description');
var eraser = $('#eraser');
var height = $('#height');
var replayButton = $('#replay');
var save = $('#save');
var spacing = $('#spacing');
var submit = $('#submit');
var tablet = $('#tablet');
var title = $('#title');
var width = $('#width');
if (canvas.length) {
    var wacom = document.getElementById('wacom').penAPI;
}

var flowLabel = $('label[for=flow-slider]');
var flowSlider = $('#flow-slider');
var sizeLabel = $('label[for=size-slider]');
var sizeSlider = $('#size-slider');
var spacingLabel = $('label[for=spacing-slider]');
var spacingSlider = $('#spacing-slider');
width.on('change', function() {
    canvas[0].width = width.val();
});
height.on('change', function() {
    canvas[0].height = height.val();
});
sizeSlider.on('input', function() {
    sizeLabel.text(sizeSlider.val() + 'px');
});
flowSlider.on('input', function() {
    flowLabel.text(flowSlider.val() + '%');
});
spacingSlider.on('input', function() {
    var spacing = getSpacing();
    if (spacing !== null) {
        spacingLabel.text(spacing + '%');
    }
});

canvas.on('mousedown', function(e) {
    var pressure = getPressure();
    if (pressure !== 0) {
        if (!isLocked) {
            isLocked = true;
            width.prop('disabled', true);
            height.prop('disabled', true);
        }
        isDrawing = true;
        brush = new Brush(
            sizeSlider.val(),
            flowSlider.val(),
            getSpacing(),
            color.val(),
            getGlobalCompositeOperation()
        );
        stroke = new Stroke(brush);
        var trace = new Trace(
            e.offsetX,
            e.offsetY,
            pressure,
            new Date().getTime()
        );
        stroke.traces.push(trace);
        brush.down(canvas, trace);
    }
});
canvas.on('mousemove', function(e) {
    if (isDrawing) {
        var trace = new Trace(
            e.offsetX,
            e.offsetY,
            getPressure(),
            new Date().getTime()
        );
        stroke.traces.push(trace);
        brush.move(canvas, trace);
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
    submit.prop('disabled', true);
    $.ajax({
        url: save[0].action,
        type: save[0].method,
        dataType: 'json',
        data: {
            title: title.val(),
            description: description.val(),
            replay_allowed: $('#replay_allowed:checked').val(),
            width: canvas[0].width,
            height: canvas[0].height,
            canvas: canvas[0].toDataURL(),
            strokes: JSON.stringify(strokes)
        },
        success:  function(data) {
            window.location.replace(data.location);
        },
        error: function() {
            submit.prop('disabled', false);
        }
    });
    e.preventDefault();
});

replayButton.on('click', function() {
    var replayCanvas = $('#replay-canvas');
    var canvas = $('<canvas></canvas>')
        .attr('id', 'replay-canvas')
        .attr('width', replayCanvas.width())
        .attr('height', replayCanvas.height());
    replayCanvas.replaceWith(canvas);
    $.get('strokes/', function (data) {
        strokes = data.strokes;
        setInterval(replayStroke, 10);
    });
});
