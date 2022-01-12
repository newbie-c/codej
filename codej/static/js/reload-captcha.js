function reloadCaptcha(event) {
  $(this).blur();
  $.ajax({
    method: "POST",
    url: $(this).data().url,
    data: {
      csrf_token: $('#csrf_token').attr('value'),
    },
    success: function(data) {
      let style = 'background:url(' + data.picture + ')';
      $('.captcha-field').attr({"style": style});
      $('#suffix').val(data.cache);
      $('#captcha').focus();
    },
    error: function(data) {
      window.location.reload();
    },
    dataType: 'json'
  });
}
