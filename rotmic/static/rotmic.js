/** Helper JS for rotmic
**/

// see: http://blog.movalog.com/a/javascript-toggle-visibility/ 
//toggle visibility of one HTML element    
function toggle_visibility(id) {
    var e = document.getElementById(id);
    if((e.style.display == 'block') || (e.style.display == ''))
        e.style.display = 'none';
    else
        e.style.display = 'block';
};

//switch visibility between two or more HTML elements
// id_off can be either a single element ID or an array of element IDs to be switched off
function toggle_between(id_on, id_off) {
    var e_on = document.getElementById(id_on);
    e_on.style.display = 'block';
   
    if (id_off instanceof Array){
        for (var i=0; i<id_off.length; i++){
            var e_off= document.getElementById(id_off[i]);
            e_off.style.display= 'none';
        }
    } else {
        var e_off= document.getElementById(id_off);
        e_off.style.display= 'none';
    }
};

