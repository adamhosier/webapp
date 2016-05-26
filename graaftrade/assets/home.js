function hideOverlay() {
    $('#overlay').hide();
    var c = $('#content');
    if(c.hasClass('blur')) c.addClass('unblur');
    c.removeClass('blur');
}

function addOverlay(name, url) {
    var c = $('#content');
    c.addClass("blur");
    c.removeClass('unblur');

    $.get(url, function(e) {
        $('#overlay').html('<div class="ui-box large" id="overlay-box" title="' + name + '">' + e + '</div>').show();
        $('#overlay-box').click(function(e) {
           e.stopPropagation();
        });
        updateTitles();
    }).fail(function() {
        setTimeout(hideOverlay, 100);
    });
}

function updateTitles() {
    $('.ui-box[title]').each(function(i){
        $(this).prepend("<h2>" + $(this).attr('title') + "</h2><hr>");
        $(this).removeAttr('title');
    });
}

$(document).ready(function(){

    //get page ready
    $(document.body).wrapInner('<div id="content"></div>');
    $(document.body).append('<div id="overlay"></div>');
    $('#overlay').click(function(){
        hideOverlay();
    });

    //adds titles to content boxes
    updateTitles();

    //changes stocks into links
    $('stock').each(function(i) {
        var t = $(this).text();
        $(this).after('<a class="ui-stock-link" href="stocks.html?name=' + t + '">' + t + '</a>');
        $(this).remove();
    });

    //makes positive values green, and negative values red
    $('.sign-colour').each(function() {
        $(this).removeClass('sign-colour');
        var text = $(this).text();
        var val = parseFloat(text);
        if(val > 0) $(this).addClass('green-text');
        if(val < 0) $(this).addClass('red-text');
    });

    //expanding view
    hideOverlay();
    $('h2').hover(function() {
        $(this).parent().css({'background-color': '#fcfcfc', 'border-color': '#bbb'});
    }, function() {
        $(this).parent().removeAttr('style');
    }).click(function() {
        $('h2').removeAttr('style');
        addOverlay($(this).text(), $(this).parent().attr('datasrc'));
    });

    //hotkeys
    $(document).keyup(function(e) {
        if(e.which == 27) { // esc
            hideOverlay();
        }
    });

    // compare box form submission
    $('#compare-form').submit(function(e) {
        var select1 = $('select[name="compare-option-1"]');
        var select2 = $('select[name="compare-option-2"]');
        var s1 = select1.val();
        var s2 = select2.val();
        select1.removeAttr('style');
        select2.removeAttr('style'); //clear formatting from previous submissions

        success = true; //validation
        if(s1 == null) {
            select1.css('border-color', '#d00');
            success = false;
        }
        if(s2 == null || s1 == s2) {
            select2.css('border-color', '#d00');
            success = false
        }

        if(success) {
            addOverlay(select1.val() + '/' + select2.val(), 'compare.html?s1=' + s1 + '&s2=' + s2);
        }
        return false; //prevent form from submitting
    })
});