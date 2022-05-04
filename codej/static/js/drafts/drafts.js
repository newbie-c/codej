$(function() {
  checkMC(800);
  hideHidden();
  let now = luxon.DateTime.now();
  renderTF('.today-field', now);
  formatFooter(now);
  $('.close-top-flashed').on('click', closeTopFlashed);
  $('#title').on(
    'keyup blur',
    {min: 3, max: 100, block: '.input-field'}, markInputError);
  $('#title').on('keyup', function(event) {
    if (event.which == 13) $('#title-submit').trigger('click');
  });
  $('#title-submit').on('click', function() {
    $(this).blur();
  });
});
