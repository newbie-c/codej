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
  pingU();
  $('#move-screen-up').on('click', function() {
    $(this).blur();
    scrollPanel($('#navigation'));
  });
  $('#tape-in').on('click', tapeIn);
  $('#tape-out').on('click', tapeOut);
  $('#like-button').on('click', likeArt);
  $('#dislike-button').on('click', likeArt);
  $('#censor-this').on('click', function() {
    $(this).blur();
    $.ajax({
      method: 'POST',
      url: $(this).data().url,
      data: {
        suffix: $('#entity-header-block').data().suffix
      },
      success: function(data) {
        if (!data.empty) window.location.reload();
      },
      error: function(data) {},
      dataType: 'json'
    });
  });
});
