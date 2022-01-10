$(function() {
  checkMC(800);
  let dtime = luxon.DateTime.now();
  if ($('.today-field').length) renderTF('.today-field', dtime);
  formatFooter(dtime);
  $('.close-top-flashed').on('click', closeTopFlashed);
  $('.reload-button').on('click', ReloadCaptcha);
});
