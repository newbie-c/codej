$(function() {
  checkMC(800);
  hideHidden();
  let now = luxon.DateTime.now();
  formatFooter(now);
  $('.close-top-flashed').on('click', closeTopFlashed);
  $('.date-field').each(function() { formatDateTime($(this)); });
  $('.slidable .block-header').on('click', showHideBlock);
  $('.copy-link').on('click', showCopyForm);
  $('#copy-button').on('click', {cls: '.entity-link-copy-form'}, copyThis);
  $('.entity-text-block iframe').each(adjustFrame);
  $('.entity-text-block').children().each(setMargin);
  $('.entity-text-block img').each(adjustImageW);
  try
  {
    countClicks($('#entity-header-block'));
  } catch (DOMException)
  {
    let html = '<p>' +
               'В вашем браузере заблокированы cookies, контент сайта' +
               ' недоступен в этом режиме, увы, вам придётся либо включить' +
               ' cookies, либо поискать счастья на других ресурсах сети.' +
               ' До скорых встреч...' +
               '</p>';
    $('.entity-text-block').empty().append(html);
  }
  pingU();
  $('#move-screen-up').on('click', function() {
    $(this).blur();
    scrollPanel($('#navigation'));
  });
  $('#tape-in').on('click', tapeIn);
  $('#tape-out').on('click', tapeOut);
  $('#like-button').on('click', likeArt);
  $('#dislike-button').on('click', likeArt);
});
