function sendPar(url, art, val, code) {
  $('#progress-block').slideDown('slow');
  $('#new-paragraph-editor').slideUp('slow');
  $.ajax({
    method: 'POST',
    url: url,
    data: {
      art: art,
      text: val,
      code: code
    },
    success: function(data) {
      if (!data.empty) {
        if (data.html) {
          window.location.reload();
        } else {
          $('#html-text-edit').val('');
          $('#progress-block').slideUp('slow');
          $('#new-paragraph-editor').slideDown('slow');
        }
      }
    },
    error: function(data) {},
    dataType: 'json'
  });
}
