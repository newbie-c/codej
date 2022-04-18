function showStateForm() {
  $(this).blur();
  let $ren = $('#rename-form');
  let $stch = $('#change-status-form');
  if ($stch.is(':hidden')) {
    $stch.slideDown('slow');
    $ren.slideUp('slow');
  } else {
    $stch.slideUp('slow');
  }
}
