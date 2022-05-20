$(function() {
  checkMC(800);
  hideHidden();
  let now = luxon.DateTime.now();
  formatFooter(now)
  $('.close-top-flashed').on('click', closeTopFlashed);
  $('.date-field').each(function() { formatDateTime($(this)); });
  scrollPanel($('.editor-forms-block'));
  $('.slidable .block-header').on('click', showHideBlock);
  if ($('.entity-text-block').length) {
    $('.entity-text-block iframe').each(adjustFrame);
    $('.entity-text-block').children().each(setMargin);
    $('.entity-text-block img').each(adjustImage);
    let ch = $('.entity-text-block').children();
    let len = $('.entity-text-block').data().len;
    let m = 0;
    for (let i = 0; i < ch.length; i++) {
      n = ch[i].nodeName;
      if (n === 'UL' || n === 'OL' || n === 'BLOCKQUOTE') {
        let lch = $(ch[i]).children();
        let l = lch.length;
        let j = 0;
        while (j < lch.length) {
          $(lch[j]).attr('data-num', m);
          j++;
          m++;
        }
      } else {
        $(ch[i]).attr('data-num', m);
        m++;
      }
    }
  }
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
