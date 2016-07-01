$(document).ready(function() {
  $('td[editable], span[editable]').each(function() {
    var elem = $(this);
    elem.css('cursor', 'pointer').click(function() {
      var val = elem.text();
      var input = $('<input type="text" class="ui-editable-field">').css('width', elem.width()).blur(function() {
        window.location = 'broker/update/' + elem.attr('name') + '/' + $(this).val();
      }).val(val).keypress(function(e) {
        if(e.which == 13)
          window.location = 'broker/update/' + elem.attr('name') + '/' + $(this).val();
      });
      elem.replaceWith(input);
      input.focus();
    });
  });
});
