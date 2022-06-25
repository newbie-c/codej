$(function() {
  checkMC(800);
  hideHidden();
  $('.content-block').each(checkNext);
  let dtime = luxon.DateTime.now();
  if ($('.today-field').length) renderTF('.today-field', dtime);
  formatFooter(dtime);
  $('.date-field').each(function() { formatDateTime($(this)); });
  $('.slidable .block-header').on('click', showHideBlock);
  $('.close-top-flashed').on('click', closeTopFlashed);
  $('.entity-link').on('click', function(event) {
    event.stopPropagation();
  });
});
