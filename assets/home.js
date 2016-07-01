var STOCK_UPDATE_INTERVAL = 3000;
var STOCK_SEARCH_PAUSE_TIMEOUT = 450;
var overlay_active = false;
var lastupdate = Math.floor(Date.now() / 1000);

function postChatMessage(broker, content, fromUs) {
    var classname = fromUs ? 'user-chat' : 'partner-chat';
    $('#chat-box-' + broker + ' ul').append('<li class="' + classname + '"><span>' + content + '</span></li>');
    chatScrollBottom();
}

function chatScrollBottom() {
  $('.chat-box ul').each(function() {
    var ul = $(this);
    ul.scrollTop(ul[0].scrollHeight - ul.height() - 5);
  });
}

function beautifyMoney() {
    $('.money').each(function() {
      var elem = $(this);
      var val = elem.text().substring(1);
      var dpval = '' + parseFloat(val).toFixed(2);
      var newval = dpval;
      if(dpval.length >= 6) {
        newval = dpval.substr(dpval.length - 6); 
        var i;
        for(i = dpval.length - 6; i > 2; i -= 3) {
          newval = dpval.substr(i - 3, i) + ',' + newval;
        }
        if(i > 0) newval = dpval.substr(0, i) + ',' + newval;
      }
      elem.html('£' + newval);
      $(this).removeClass('money').addClass('gold');
    });
}

function hideOverlay() {
    overlay_active = false;
    $('#overlay').hide();
    var c = $('#content');
    if(c.hasClass('blur')) c.addClass('unblur');
    c.removeClass('blur');
}

function addOverlay(name, url) {
    overlay_active = true;
    var c = $('#content');
    c.addClass("blur");
    c.removeClass('unblur');

    $.get(url, function(e) {
        $('#overlay').html('<div class="ui-box large" id="overlay-box" title="' + name + '">' + e + '</div>').fadeIn(150);
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
        var content = $('<div class="box-content"></div>');
        $(this).wrapInner(content);
        $(this).prepend("<h2>" + $(this).attr('title') + '</h2>').removeAttr('title');
    });
}

function initSearch(elem) {
    var name = elem.attr('name');
    var searchTimeout;
    elem.keyup(function() {
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(function() {
        var box = $('#search-box-' + name);
        box.empty();
        var str = elem.val();
        if(str == '') {
          box.hide();
        } else {
          $.get('stock/search/' + str, function(data) {
            if(data.length == 0) {
              box.hide();
            } else {
              for(i in data) {
                if(name == 'global') {
                  var span = $('<span><stock>' + data[i]['ticker'] + '</stock></span>').click(function() {
                    box.hide();
                  });
                  var icon1 = $('<span class="right ui-icon ui-icon-plusthick">').click(function() { 
                    var stock = $(this).siblings().first().text();
                    window.location='stock/add/' + stock;
                  });
                  var icon2 = $('<span class="right ui-icon ui-icon-star">').click(function() { 
                    var stock = $(this).siblings().first().text();
                    window.location='watch/add/' + stock;
                  });
                  span.append('<p class="stock-name">' + data[i]['name'] + '</p>').append(icon1).append(icon2);
                  box.append(span);
                } else {
                  var span = $('<span>' + data[i]['ticker'] + '</span>').click(function() {
                    elem.val($(this).text());
                    box.hide();
                  });
                  box.append(span);
                }
              }
              updateStockLinks();
              box.show();
            }
          });
        }
      }, STOCK_SEARCH_PAUSE_TIMEOUT);
    });
}

function updateStockColors() {
    //makes positive values green, and negative values red
    $('.sign-colour').each(function() {
        var text = $(this).text();
        var val = parseFloat(text).toFixed(2);
        $(this).text(val);
        if(val > 0) $(this).addClass('green-text').prepend('+');
        if(val < 0) $(this).addClass('red-text');
    });
}

function updatePositions() {
  $('.search').each(function() {
    var elem = $(this);
    var box = $('#search-box-' + elem.attr('name'));
    box.css({
      left   : elem.position().left,
      top    : elem.position().top + elem.outerHeight() - 1,
      width  : elem.outerWidth() - 2,
    });
  });
  $('.chat-box').each(function() {
    var box = $(this);
    var bar = $('#chat-bar-' + box.attr('id').substr("chat-box-".length));
    box.css({
      left  : bar.position().left + 4,
      top   : -box.outerHeight(),
    }); 
  });
}	

function updateBrokerChatLinks() {
  $('a.ui-chat-link').click(function() {
    var id = $(this).attr('name');
    $.get('/home/openchat/' + id, function(data) {
      hideOverlay();
      if(data.length == 0) {
        var box = $('#chat-box-' + id);
        chatScrollBottom();
        box.show();
        return; 
      }
      var bar = $('<div class="footer-chat" id="chat-bar-' + data['id'] + '">' + data['name'] + '</div>');
      var box = $(data['chat_box']);
      $('#footer-content').append(bar).append(box);
      updateChatBar();
      updatePositions();
    });
  });
}

function getToken() {
  str = ';' + document.cookie;
  parts = str.split(';csrftoken=');
  return parts.pop().split(';').shift();
}

function updateChatBar() {
  $('.footer-chat').unbind('click');
  $('.footer-chat').click(function() {
    var bar = $(this);
    var boxselector = '#chat-box-' + bar.attr('id').substr("chat-bar-".length);
    var box = $(boxselector);
    box.toggle();
    chatScrollBottom();
  });

  $('.chat-input').keyup(function(e) {
    var elem = $(this);
    var input = elem.val();
    var broker = elem.parent().attr('id').substr(9);
    if(input != '' && e.keyCode == 13) {
      elem.val(''); 
      $.post('/chatupdate', { broker:broker, msg:input, csrfmiddlewaretoken:getToken() }, function(data) {
        postChatMessage(broker, input, true);
      });
    }
  });
}

function flashUpdate(data, i) {
  setTimeout(function() {
    if(overlay_active) return;
    var j = parseInt(i) + 1;
    var priceElem = $('#stock-table tr:eq(' + j + ') td:eq(1)');
    var changeElem = $('#stock-table tr:eq(' + j + ') td:eq(2)');
    var amountElem = $('#stock-table tr:eq(' + j + ') td:eq(3)');
    var valueElem = $('#stock-table tr:eq(' + j + ') td:eq(4)');
    var change = data[i]['price'] - parseFloat(priceElem.text().substring(1));
    priceElem.text('£' + data[i]['price']);
    changeElem.html('<span class="sign-colour">' + data[i]['change'] + '</stock>'); //change
    var newvalue = parseFloat(priceElem.text().substring(1)) * parseInt(amountElem.text());
    valueElem.html('<span class="money">£' + newvalue + "</span>");
    // flash green or red based on the change
    if(change != 0) {
      var row = $('#stock-table tr:eq(' + j + ')');
      var overlay = $('<div class="stock-row-overlay"></div>').css({
        'left'            : row.position().left,
        'top'             : row.position().top,
        'width'           : row.width(),
        'height'          : row.height(),
        'background-color': (change > 0) ? 'rgba(0, 192, 0, 0.5)' : 'rgba(192, 0, 0, 0.5)',
      });
      $(document.body).append(overlay);
      overlay.fadeOut(500, function() { 
        $(this).remove();
      });
      var totalElem = $('#money-total');
      var newtotal = parseFloat(totalElem.text().substr(1).replace(',','')) + change;
      totalElem.text('£' + newtotal).addClass('money');
      beautifyMoney();
    }
    beautifyMoney();
    updateStockColors();
  }, i* 250 );
}

function updateStockLinks() {
  $('stock').each(function() {
      var t = $(this).text();
      $(this).after(function() {
        return $('<a class="ui-stock-link">' + t + '</a>').click(function() {
          addOverlay(t + " Summary", "/stock/" + $(this).text());
        });
      });
      $(this).remove();
  });
}

$(document).ready(function(){
    $('#settings-button').click(function() {
      window.location = '/logout';
    });
    //get page ready
    $(document.body).wrapInner('<div id="content"></div>').append('<div id="overlay"></div>');
    $('.search').each(function() {
      $(document.body).append('<div class="search-box" id="search-box-' + $(this).attr('name') + '"><table></table></div>');
    });
    $('#overlay').click(function(){
        hideOverlay();
    });

    //adds titles to content boxes
    updateTitles();

    //changes stocks into links
    updateStockLinks();
 
    //changes brokers into links
    $('broker').each(function() {
        var t = $(this).text();
        var id = this.id
        $(this).after(function() {
          return $('<a class="ui-broker-link">' + t + '</a>').click(function() {
            addOverlay(t, "/broker/" + id);
          });
        });
        $(this).remove();
    });

    updateStockColors();

    //expanding view
    hideOverlay();
    $('h2').each(function() {
      var parent = $(this).parent();
      if(parent.attr('expandable') != undefined) {
        $(this).hover(function() {
            parent.css({'background-color': '#fcfcfc', 'border-color': '#bbb'});
        }, function() {
            parent.removeAttr('style');
        }).click(function() {
            $('h2').removeAttr('style');
            addOverlay($(this).text(), parent.attr('datasrc'));
        }).addClass('pointer');
      }
    });

    //hotkeys
    $(document).keyup(function(e) {
        if(e.which == 27) { // esc
            hideOverlay();
        }
    });

    // compare box form submission
    $('#compare-form').submit(function(e) {
        var select1 = $('#compare1-search');
        var select2 = $('#compare2-search');
        var s1 = select1.val();
        var s2 = select2.val();
        select1.removeAttr('style');
        select2.removeAttr('style'); //clear formatting from previous submissions

        success = true; //validation
        if(s1 == '') {
            select1.css('border-color', '#d00');
            success = false;
        }
        if(s2 == '' || s1 == s2) {
            select2.css('border-color', '#d00');
            success = false
        }

        if(success) {
            addOverlay(select1.val() + '/' + select2.val(), 'compare/' + s1 + '&' + s2);
        }
        return false; //prevent form from submitting
    })

    // stock search
    $(document).mousedown(function(e) {
      if($(e.target).closest('.search-box').length == 0) {
        $('.search-box').hide();
      }
    })
    $('.search').each(function() {
      initSearch($(this));
    });

    // update stocks and chat
    setInterval(function() {
        if(overlay_active) return;
        $.get('home/update/' + lastupdate, function(data) {
           lastupdate = Math.floor(Date.now() / 1000);
           for(i in data['stock']) {
             flashUpdate(data['stock'], i)
           }
           for(id in data['chat']) {
             newmsgs = data['chat'][id];
             for(i in newmsgs) {
               postChatMessage(id, newmsgs[i], false);
             }
           }
        });
    }, STOCK_UPDATE_INTERVAL);

    //editable spans
    $('span.editable').click(function() {
      var elem = $(this);
      var val = elem.text();
      var input = $('<input type="text" class="ui-editable-stock">').blur(function() {
        window.location = 'stock/update/' + elem.attr('name') + '/' + $(this).val();
      }).val(val).keypress(function(e) {
        if(e.which == 13)
          window.location = 'stock/update/' + elem.attr('name') + '/' + $(this).val();
      });
      elem.parent().append(input);
      elem.remove();
      input.focus();
    });

    beautifyMoney()
 
    updateChatBar();

    $(window).resize(updatePositions);
    updatePositions();
    
    var get = window.location.search.replace("?", "").split('=');
    if(get[0] == 'added') {
      var ticker = get[1].replace(".", "\.")
      var cell = $("#row-" + ticker + " td:eq(3) span");
      cell.trigger('click');
      cell.children().first().focus();
    }
        
});
