function update_abstract(t, hook) {
  $.ajax("/update_abstract", {
    data: {
      "hook": hook
    },
    crossDomain: true,
    dataType: 'json',
    type: "GET",
    success: function(data) {
      if (data != "") {
        var panel_el = $(t).parentsUntil(".panel");
        var coll_el = panel_el.next('.collapse').attr('id');
        $("#" + coll_el).find('.card-block').html(data['abstract']);
        panel_el.find('img.red').attr('class', 'green');
      }
    }
  });
};

// Panel toolbox
$(document).ready(function() {
  $('.refresh-link').on('click', function() {
    var hook = $(this).attr('data-hook');
    var el = $(this);
    $.ajax("/update_abstract", {
      data: {
        "hook": hook
      },
      crossDomain: true,
      dataType: 'json',
      type: "GET",
      beforeSend: function() {
        el.find('.fa').attr('class', 'fa fa-refresh fa-spin fa-fw');
      },
      complete: function() {
        el.find('.fa').attr('class', 'fa fa-refresh');
      },
      success: function(data) {
        if (data != "") {
          var panel_el = el.parentsUntil(".x_panel");
          var coll_el = panel_el.next('.x_content').find('.collapse').attr('id');
          $("#" + coll_el).find('.card-block').html(data['abstract']);
          panel_el.find('img.red').attr('class', 'green');
          el.closest('li').html('<i class="fa fa-refresh" aria-hidden="true"></i>')
        }
      }
    });
  });
  // $('.collapse-link').on('click', function() {
  //   var $BOX_PANEL = $(this).closest('.x_panel'),
  //     $ICON = $(this).find('i'),
  //     $BOX_CONTENT = $BOX_PANEL.find('.x_content');
  //
  //   // fix for some div with hardcoded fix class
  //   if ($BOX_PANEL.attr('style')) {
  //     $BOX_CONTENT.slideToggle(200, function() {
  //       $BOX_PANEL.removeAttr('style');
  //     });
  //   } else {
  //     $BOX_CONTENT.slideToggle(200);
  //     $BOX_PANEL.css('height', 'auto');
  //   }
  //
  //   $ICON.toggleClass('fa-chevron-up fa-chevron-down');
  // });

});
// /Panel toolbox
