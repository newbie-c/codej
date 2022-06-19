$(function() {
  checkMC(800);
  let dtime = luxon.DateTime.now();
  if ($('.today-field').length) renderTF('.today-field', dtime);
  formatFooter(dtime);
  $('.close-top-flashed').on('click', closeTopFlashed);
  $('.date-field').each(function() { formatDateTime($(this)); });
  $('.content-block').each(checkNext);
});
