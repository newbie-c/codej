function showUserStat(url, uid) {
  console.log(url, uid);
  if ($('.clicked-item').length) {
    $('.clicked-item').removeClass('clicked-item');
    $.ajax({
      method: 'POST',
      url: url,
      data: {
        uid: uid
      },
      success: function(data) {
        if (!data.empty) {
          $('#right-panel').empty().append(data.html);
          formatDateTime($('#right-panel .date-field'));
        }
      },
      error: function(data) {},
      dataType: 'json'
    });
  }
}
