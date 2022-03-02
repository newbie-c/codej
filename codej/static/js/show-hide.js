function showHideBlock() {
  let $body = $(this).siblings('.block-body');
  let $parent = $(this).parents('.slidable');
  if ($body.is(':hidden')) {
    $body.slideDown('slow');
    scrollPanel($parent);
  } else {
    $body.slideUp('slow');
  }
}
