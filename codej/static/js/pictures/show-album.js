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
    let $form = $('#upload-form-block');
    if (!$form.is(':hidden')) $form.slideUp('slow');
    if ($('.clicked-item').length) {
      $('.clicked-item').removeClass('clicked-item');
      showStatistic($(this).data().url, $(this).data().suffix);
    }
  });
  $('.album-reload').on('click', function() {
    $(this).blur();
    window.location.reload();
  });
  $('.album-first-page').on('click', function() {
    $(this).blur();
    window.location.replace($(this).data().dest);
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
        if ($('.clicked-item').length) {
          $('.clicked-item').removeClass('clicked-item');
          showStatistic(
            $('.show-statistic').data().url,
            $('.show-statistic').data().suffix);
        }
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
  $('#main-container').on('click', '#show-rename-form', showRenameForm);
  $('#main-container').on('click', '#show-state-form', showStateForm);
  $('#main-container').on('change', '#select-status', changeStatus);
  $('#main-container').on('click', '#rename-album', renameAlbum);
  $('#main-container')
  .on('keyup blur', '#title-change',
      {min: 3, max: 100, block: '#rename-form'}, markInputError);
  let $header = $('.album-header-panel');
  if ($header.length) {
    $header.on('click', function() {
      if (!$(this).hasClass('clicked-item')) {
        let $form = $('#upload-form-block');
        if (!$form.is(':hidden')) $form.slideUp('slow');
        $('.clicked-item').removeClass('clicked-item');
        $(this).addClass('clicked-item');
        $.ajax({
          method: 'POST',
          url: $(this).data().url,
          data: {
            suffix: $(this).data().suffix
          },
          success: function(data) {
            if (!data.empty) {
              $('#right-panel').empty().append(data.html);
              formatDateTime($('#right-panel .date-field'));
              let $block_width = parseInt($('.album-statistic').width());
              let $pic_width = parseInt($('.picture-body img').attr('width'));
              if ($pic_width >= $block_width) {
                let $pic_height = parseInt($('.picture-body img')
                                           .attr('height'));
                let width = $block_width - 4;
                let height = Math.round($pic_height / ($pic_width / width));
                $('.picture-body img').attr({
                  "width": width, "height": height
                });
              }
            }
          },
          error: function(data) {
            $('.clicked-item').removeClass('clicked-item');
          },
          dataType: 'json'
        });
      }
    });
  }
  $('#right-panel').on('click', '.copy-link', function() {
    $(this).blur();
    let $ff = $('.album-form');
    let $sf = $('.album-form-b');
    if ($ff.is(':hidden')) {
      $ff.slideDown('slow');
      $sf.slideUp('slow');
    } else {
      $ff.slideUp('slow');
    }
  });
  $('#right-panel').on('click', '.copy-md-code', function() {
    $(this).blur();
    let $sf = $('.album-form-b');
    let $ff = $('.album-form');
    if ($sf.is(':hidden')) {
      $sf.slideDown('slow');
      $ff.slideUp('slow');
    } else {
      $sf.slideUp('slow');
    }
  });
  $('#right-panel')
  .on('click', '#copy-button', {cls: '.album-form'}, copyThis);
  $('#right-panel')
  .on('click', '#copy-button-b', {cls: '.album-form-b'}, copyThis);
});
