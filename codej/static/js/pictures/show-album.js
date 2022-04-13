$(function() {
  checkMC(1152);
  hideHidden();
  let now = luxon.DateTime.now();
  renderTF('.today-field', now);
  formatFooter(now);
  $('#main-container').on('click', '.close-top-flashed', closeTopFlashed);
  $('.date-field').each(function() {formatDateTime($(this));});
  $('.go-home').on('click', function() {
    $(this).blur();
    window.location.assign($(this).data().dest);
  });
  $('.show-statistic').on('click', function() {
    $(this).blur();
  });
  $('.album-reload').on('click', function() {
    $(this).blur();
    window.location.reload();
  });
  $('.upload-new').on('click', function() {
    $(this).blur();
  });
  let $data_panel = $('#data-panel');
  if ($data_panel.length) {
    let timer = setInterval(function(elem) {
      $.ajax({
        method: 'POST',
        url: elem.data().url,
        data: {
          cache: elem.data().cache
        },
        success: function(data) {
          if (!data.empty) {
            clearInterval(timer);
            window.location.replace(elem.data().redirect);
          }
        },
        error: function(data) {
          clearInterval(timer);
          let html = '<div class="top-flashed-block">' +
                     '  <div class="flashed-message">' +
                     '    <div class="alert alert-warning">' +
                     '      <button class="close close-top-flashed"' +
                     '              type="button">' +
                     '        &times;</button>' +
                     'Произошёл непредвиденный сбой, обновите страницу.' +
                     '    </div>' +
                     '  </div>' +
                     '</div>';
        },
        dataType: 'json'
      });
    }, 600, $data_panel);
  }
  let $upblock = $('#upload-form-block');
  if ($upblock.length) {
    $('.upload-new').on('click', function() {
      $(this).blur();
      if (!$upblock.is(':hidden')) {
        $upblock.slideUp('slow');
      } else {
        $upblock.slideDown('slow');
        scrollPanel($('.albums-options'));
      }
    });
    $('#image').on('change', function() {
      let $file = $(this)[0].files[0];
      if ($file.size <= 5242880 && $file.name.length <= 128) {
        $('#upload-form-block').slideUp('slow');
        $('#progress-block').slideDown('slow');
        $('#submit').trigger('click');
      } else {
        let $cl = $('.close-top-flashed');
        if ($cl.length) $cl.trigger('click');
        let html = '<div class="top-flashed-block">' +
                   '  <div class="flashed-message">' +
                   '    <div class="alert alert-warning">' +
                   '      <button class="close close-top-flashed"' +
                   '              type="button">' +
                   '        &times;</button>' +
                   'Файл не соответствует условиям сервиса.' +
                   '    </div>' +
                   '  </div>' +
                   '</div>';
        $('#left-panel').before(html);
        $(this).val(null);
        scrollPanel($('#navigation'));
        $upblock.slideUp('slow');
      }
    });
  }
});
