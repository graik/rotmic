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
    var fh= 12;  // feature bar height in pixles
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
        return len_a < len_b ? -1 : len_a > len_b ? 1 : 0;
    }    
    
    function load(sequence, seqfeatures){
        seq = sequence;
        features = seqfeatures;
        
        var scale = d3.scale.linear();
        scale.domain([1, seq.length])           // input domain
        scale.range([padding, w-2*padding]);    // normalize to pixel output range
        
        features = features.sort(_cmp_feature_len); // sort features by length

        // map each data entry to a *new* (enter.append) rect
        var bars = svg.selectAll('rect')       //empty selection of not yet existing <p> in div
            .data(features)         // connect data
                .enter().append('rect')         // create new rect for each data point
                    .attr('fill', function(d){
                        return d.color;
                    })
                    .attr('x', function(d){
                        return scale(d.start);
                    })
                    .attr('y', function(d,i){
                        d.ypos = fh + i*(fh+4);
                        return d.ypos;
                    })
                    .attr('height', fh)
                    .attr('width', function(d){
                        return scale(d.end-d.start+1) - scale(1);
                    });
        // now look at layouts:   https://github.com/mbostock/d3/wiki/SVG-Shapes
        // or constraint relaxation: http://grokbase.com/t/gg/d3-js/139k13sm0v/force-layout-for-static-chart-label-placement
        
        // put labels centered within annotation bars
        var labels = svg.selectAll('text').data(features).enter().append('text')
            .text(function(d){
                var estimated_size = d.name.length * 6;
                if ( estimated_size < scale(d.end-d.start) ){ 
                    return d.name;
                }
            })
            .attr('x', function(d){
                var r = d.start + (d.end - d.start)/2
                return scale(r);
            })
            .attr('y', function(d,i){
                return d.ypos + fh - 2;
            })
            .classed("feature-label", true)  // apply text style from CSS
            .attr("text-anchor", "middle")
            .attr("fill", "black");

        var xAxis = d3.svg.axis();
        xAxis.scale(scale);
        svg.append("g")
            .attr("class", "axis")  //Assign "axis" class from custom CSS
            .attr("transform", "translate(0," + (h - (20 +padding)) + ")") // move from top to bottom
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
