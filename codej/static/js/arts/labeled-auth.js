$(function() {
  checkMC(800);
  hideHidden();
  $('.content-block').each(checkNext);
  let now = luxon.DateTime.now();
  renderTF('.today-field', now);
  formatFooter(now);
  $('.date-field').each(function() { formatDateTime($(this)); });
  $('.slidable .block-header').on('click', showHideBlock);
  $('.close-top-flashed').on('click', closeTopFlashed);
  $('.entity-link').on('click', function(event) {
    event.stopPropagation();
  });
});
