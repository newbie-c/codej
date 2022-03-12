$(function() {
  checkMC(800);
  formatFooter(luxon.DateTime.now());
  $('.close-top-flashed').on('click', closeTopFlashed);
  $('.last-seen').each(function() {
    let text = $.trim($(this).text());
    $(this).text(luxon.DateTime.fromISO(text)
                               .setLocale('ru').toRelative());
  });
});
