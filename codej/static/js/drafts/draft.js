$(function() {
  checkMC(800);
  hideHidden();
  let now = luxon.DateTime.now();
  formatFooter(now)
  $('.close-top-flashed').on('click', closeTopFlashed);
  $('.date-field').each(function() { formatDateTime($(this)); });
  scrollPanel($('.editor-forms-block'));
  $('#html-text-edit').on('keyup', function(event) {
    if (event.which == 13) {
      let val = $(this).val().trim();
      let url = $(this).data().url;
      let art = $('#entity-header-block').data().id;
      const F = '```'
      if (val.startsWith(F)) {
        if (val.indexOf(F, 1) >= 4) {
          val = F + val.split(F)[1].trim() + '\n\n' + F;
          sendPar(url, art, val, 1);
        }
      } else if (val) {
        sendPar(url, art, val, 0);
      }
    }
  });
});
