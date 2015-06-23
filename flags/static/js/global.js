$(function() {
    //SHOWING AN INPUT FIELD DYNAMICALLY
    $('.add-text').click(function(e) {
        $(this).next().show();
        $(this).next().find(".add-form-input").focus();
        $(this).hide();
    });

    //DELETE CONFIRMATION
    $('.delete').click(function(e) {
        if(confirm('Are you sure you want to delete?')) {
            //Add confirm action here
        } else {
            e.preventDefault();
            return;
        }
    });

    //ON PAGE LOAD, FIND ALL OPTIONS THAT ARE HIDDEN, AND HIDE ITS CHILDREN
    $(".block-header .ios-toggle").each(function( index ) {
        if (!$(this).is(':checked')) {
            $(this).parent().parent().parent().find(".options-block").hide();
        }
    });

    //TOGGLING THE IOS STYLE CHECK BOXES
    $('.ios-toggle').click(function(e) {
        parent_div = $(this).parent().parent().parent();

        if ($(this).parent().hasClass("header-switch")) {
            parent_div.find(".segmentation-block").fadeToggle("fast");
        }

        parent_div.find(".options-block").fadeToggle("fast");

        if ($(this).is(':checked')) {
        } else {
            parent_div.find("input:checkbox").each(function() {
                this.checked = false;
            });
        }
    });
});