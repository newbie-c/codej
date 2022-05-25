function sendEdited(url, art, num, val, code) {
  let html = '<div id="p-block" class="text-center hidden">' +
             '  <img alt="progress show"' +
             '       src="/static/images/upload.gif">' +
             '</div>';
  let block = $('#paragraph-editor');
  block.append(html);
  block.find('.form-group').slideUp('slow');
  $('#p-block').hide().removeClass('hidden').slideDown('slow');
  $.ajax({
    method: 'POST',
    url: url,
    data: {
      art: art,
      num: num,
      text: val,
      code: code
    },
    success: function(data) {
      if (!data.empty) {
        if (data.html) {
          window.location.reload();
        } else {
          $('#p-block').slideUp('slow', function() {
            $('#p-block').remove();
          });
          $('#paragraph-editor').find('.form-group').slideDown('slow');
        }
      }
    },
    error: function(data) {},
    dataType: 'json'
  });
}
