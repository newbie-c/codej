$(function() {
  checkMC(800);
  let dtime = luxon.DateTime.now();
  formatFooter(dtime);
  $('.close-top-flashed').on('click', closeTopFlashed);
});
