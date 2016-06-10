$(document).ready(function() {
    var max_fields      = 10; //maximum input boxes allowed
    var wrapper         = $(".input_fields_wrap"); //Fields wrapper
    var add_button      = $(".add_field_button"); //Add button ID
    
    var x = 1; //initlal text box count
    $(add_button).click(function(e){ //on add input button click
        e.preventDefault();
        if(x < max_fields){ //max input box allowed
            x++; //text box increment
            $(wrapper).append('<div class=" input-group input-group-option col-xs-12 margin-b-5"><input type="text" name="repo_url'+x+'" class="form-control" placeholder="" autofocus required><span class="input-group-addon input-group-addon-remove btn-danger remove_field"><span class="glyphicon glyphicon-trash"></span></span></div>'); 
        }
    });
    
    $(wrapper).on("click",".remove_field", function(e){ //user click on remove text
        e.preventDefault(); $(this).parent('div').remove(); x--;
    })
});