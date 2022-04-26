$(function() {
  checkMC(800);
  hideHidden();
  let now = luxon.DateTime.now();
  renderTF('.today-field', now);
  formatFooter(now);
  $('.close-top-flashed').on('click', closeTopFlashed);
  if ($('.create-block').length) slideError('.create-block .block-body');
  $('.last-seen').each(renderLastSeen);
  let $cblock = $('.content-block');
  if ($cblock.length) $cblock.each(checkNext);
  $('#main-container').on('click', '.slidable .block-header', showHideBlock);
  let $submit = $('#submit');
  if ($submit.length) $submit.on('click', function() { $(this).blur(); });
  let $find = $('#username-input');
  if ($find.length) {
    $find.on('keyup', function(event) {
      let list = [0, 8, 9, 13, 17, 18, 20, 27, 32, 33, 34, 35, 36, 37, 38, 39,
                  40, 45, 46, 91, 93, 144];
      $('.found-block').remove();
      let $val = $(this).val();
      if ($.inArray(event.which, list) == -1 ||
          ((event.which == 8 || event.which == 46) && $val != '')) {
        $.ajax({
          method: 'POST',
          url: $(this).data().url,
          data: {
            value: $val
          },
          success: function(data) {
            if (!data.empty) {
              $('.found-block').remove();
              $('#society-block').before(data.html);
              $('.found-block .last-seen').each(renderLastSeen);
            }
          },
          error: function(data) {},
          dataType: 'json'
        });
      }
    });
  }
});
