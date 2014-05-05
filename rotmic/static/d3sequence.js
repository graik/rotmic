/** Rotten Microbes (rotmic) -- Laboratory Sequence and Sample Management
## Copyright 2013 - 2014 Raik Gruenberg

## This file is part of the rotmic project (https://github.com/graik/rotmic).
## rotmic is free software: you can redistribute it and/or modify
## it under the terms of the GNU Affero General Public License as
## published by the Free Software Foundation, either version 3 of the
## License, or (at your option) any later version.

## rotmic is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Affero General Public License for more details.
## You should have received a copy of the GNU Affero General Public
## License along with rotmic. If not, see <http://www.gnu.org/licenses/>.
**/
/** Simple Sequence + Annotation display widget using D3 
* requires CSS:
* - axis ... sequence ruler with regular position marks
* - feature-label ... text properties for annotation labels
*
* Usage:
* <div id='containerElementId'></div>
* seqdisplay.init('containerElementID');
* seqdisplay.load(sequence, features);
*
* Features should look like this:
[
 { 'name': "name",
   'color': "#FFFFFF",
   'start': 1,
   'end': 100,
   'strand' : 1,
   'type' : "CDS" },
]
**/

// D3 crash course: http://www.cc.gatech.edu/~stasko/7450/Chad-D3-Crash-Course-Slides.pdf
// module layout inspired by http://christianheilmann.com/2008/05/23/script-configuration/
// D3 code adapted from: http://alignedleft.com/tutorials/d3
var seqdisplay = function(){
    
    var w = 100; // canvas width, will be taken from parent container    
    var h = 100; // canvas height in pixels
    var fh= 13;  // feature bar height in pixles
    var fgap= 8; // gap or padding between feature bars
    var haxis= 20; // assumed axis height in pixels
    var nrows = 4; // number of rows available for placing annotations; will be calculated
    var padding = 5;  // right and left margin in pixels
    var arrowhead = 5; // length of arrow-head tip of annotations 
    var e_id = ''; // container element ID
    var econtainer;         // container element

    var svg;        // will hold svg component

    var scale = d3.scale.linear(); // x-dimension scaling; set in load()
    
    var seq= '';         // last sequence passed in via load()
    var features = [];   // last list of features passed in
    
    var z_scale = 1;      // current zoom scale
    var z_trans = 0;      // current panning move in x direction

    var zoomX = d3.behavior.zoom()  // zoom "behaviour"
        .scaleExtent([1.0, 100.0])
        .on("zoom", zoomHandler);


       
    // initialization
    function init(container_id){
        e_id = container_id;
        econtainer = document.getElementById(container_id);
        // create canvas
        svg = d3.select('#'+container_id).append('svg');
        
        svg.call(zoomX);
        
        dimensions();
    }
    
    // move this closer to load so that dimensions are decided just before
    // drawing ... otherwise too broad dimension is assumed if page built-up
    // hasn't yet introduced scroll bar. Putting the method into the page
    // footer or register a resize event listener on parent element?
    // (re-) assign canvas dimensions after re-size    
    function dimensions(){
        w = econtainer.clientWidth; // canvas width in pixels
        h = econtainer.clientHeight; // canvas height
        
        nrows = Math.floor( (h - 2*padding - haxis) / (fh + fgap) );

        svg.attr('height', h)
           .attr('width', w);
    }

    // clear all content of SVG; re-assign box dimensions
    function reset(){
        svg.selectAll('*').remove();
        dimensions();
    }    
    
    // function for handling zoom event
    function zoomHandler() {
        var x = zoomX.translate()[0];
        var z = zoomX.scale();
        var weff = w - padding*2
        
        var maxdelta = (weff*z - weff); // maximal shift in x before hitting end
        
        if (x > 0){ zoomX.translate([0,0]) }
        if (x < -maxdelta ){ zoomX.translate([-maxdelta, 0]) }
        
        x = zoomX.translate()[0];

        var seqwindow = Math.ceil( seq.length / z) // new length of sequence segment to show

        var seqdelta = 0;
        if (maxdelta != 0){
            seqdelta = -1 * x / maxdelta * (seq.length - seqwindow);
        }

        scale.domain([1 + seqdelta - 0.5, seqdelta + seqwindow + 0.5]);
            
        reset();
        redraw();

        z_scale = z;
        z_trans = x;
    }

    // comparison function for sorting features by length (decending)
    function _cmp_feature_len(a, b){
        len_a = a.end - a.start;
        len_b = b.end - b.start;
        return len_a < len_b ? 1 : len_a > len_b ? -1 : 0;
    }    

    // create 2-D array of zeros    
    function _zeros(x,y){
        var r = new Array(x);
        for (var i=0; i < x; i++){
            var yarray = new Array(y);
            for (var j=0; j < y; j++){
                yarray[j] = 0;
            }
            r[i] = yarray;
        }
        return r;
    } 
    
    //return true if there is any non-zero value in a[row, start..end]
    function _nonzero(a, row, start, end){
        for (var j=start; j < end; j++){
            if ( a[row][j] > 0 ){ return true; };
        }
        return false;
    }
    
    // requires seq being set in module namespace    
    function assign_rows(features, n_rows){
        var occupied = _zeros(n_rows+1, seq.length);
        
        for (var i=0; i < features.length; i++){
            row = 0;
            s = features[i].start - 1;
            e = features[i].end;
            while ((row < n_rows) && _nonzero(occupied, row, s, e)){
                row++;
            }
            //if (row == n_rows){ row = 0 }; // hack: shift last comming to first row.
            features[i].row = row;
            for (var j=s; j < e; j++ ){
                occupied[row][j] = 1;
            }
        }
        return occupied;
    }
    
    // create svg:polygon point string for a rectangle with sharp tip
    // see: http://stackoverflow.com/questions/13204562/proper-format-for-drawing-polygon-data-in-d3
    function _polygon_points(x,y,height, width, strand){
        var tip = (width >= arrowhead) ? arrowhead : 0;
        var points;
        if (strand==1){
            points = [  {'x': x,           'y':y},
                        {'x': x+width-tip, 'y':y},
                        {'x': x+width,     'y':y + height/2},
                        {'x': x+width-tip, 'y':y + height},
                        {'x': x,           'y':y + height}
                     ]
        } else {
            points = [  {'x': x+tip,       'y':y},
                        {'x': x+width,     'y':y},
                        {'x': x+width,     'y':y + height},
                        {'x': x+tip,       'y':y + height},
                        {'x': x,           'y':y + height/2}
                     ]
        }
        var p_str = points.map( function(d){ 
                        return [Math.round(d.x), Math.round(d.y)].join(','); 
                    } ).join(' ');
        return p_str;
    }
    
    // from: http://stackoverflow.com/questions/5623838/rgb-to-hex-and-hex-to-rgb
    // hex - str with HTML color code    
    function _hexToRgb(hex) {
        var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
        return result ? {
            red:   parseInt(result[1], 16),
            green: parseInt(result[2], 16),
            blue:  parseInt(result[3], 16)
        } : null;
    }
    
    // return black or white text color depending on background color hue.
    // http://stackoverflow.com/questions/3942878/how-to-decide-font-color-in-white-or-black-depending-on-background-color
    function _text_color(bgcolor){
        c = _hexToRgb(bgcolor);
        // note: real midline is 186 but I prefer black in the middle color range
        if ((c.red*0.299 + c.green*0.587 + c.blue*0.114) > 140) { return '#000000';};
        return '#ffffff';
    }
    
    // requires sequence variable set
    // split end-spanning features in two and sort features by length
    function clean_features(seqfeatures){
        for (var i=0; i<seqfeatures.length; i++){
            d = seqfeatures[i];
            if (d.start > d.end){
                var fnew  = {'start':1, 'end':d.end, 'name': '...'+d.name,
                    'type': d.type, 'strand':d.strand, 'color':d.color};
                d.end = sequence.length;
                d.name = d.name + '...';
                seqfeatures.push( fnew ); // append second half of end-spanning feature
            }
        }
        seqfeatures = seqfeatures.sort(_cmp_feature_len); // sort features by length
        return seqfeatures;    
    }
    
    // sequence - str, raw sequence
    // seqfeatures - [ {} ], list of feature records with start, end, color, type, name
    function load(sequence, seqfeatures){
        seq = sequence || seq;
        
        if (seqfeatures){    
            features = clean_features( seqfeatures );
        }
        
        scale.range([padding, w-padding]);    // normalize to pixel output range
        scale.domain([1 - 0.5, seq.length + 0.5])         // input domain !!
        
        assign_rows(features, nrows);
        
        redraw();
    }

    function redraw(){

        var show_sequence = ((scale(2) - scale(1)) > 7);
        var s_start = Math.floor(scale.domain()[0]);
        var s_end = Math.ceil(scale.domain()[1]);
        
        var visible_features = features.filter(function(d){
                return ((d.start <= s_end) && (d.end >= s_start))
            });

        // map each data entry to a *new* (enter.append) rect
        var bars = svg.append('g').selectAll('rect')       //empty selection of not yet existing <p> in div
            .data(visible_features)                    // connect data
                .enter().append('polygon')     // create new polygon for each data point
                    .attr('fill', function(d){
                        return d.color;
                    })
                    .attr('stroke-width', 0.3)
                    .attr('stroke', 'grey')
                    .attr('points', function(d){
                        var margin = 0.5; // move half letter left and right as start and end are included in feature
                        var x = scale(d.start - margin);
                        var row = (d.row < nrows ) ? d.row : 0.3 // offset flow-over annotations
                        d.ypos = h - fh - fgap - padding - haxis - 10 - row * (fh+fgap);
                        var y = d.ypos;
                        var height = (d.row == nrows) ? 0.5 * fh : fh; // half-height for overflow features
                        var width = scale(d.end+margin)-scale(d.start-margin);
                        return _polygon_points(x, y, height, width, d.strand);
                    });
                    
        var tooltips = bars.append('title')        // assign mouse-over tooltip
                        .text(function (d){
                            r = d.type + ': ' + d.name;
                            r += (d.strand==1) ? '\n---->' : '\n<----';
                            r += '\n[' + d.start + ' - ' + d.end + ']';
                            return r;
                        });
        
        // put labels centered within annotation bars
        var labels = svg.append('g').selectAll('text').data(visible_features)
            .enter().append('text')
            .text(function(d){  // create text label with strand info unless too long
                var r = d.name;
                var estimated_size = r.length * 6.5;
                if ( estimated_size < (scale(d.end) - scale(d.start)) ){ 
                    return r;
                }
            })
            .attr('x', function(d){
                var r = d.start + (d.end - d.start)/2
                return scale(r);
            })
            .attr('y', function(d,i){
                return d.ypos + fh - 3;
            })
            .classed("feature-label", true)  // apply text style from CSS
            .attr("text-anchor", "middle")
            .attr("fill", function(d){
                return _text_color(d.color);
            });
        
        if (show_sequence){
            // only show letters that are within visible range (large speedup)
            seq_array = seq.slice( s_start, s_end ).split('');
            var seqletters = svg.append('g').selectAll('text').data(seq_array)
                .enter().append('text')
                    .text(function(d){
                        return d;
                    })
                    .attr('x', function(d,i){
                        return scale(s_start + i + 1);
                    })
                    .attr('y', h -fgap/2 - padding - haxis )
                    .attr('text-anchor', 'middle')
                    .attr('fill', 'black');
        }
        
        var xAxis = d3.svg.axis()           // xAxis is NOT an object or selection but a function
                            .scale(scale);  // ...creating an axis for whatever is passed in as it's argument
        svg.append("g")
            .attr("class", "axis")  //Assign "axis" class from custom CSS
            .attr("transform", "translate(0," + (h - (haxis +padding)) + ")") // move from top to bottom
            .call(xAxis);           // call xAxis function and pass selection as parameter
    }

    // call again when resizing
    window.addEventListener('resize', function(event){
        reset();
        dimensions();
        seqdisplay.load();
    });


    // define public methods
    return {
        init : init,
        load : load,
        reset: reset
    }
}();
