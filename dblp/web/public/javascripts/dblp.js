(function($) {
  function update_abstract(hook) {
    $.post("/update_abstract", {
        "hook": hook
      },
      function(data) {
        alter(hook)
      });
  }
})(jQuery);
