$(function() {
  checkMC(1152);
  formatFooter(luxon.DateTime.now());
  $('.close-top-flashed').on('click', closeTopFlashed);
  $('.date-field').each(function() {formatDateTime($(this));});
});
