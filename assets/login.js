$(document).ready(function(){

    // check for invalid attempt
    if(window.location.href.indexOf("invalid") > -1) {
        $('input[type=text], input[type=password]').css('border-color', '#d00');
    }

    // validate form submission
    $('#login-form').submit(function() {
        var uname = $('input[name=login-username]');
        var pword = $('input[name=login-password]');
        uname.removeAttr('style');
        pword.removeAttr('style');
        var valid = true;
        if(uname.val() == '') {
            uname.css('border-color', '#d00');
            valid = false;
        }
        if(pword.val() == '') {
            pword.css('border-color', '#d00');
            valid = false;
        }
        return valid;
    });

    // home button
    $('h1').click(function() {
      window.location = '/';
    });

    // register validation
    $('#register-form').submit(function(e) {
        var email1 = $('input[name=register-email-1]');
        var email2 = $('input[name=register-email-2]');
        var uname = $('input[name=register-username]');
        var pword1 = $('input[name=register-password-1]');
        var pword2 = $('input[name=register-password-2]');

        $(this).children().removeAttr('style');
        var valid = true;

        var emailRegex = /^[+a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]+$/i; //TODO: caps???
        if(email1.val() != email2.val() || !emailRegex.test(email1.val())) {
            email1.css('border-color', '#d00');
            email2.css('border-color', '#d00');
            valid = false;
        }
        var nameRegex = /^[a-z0-9_-]+$/i;
        if(!nameRegex.test(uname.val())) {
            uname.css('border-color', '#d00');
            valid = false;
        }

        if(pword1.val() != pword2.val() || pword1.val().length < 6) {
            pword1.css('border-color', '#d00');
            pword2.css('border-color', '#d00');
            valid = false;
        }
        return valid;
    })
});
