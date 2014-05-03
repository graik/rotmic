/** Simple Sequence + Annotation display widget using D3 
* requires CSS:
* - axis ... sequence ruler with regular position marks
* - feature-label ... text properties for annotation labels
**/


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
    var container = '' // container element ID
    var svg= null;     // will hold svg component
    
    var seq= ''         // last sequence passed in via load()
    var features = []   // last list of features passed in
       
    // initialization
    function init(container_id){
        container = container_id;
        var e = document.getElementById(container_id);
        w = e.clientWidth; // canvas width in pixels
        h = e.clientHeight; // canvas height
        
        nrows = Math.floor( (h - 2*padding - haxis) / (fh + fgap) );

        // create canvas
        svg = d3.select('#'+container_id).append('svg');
        svg.attr('height', h)
           .attr('width', w);
    }

    // delete and re-instantiate SVG (if any) -- otherwise resizing adds a second one
    function reset(){
        d3.select('svg').remove();
        init(container);
    }
    
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
            console.log('current row: ' + row);
            for (var j=s; j < e; j++ ){
                occupied[row][j] = 1;
            }
        }
        return occupied;
    }    
    
    function load(sequence, seqfeatures){
        seq = sequence;
        features = seqfeatures;
        
        var scale = d3.scale.linear();
        scale.domain([1, seq.length])           // input domain
        scale.range([padding, w-2*padding]);    // normalize to pixel output range
        
        features = features.sort(_cmp_feature_len); // sort features by length
        assign_rows(features, nrows);

        // map each data entry to a *new* (enter.append) rect
        var bars = svg.selectAll('rect')       //empty selection of not yet existing <p> in div
            .data(features)         // connect data
                .enter().append('rect')         // create new rect for each data point
                    .attr('fill', function(d){
                        return d.color;
                    })
                    .attr('stroke-width', 0.3)
                    .attr('stroke', 'grey')
                    .attr('x', function(d){
                        return scale(d.start);
                    })
                    .attr('y', function(d,i){
                        var row = (d.row < nrows ) ? d.row : 0.3 // offset flow-over annotations
                        d.ypos = h - fh - fgap - padding - haxis - row * (fh+fgap);
                        return d.ypos;
                    })
                    .attr('height', function(d){
                        if (d.row == nrows){ return 0.5 * fh ;}
                        return fh;
                    })
                    .attr('width', function(d){
                        return scale(d.end-d.start+1) - scale(1);
                    })
                    .append('title')        // assign mouse-over tooltip
                        .text(function (d){
                            r = d.type + ': ' + d.name;
                            r += '\n[' + d.start + ' - ' + d.end + ']';
                            return r;
                        });
        
        // put labels centered within annotation bars
        var labels = svg.selectAll('text').data(features).enter().append('text')
            .text(function(d){  // create text label with strand info unless too long
                var r = d.name;
                if (d.strand == 1){ r = '>'+r};
                if (d.strand == -1){r = r + '<'};
                var estimated_size = r.length * 6.5;
                if ( estimated_size < scale(d.end-d.start) ){ 
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
            .attr("fill", "black");

        var xAxis = d3.svg.axis();
        xAxis.scale(scale);
        svg.append("g")
            .attr("class", "axis")  //Assign "axis" class from custom CSS
            .attr("transform", "translate(0," + (h - (haxis +padding)) + ")") // move from top to bottom
            .call(xAxis);
    }

    // call again when resizing
    window.addEventListener('resize', function(event){
        reset();
        seqdisplay.load(seq, features);
    });


    // define public methods
    return {
        init : init,
        load : load,
        reset: reset
    }
}();
