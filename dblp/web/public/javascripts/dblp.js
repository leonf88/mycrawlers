function update_abstract(t, hook) {
  console.log(hook)
  $.ajax("http://localhost:5000/update_abstract", {
    data: {
      "hook": hook
    },
    crossDomain: true,
    dataType: 'jsonp',
    type: "GET",
    success: function(data) {
      var panel_el = $(t).parentsUntil(".panel");
      var coll_el = panel_el.next('.collapse').attr('id');
      coll_el.next('.card-block').html(data['html']);
      panel_el.next('img').attr('class', 'green');
    }
  });
};
