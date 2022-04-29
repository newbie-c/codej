$(function() {
  checkMC(800);
  hideHidden();
  let now = luxon.DateTime.now();
  formatFooter(now);
  $('.close-top-flashed').on('click', closeTopFlashed);
  $('.date-field').each(function() {formatDateTime($(this));});
  let $cblock = $('.content-block');
  if ($cblock.length) $cblock.each(checkNext);
  $('.picture-itself img').each(adjustPicture);
  $('#main-container').on('click', '.slidable .block-header', showHideBlock);
  $('#main-container').on('click', '.details-button', function(event) {
    event.stopPropagation();
    $(this).blur();
    let $info = $(this).parents('.picture-block').siblings('.picture-info');
    let $icon = $(this).find('.glyphicon');
    if ($info.is(':hidden')) {
      $info.slideDown('slow');
      $(this).attr({"title": "скрыть детали"});
      $icon.removeClass('glyphicon-chevron-down')
           .addClass('glyphicon-chevron-up');
      scrollPanel($(this).parents('.content-block'));
    } else {
      $info.slideUp('slow');
      $('.remove-button').each(function() {$(this).fadeOut('slow');});
      $(this).attr({"title": "показать детали"});
      $icon.removeClass('glyphicon-chevron-up')
           .addClass('glyphicon-chevron-down');
    }
  });
  $('#main-container').on('click', '.trash-button', function() {
    $(this).blur();
    showHideButton($(this), '.remove-button');
  });
  $('#main-container').on('click', '.remove-button', removeThis);
  let $find = $('#suffix-input');
  if ($find.length) $find.on('keyup', function(event) {
    let list = [0, 8, 9, 13, 17, 18, 20, 27, 32, 33, 34, 35, 36, 37, 38, 39,
                40, 45, 46, 91, 93, 144];
    let $val = $(this).val();
    if (event.which == 8) $('.found-aliases').remove();
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
            $('.found-aliases').remove();
            $('.find-block').after(data.html);
            $('.found-aliases .date-field').each(function() {
              formatDateTime($(this)) });
            $('.found-aliases img').each(adjustPicture);
          }
        },
        error: function(data) {},
        dataType: 'json'
      });
    }
  });
});
