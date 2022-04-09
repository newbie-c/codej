$(function() {
  checkMC(1152);
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
      } else {
        $findblock.slideUp('slow');
      }
    });
    $('.create-new-button').on('click', function() {
      $(this).blur();
      if ($cform.is(':hidden')) {
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
  });
  $('.album-reload').on('click', function() {
    $(this).blur();
    window.location.reload();
  });

});
