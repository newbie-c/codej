$(function() {
  checkMC(1152);
  hideHidden();
  let now = luxon.DateTime.now();
  renderTF('.today-field', now);
  formatFooter(now);
  $('.close-top-flashed').on('click', closeTopFlashed);
  $('.date-field').each(function() {formatDateTime($(this));});
  let $cform = $('#create-form-block');
  let $findblock = $('#find-pic-block');
  if ($cform.length) {
    $('.album-search').on('click', function() {
      $(this).blur();
      if ($findblock.is(':hidden')) {
        if (!$cform.is(':hidden')) $cform.slideUp('slow');
        $findblock.slideDown('slow', function() {
          scrollPanel($('.albums-options'));
        });
        showUserStat($('.user-home').data().url, $('.user-home').data().uid);
      } else {
        $findblock.slideUp('slow');
      }
    });
    $('.create-new-button').on('click', function() {
      $(this).blur();
      if ($cform.is(':hidden')) {
        showUserStat($('.user-home').data().url, $('.user-home').data().uid);
        if (!$findblock.is(':hidden')) $findblock.slideUp('slow');
        $cform.slideDown('slow', function() {
          if (!$findblock.is(':hidden')) $findblock.slideUp('slow');
          $('#title').focus();
        });
        scrollPanel($('.albums-options'));
      } else {
        $cform.slideUp('slow');
      }
    });
    let $pub = $('#pub-f');
    $pub.on('change', function() {
      if ($(this).is(':checked')) {
        uncheckBox('#priv-f');
        uncheckBox('#ffo-f');
      } else {
        checkBox('#priv-f');
      }
    });
    let $priv = $('#priv-f');
    $priv.on('change', function() {
      if ($(this).is(':checked')) {
        uncheckBox('#pub-f');
        uncheckBox('#ffo-f');
      } else {
        checkBox('#pub-f');
      }
    });
    let $ffo = $('#ffo-f');
    $ffo.on('change', function() {
      if ($(this).is(':checked')) {
        uncheckBox('#pub-f');
        uncheckBox('#priv-f');
      } else {
        checkBox('#pub-f');
      }
    });
    $('#create-new').on('click', function() {
      $(this).blur();
      if (!$('#title-group').hasClass('has-error')) {
        $cform.slideUp('slow', function() {
          $('#progress-block').slideDown('slow');
        });
        $.ajax({
          method: 'POST',
          url: $(this).data().url,
          data: {
            title: $('#title').val(),
            state: $('#create-form-block :checked').val()
          },
          success: function(data) {
            if (!data.empty) {
              if (data.redirect) window.location.replace(data.redirect);
            }
          },
          error: function(data) {},
          dataType: 'json'
        });
      }
    });
    $('#title')
    .on('keyup blur',
        {min: 3, max: 100, block: '.form-group'}, markInputError);
  }

  let $show_album = $('.show-album');
  if ($show_album.length) $show_album.on('click', function() {
    $(this).blur();
    window.location.assign($(this).data().dest);
  });
  $('.user-home').on('click', function() {
    $(this).blur();
    let $createform = $('#create-form-block');
    let $findform = $('#find-pic-block');
    if (!$createform.is(':hidden')) $createform.slideUp('slow');
    if (!$findform.is(':hidden')) $findform.slideUp('slow');
    showUserStat($(this).data().url, $(this).data().uid);
  });
  $('.album-reload').on('click', function() {
    $(this).blur();
    window.location.reload();
  });
  let $header = $('.album-header-panel');
  if ($header.length) {
    $header.on('click', function() {
      if (!$(this).hasClass('clicked-item')) {
        let $createform = $('#create-form-block');
        let $findform = $('#find-pic-block');
        if (!$createform.is(':hidden')) $createform.slideUp('slow');
        if (!$findform.is(':hidden')) $findform.slideUp('slow');
        $('.clicked-item').removeClass('clicked-item');
        $(this).addClass('clicked-item');
        showStatistic($(this).data().url, $(this).data().suffix);
      }
    });
  }
  let $first = $('.album-first-page');
  if ($first.length) $first.on('click', function() {
    $(this).blur();
    window.location.replace($(this).data().url);
  });
  $('#main-container').on('click', '#show-rename-form', showRenameForm);
  $('#main-container').on('click', '#show-state-form', showStateForm);
  $('#main-container').on('change', '#select-status', changeStatus);
  $('#main-container').on('click', '#rename-album', renameAlbum);
  $('#main-container')
  .on('keyup blur', '#title-change',
      {min: 3, max: 100, block: '#rename-form'}, markInputError);
});
