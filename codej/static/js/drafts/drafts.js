$(function() {
  checkMC(800);
  hideHidden();
  $('.content-block').each(checkNext);
  let now = luxon.DateTime.now();
  renderTF('.today-field', now);
  formatFooter(now);
  $('.date-field').each(function() { formatDateTime($(this)); });
  $('.slidable .block-header').on('click', showHideBlock);
  $('.close-top-flashed').on('click', closeTopFlashed);
  $('#title').on(
    'keyup blur',
    {min: 3, max: 100, block: '.input-field'}, markInputError);
  $('#title').on('keyup', function(event) {
    if (event.which == 13) $('#title-submit').trigger('click');
  });
  $('#title-submit').on('click', function() {
    $(this).blur();
    $('.form-form').slideUp('slow');
    $('#progress-block').slideDown('slow');
    let $title = $('#title');
    $title.blur();
    if (!$('.input-field').hasClass('has-error')) {
      $.ajax({
        method: 'POST',
        url: $(this).data().url,
        data: {
          title: $.trim($title.val())
        },
        success: function(data) {
          if (!data.empty) window.location.replace(data.url);
        },
        error: function(data) {
          let html = '<div class="alert alert-danger">' +
                     '  Произошёл непредвиденный сбой, ' +
                     '  сообщите администратору сервиса.' +
                     '</div>';
          $('#progress-block').before(html).remove();
        },
        dataType: 'json'
      });
    }
  });
  $('.entity-link').on('click', function(event) {
    event.stopPropagation();
  });
});
