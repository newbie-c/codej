$(function() {
  checkMC(800);
  let now = luxon.DateTime.now();
  renderTF('.today-field', now);
  formatFooter(now);
  $('.close-top-flashed').on('click', closeTopFlashed);
  if ($('.create-block').length) slideError('.create-block .block-body');
  $('.last-seen').each(function() {
    let text = $.trim($(this).text());
    $(this).text(luxon.DateTime.fromISO(text)
                               .setLocale('ru').toRelative());
  });
  let $cblock = $('.content-block');
  if ($cblock.length) $cblock.each(checkNext);
  $('#main-container').on('click', '.slidable .block-header', showHideBlock);
  let $submit = $('#submit');
  if ($submit.length) $submit.on('click', function() { $(this).blur(); });
});
