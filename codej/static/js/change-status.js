function changeStatus() {
  $.ajax({
    method: 'POST',
    url: $(this).data().url,
    data: {
      album: $(this).data().aid,
      state: $(this).val()
    },
    success: function(data) {
      if (!data.empty) {
        $('#right-panel').empty().append(data.html);
        $('#right-panel .date-field').each(function() {
          formatDateTime($(this));
        });
      }
    },
    error: function(data) {
      $('#change-status-form').slideUp('slow');
    },
    dataType: 'json'
  });
}
