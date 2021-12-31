function checkMC(width) {
  let $wwidth = $(window).width();
  let $mcon = $('#main-container');
  if ($wwidth >= width) {
    $mcon.addClass('main-container');
  } else {
    $mcon.addClass('container-fluid');
  }
  $(window).on('resize', function() {
    let $wwidth = $(window).width();
    let $mcon = $('#main-container');
    if ($wwidth >= width) {
      if ($mcon.hasClass('container-fluid')) {
        $mcon.removeClass('container-fluid').addClass('main-container');
      }
    } else {
      if ($mcon.hasClass('main-container')) {
        $mcon.removeClass('main-container').addClass('container-fluid');
      }
    }
  });
}
