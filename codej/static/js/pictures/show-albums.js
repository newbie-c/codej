$(function() {
  checkMC(1024);
  let now = luxon.DateTime.now();
  formatFooter(now);
  $('.close-top-flashed').on('click', closeTopFlashed);
});
