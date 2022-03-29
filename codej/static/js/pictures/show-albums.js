$(function() {
  checkMC(1152);
  let now = luxon.DateTime.now();
  renderTF('.today-field', now);
  formatFooter(now);
  $('.close-top-flashed').on('click', closeTopFlashed);

  let $cform = $('.create-form-block');
  if ($cform.length) {
    $('.album-search').on('click', function() {
      $(this).blur();
      if (!$cform.is(':hidden')) $cform.slideUp('slow');
    });
    $('.create-new-button').on('click', function() {
      $(this).blur();
      if ($cform.is(':hidden')) {
        $cform.slideDown('slow', function() {
          scrollPanel($('.albums-options'));
        });
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
      console.log($('.create-form-block :checked').val());
    });
  }

  $('.user-home').on('click', function() {
    $(this).blur();
  });
  $('.album-reload').on('click', function() {
    $(this).blur();
    window.location.reload();
  });

});
