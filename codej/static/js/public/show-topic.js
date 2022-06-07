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
               ' недоступен в этом режиме, увы.' +
               '</p>';
    $('.entity-text-block').empty().append(html);
  }
  pingU();
});