function showStatistic(url, suffix) {
  $.ajax({
    method: 'POST',
    url: url,
    data: {
      suffix: suffix
    },
    success: function(data) {
      if (!data.empty) {
        $('#right-panel').empty().append(data.html);
        formatDateTime($('#right-panel .date-field'));
      }
    },
    error: function(data) {
      $('.clicked-item').removeClass('clicked-item');
    },
    dataType: 'json'
  });
}
