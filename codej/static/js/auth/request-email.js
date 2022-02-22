$(function() {
  checkMC(800);
  let dtime = luxon.DateTime.now();
  renderTF('.today-field', dtime);
  formatFooter(dtime);
  $('.close-top-flashed').on('click', closeTopFlashed);
});
