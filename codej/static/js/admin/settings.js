$(function() {
  checkMC(800);
  formatFooter(luxon.DateTime.now());
  $('.close-top-flashed').on('click', closeTopFlashed);
  $('.slidable .block-header').on('click', showHideBlock);
  $('#perm-submit').on('click', function(event) {
    $(this).blur();
    event.preventDefault();
    let $data = new Object();
    $('.permissions-form .perm-checkbox').each(function() {
      $data[$(this).attr('id')] = $(this).prop('checked') ? 1 : 0;
    });
    let $token = $('#main-container').data().token;
    $data.csrf_token = $token;
    $.ajax({
      method: 'POST',
      url: $(this).data().url,
      data: $data,
      success: function(data) {
        if (!data.empty) window.location.reload();
      },
      error: function(data) {},
      dataType: 'json'
    });
  });
  $('#robots-submit').on('click', function() {
    $(this).blur();
    $.ajax({
      method: 'POST',
      url: $(this).data().url,
      data: {
        text: $('#robots-editor').val()
      },
      success: function(data) {
        window.location.assign('/robots.txt');
      },
      error: function(data) {},
      dataType: 'json'
    });
  });
});
