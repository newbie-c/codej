function tapeIn() {
  $(this).blur();
  console.log($('#entity-header-block').data().suffix);
  $.ajax({
    method: 'POST',
    url: $(this).data().url,
    data: {
      suffix: $('#entity-header-block').data().suffix
    },
    success: function(data) {
      if (!data.empty) window.location.reload();
    },
    error: function(data) {},
    dataType: 'json'
  });
}
