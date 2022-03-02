$(function() {
  checkMC(800);
  formatFooter(luxon.DateTime.now());
  $('.close-top-flashed').on('click', closeTopFlashed);
  $('.date-field').each(function() {formatDateTime($(this));});
  let $ls = $.trim($('.last-seen').text());
  $('.last-seen').text(luxon.DateTime.fromISO($ls)
                                     .setLocale('ru').toRelative());
  $('.slidable .block-header').on('click', showHideBlock);
});
