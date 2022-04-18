function showRenameForm() {
  $(this).blur();
  let $ren = $('#rename-form');
  let $stch = $('#change-status-form');
  if ($ren.is(':hidden')) {
    $ren.slideDown('slow');
    $stch.slideUp('slow');
  } else {
    $ren.slideUp('slow');
  }
}
