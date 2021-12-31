$(function() {
  checkMC(800);
  let dtime = luxon.DateTime.now();
  if ($('.today-field').length) renderTF('.today-field', dtime);
  formatFooter(dtime);
});
