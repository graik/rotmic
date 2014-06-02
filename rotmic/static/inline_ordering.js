// Note: if there are more than one inline blocks on the form, this will propably not work

var ordering = (function($){

    var sort_column = 'position';
    
    $(document).ready(function(){
        initialiseRows();
    });
    
    $('.add-row a').live('click', function(){
        initialiseRows();
    });
    
    $('.inline-deletelink').live('click', function(){
        initialiseRows();
    });
   

    function initialiseRows(){
        var last_so = 0;
    
        $('div.inline-related tbody tr.form-row').not('.empty-form').not('add-row').each(function(i){
            // Gather the required items from this row
            var sort_td = $(this).find('.field-' + sort_column);
            var sort_input = $(this).find('.field-' + sort_column + ' input');
            var this_sort = parseInt(sort_input.val());
    
            // Remove any current movement buttons if this is a reinitialisation
            $(sort_td).find('.moveButton').remove();
    
            // On the off chance any existing bad sort data exists replace it so you always start with a clean order
            if(this_sort != last_so+1){
                $(sort_input).val(last_so+1);
                this_sort = last_so+1;
            }
            // Increment the sort loop value
            last_so = this_sort;
    
            // Setup the up/down button html for this row
            var btnUpHtml = '<input type="button" class="moveButton" title="move one up" value="&#x2b06" onclick="ordering.move(' + i + ', 1)">';
            var btnDownHtml = '<input type="button" class="moveButton" title="move one down" value="&#x2b07" onclick="ordering.move(' + i + ', 0)">';
    
            // Apply the up button to all but the first row
            if(this_sort > 1)
                $(sort_td).append(btnUpHtml);
    
            // Apply the down button to all but the last row
            if(this_sort < $('div.inline-related tbody tr.form-row').not('.empty-form').not('add-row').length)
                $(sort_td).append(btnDownHtml);
    
        });
    
        // Set the default sort of the hidden add row so new items don't jump to the top on save
        $('div.inline-related tbody tr.empty-form').find('.field-' + sort_column + ' input').val(last_so+1);
    }

    function moveRow(i, dir){
        // Grab all rows then find the one we are after and the one to swap it with
        var rows = $('div.inline-related tbody tr.form-row').not('.empty-form').not('add-row');
        var this_row = rows[i];
        var this_sort = parseInt($(this_row).find('.field-' + sort_column + ' input.vIntegerField').val());
        if (dir)
            var swap_row = rows[i-1];
        else
            var swap_row = rows[i+1];
        var swap_sort = parseInt($(swap_row).find('.field-' + sort_column + ' input.vIntegerField').val());

        // Swap the position of the rows and their sort order values
        if (dir)
            $(this_row).after($(swap_row));
        else
            $(swap_row).after($(this_row));
        $(this_row).find('.field-' + sort_column + ' input.vIntegerField').val(swap_sort);
        $(swap_row).find('.field-' + sort_column + ' input.vIntegerField').val(this_sort);

        // Reset the style classes to keep things pretty
        $(this_row).toggleClass('row1 row2');
        $(swap_row).toggleClass('row1 row2');

        // Re-initialise the rows to ensure the right buttons are in the right places
        initialiseRows();
    }

    return {
        move: moveRow,
        init: initialiseRows,
    }

})(django.jQuery);
