$(function() {
  checkMC(800);
  hideHidden();
  let now = luxon.DateTime.now();
  formatFooter(now)
  $('.close-top-flashed').on('click', closeTopFlashed);
  $('.date-field').each(function() { formatDateTime($(this)); });
});
