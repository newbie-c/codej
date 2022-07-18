$(function() {
  checkMC(800);
  hideHidden();
  formatFooter(luxon.DateTime.now());
  $('.content-block').each(checkNext);
  let $find = $('#labelname-input');
  if ($find.length) $find.on('keyup', function(event) {
    $('.found-labels-block').remove();
    let list = [0, 8, 9, 13, 17, 18, 20, 27, 32, 33, 34, 35, 36, 37, 38, 39,
                40, 45, 46, 91, 93, 144];
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
            $('.labels-block').before(data.html);
            $('.content-block').each(checkNext);
          }
        },
        error: function(data) {},
        dataType: 'json'
      });
    }
  });
});
