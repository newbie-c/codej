function checkSC() {
  $(this).blur();
  $.ajax({
    method: 'POST',
    url: $(this).data().url,
    data: {
      id: $('#entity-header-block').data().id
    },
    success: function(data) {
      if (!data.empty) window.location.reload();
    },
    error: function(data) {},
    dataType: 'json'
  });
}
