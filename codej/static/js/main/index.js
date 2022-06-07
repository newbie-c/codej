$(function() {
  checkMC(800);
  let dtime = luxon.DateTime.now();
  if ($('.today-field').length) renderTF('.today-field', dtime);
  formatFooter(dtime);
  $('.close-top-flashed').on('click', closeTopFlashed);
  $('.date-field').each(function() { formatDateTime($(this)); });
  $('.entity-text-block iframe').each(adjustFrame);
  $('.entity-text-block').children().each(setMargin);
  $('.entity-text-block img').each(adjustImageW);
});
