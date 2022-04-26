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
});
